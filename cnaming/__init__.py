import os

import clang
import clang.cindex


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


class NamingCheck:
    def __init__(self, ruleset):
        self.index = clang.cindex.Index.create()
        self.ruleset = ruleset

    def check(self, file):
        self.file = file
        tu = self.index.parse(file)
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


class NamingIssue:
    def __init__(self, node, rule):
        self.node = node
        self.rule = rule

    def __repr__(self):
        return '<NamingIssue @{}:{}: "{}">'.format(self.node.location.line, self.node.location.column, str(self.rule))
