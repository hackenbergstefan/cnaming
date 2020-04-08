import os
import re

import clang
import clang.cindex

try:
    clang.cindex.conf.lib
except clang.cindex.LibclangError:
    import sys
    if sys.platform == 'linux':
        import glob
        libs = list(sorted(glob.glob('/usr/lib/x86_64-linux-gnu/libclang-[6789].[0-9].so*')))
        if len(libs) > 0:
            clang.cindex.conf.set_library_file(libs[-1])


def find_ignores(node):
    comment = [
        t.spelling
        for t in node.translation_unit.cursor.get_tokens()
        if all([
            t.kind is clang.cindex.TokenKind.COMMENT,
            t.location.line == node.location.line,
            t.spelling.startswith('//cnaming'),
        ])
    ]
    re_ignore = re.compile(r'-"(.+?)"')
    return sum((re_ignore.findall(c) for c in comment), [])


class TranslationElement:
    def __init__(self, node):
        self.node = node
        self.location = node.location

    def __repr__(self):
        return self.node.displayname


class Declaration(TranslationElement):
    def __init__(self, node, node_type):
        super().__init__(node)
        self.node_type = node_type

        self.flags = set()
        if node.kind is not clang.cindex.CursorKind.FIELD_DECL and \
           node.linkage is clang.cindex.LinkageKind.EXTERNAL:
            self.flags.add('global')
        elif node.storage_class is clang.cindex.StorageClass.STATIC:
            self.flags.add('static')

        self.ignores = find_ignores(node)

    @property
    def typename(self):
        return '{}{}'.format(''.join('{} '.format(f) for f in self.flags), self.node.type.spelling)

    @property
    def declname(self):
        return self.node.displayname

    def __repr__(self):
        return '{} {}'.format(self.node.type.spelling, self.node.displayname)


class Typedef(TranslationElement):
    def __init__(self, node):
        super().__init__(node)
        self.kind = node.underlying_typedef_type.spelling.split(' ')[0]

        self.ignores = find_ignores(node)


class NamingCheck:
    def __init__(self, ruleset):
        self.index = clang.cindex.Index.create()
        self.ruleset = ruleset

    def check(self, file, clang_args=None):
        self.file = file
        tu = self.index.parse(file, args=clang_args)
        errors = [d for d in tu.diagnostics if d.severity in (clang.cindex.Diagnostic.Error, clang.cindex.Diagnostic.Fatal)]
        if len(errors):
            return [str(d) for d in errors]
        return self.walk(tu.cursor)

    def walk(self, node):
        issues = []
        if os.path.abspath(str(node.location.file)) == os.path.abspath(self.file):
            issues.append(self.ruleset.check(node))
        for c in node.get_children():
            issues.extend(self.walk(c))

        # Return unique issues
        issue_hashes = set()
        return [
            i for i in issues
            if i is not None and
            i.node.node.hash not in issue_hashes and
            (issue_hashes.add(i.node.node.hash) or True)
        ]


class ParseError(Exception):
    pass


class Issue:
    def __init__(self, node):
        self.node = node

    def __repr__(self):
        return '<{} @{}:{}: "{}">'.format(self.__class__.__name__, self.node.location.line, self.node.location.column, self.node.spelling)


class NamingIssue(Issue):
    def __init__(self, node, rule):
        self.node = node
        self.rule = rule

    def __repr__(self):
        return '<NamingIssue @{}:{}: "{}">'.format(self.node.location.line, self.node.location.column, str(self.rule))


class NoRuleIssue(Issue):
    pass
