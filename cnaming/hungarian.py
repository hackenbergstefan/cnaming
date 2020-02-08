import re

import clang.cindex

from . import NamingCheck, ParseError, NamingIssue


identifier_re = r'[A-Z]\w*'

naming_rules = [
    (re.compile('uint8_t'), re.compile(r'b' + identifier_re)),
    (re.compile('uint16_t'), re.compile(r'w' + identifier_re)),
    (re.compile('uint32_t'), re.compile(r'dw' + identifier_re)),
    (re.compile('uint64_t'), re.compile(r'qw' + identifier_re)),
    (re.compile('s\w+_d'), re.compile(r's' + identifier_re)),
]


def check_kind(selector):
    if not hasattr(check_kind, 'selectors'):
        check_kind.selectors = []
    def check_kind_(func):
        check_kind.selectors.append((selector, func))
        return func
    return check_kind_


class HungarianNamingCheck(NamingCheck):
    def check_node(self, node):
        for selector, func in check_kind.selectors:
            if selector(node):
                return func(self, node)

    @check_kind(lambda node: node.kind is clang.cindex.CursorKind.VAR_DECL)
    def check_kind_vardecl(self, node):
        refed_type = list(node.get_children())[0]
        if refed_type.kind is not clang.cindex.CursorKind.TYPE_REF:
            raise ParseError('Wrong kind. Is: {} Excpected: {}'.format(refed_type.kind, clang.cindex.CursorKind.VAR_DECL))

        return self.check_variable_name(node, refed_type.displayname, node.displayname)

    def check_variable_name(self, node, typename, varname):
        for re_type, re_name in naming_rules:
            if re_type.match(typename) and not re_name.match(varname):
                return NamingIssue(node, '"{} {}" does not match "{} {}"'.format(
                    typename,
                    varname,
                    re_type.pattern,
                    re_name.pattern,
                ))
