import re

import clang
import clang.cindex

from .. import Declaration, NamingIssue, ParseError, Typedef

rulesets = {}


class Ruleset:
    def __init__(self, name, variable_declarations=None, typedef_declarations=None, function_declarations=None):
        self.name = name
        self.variable_declarations = variable_declarations
        self.typedef_declarations = typedef_declarations

        # Register ruleset
        rulesets[self.name] = self

    def check(self, node):
        if node.kind is clang.cindex.CursorKind.TYPEDEF_DECL:
            return self.check_typedef_declarations(Typedef(node), node.displayname)
        elif node.kind is clang.cindex.CursorKind.VAR_DECL or \
            node.kind is clang.cindex.CursorKind.FIELD_DECL or \
            node.kind is clang.cindex.CursorKind.PARM_DECL:
            refed_type = list(node.get_children())[0]
            if refed_type.kind is not clang.cindex.CursorKind.TYPE_REF:
                raise ParseError('Wrong kind. Is: {} Excpected: {}'.format(refed_type.kind, clang.cindex.CursorKind.VAR_DECL))
            declaration = Declaration(node, refed_type)
            return self.check_variable_declaration(declaration, declaration.typename, declaration.declname)

    def check_variable_declaration(self, node, typename, declname):
        for rule in self.variable_declarations:
            if not rule.selector(node):
                continue
            if rule.type.fullmatch(typename):
                match = rule.rule.fullmatch(declname)
                if not match:
                    return NamingIssue(node, rule)
                if rule.forward:
                    return self.check_variable_declaration(node, node.node_type.displayname, match.group(1))

    def check_typedef_declarations(self, node, typename):
        for rule in self.typedef_declarations:
            if not rule.selector(node):
                continue
            if not rule.rule.fullmatch(typename):
                return NamingIssue(node, rule)


class Rule:
    def __init__(self, description, rule, **kwargs):
        self.description = description
        self.rule = re.compile(rule)
        self.selector = kwargs.get('selector', lambda x: x)
        self.type = re.compile(kwargs.get('type')) if 'type' in kwargs else None
        self.forward = kwargs.get('forward', False)

    def __repr__(self):
        return self.description


def load_builtin_rules():
    import importlib
    import pkgutil
    for pkg in pkgutil.walk_packages(__path__):
        importlib.import_module(__name__ + '.' + pkg.name)
