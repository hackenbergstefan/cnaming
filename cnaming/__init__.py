import os
import re

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
            issues.append(self.check_node(node))
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

    def check_node(self, node):
        if node.kind is clang.cindex.CursorKind.TYPEDEF_DECL:
            return self.check_node_typedef(Typedef(node), node.displayname)
        elif node.kind is clang.cindex.CursorKind.VAR_DECL or \
            node.kind is clang.cindex.CursorKind.FIELD_DECL or \
            node.kind is clang.cindex.CursorKind.PARM_DECL:
            refed_type = list(node.get_children())[0]
            if refed_type.kind is not clang.cindex.CursorKind.TYPE_REF:
                raise ParseError('Wrong kind. Is: {} Excpected: {}'.format(refed_type.kind, clang.cindex.CursorKind.VAR_DECL))
            declaration = Declaration(node, refed_type)
            return self.check_node_declaration(declaration, declaration.typename, declaration.declname)

    def check_node_declaration(self, node, typename, declname):
        for name, rule in self.ruleset['variable_declarations'].items():
            if 'selector' in rule and not rule['selector'](node):
                continue
            if re.fullmatch(rule['type'], typename):
                match = re.fullmatch(rule['rule'], declname)
                if not match:
                    return NamingIssue(node, name)
                if 'forward' in rule:
                    return self.check_node_declaration(node, node.node_type.displayname, match.group(1))

    def check_node_typedef(self, node, typename):
        for name, rule in self.ruleset['typedef_declarations'].items():
            if 'selector' in rule and not rule['selector'](node):
                continue
            if not re.fullmatch(rule['rule'], typename):
                return NamingIssue(node, name)


class ParseError(Exception):
    pass


class NamingIssue:
    def __init__(self, node, text):
        self.node = node
        self.text = text

    def __repr__(self):
        return '<NamingIssue "{}">'.format(self.text)
