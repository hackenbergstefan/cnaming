import re

import clang
import clang.cindex

from .. import Declaration, NamingIssue, NoRuleIssue, ParseError, Typedef

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
            refed_types = [n for n in node.get_children() if n.kind is clang.cindex.CursorKind.TYPE_REF]
            if len(refed_types) == 0 and 'void *' not in node.type.spelling:
                raise ParseError('No CursorKind.TYPE_REF found under {}:{}:{}.'.format(node.location.line, node.location.column, node.spelling))
            declaration = Declaration(node, refed_types[0] if refed_types else node)
            return self.check_variable_declaration(declaration, declaration.typename, declaration.declname)

    def check_variable_declaration(self, node, typename, declname):
        one_matched = False
        for rule in self.variable_declarations:
            if not rule.selector(node):
                continue
            match_type = rule.type.fullmatch(typename)
            if match_type:
                one_matched = True
                match_rule = rule.rule.fullmatch(declname)
                if not match_rule:
                    return NamingIssue(node, rule)
                if rule.forward:
                    return self.check_variable_declaration(
                        node,
                        [g for g in match_type.groups() if g][0],
                        [g for g in match_rule.groups() if g][0],
                    )
        if one_matched is False:
            return NoRuleIssue(node)

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
