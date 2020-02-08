import re

import clang.cindex

from . import NamingCheck, ParseError, NamingIssue


rule_identifier = r'([A-Z][a-z0-9]*)+'

rules_variables = [
    (re.compile(r'uint8_t'), re.compile(r'b' + rule_identifier)),
    (re.compile(r'uint16_t'), re.compile(r'w' + rule_identifier)),
    (re.compile(r'uint32_t'), re.compile(r'dw' + rule_identifier)),
    (re.compile(r'uint64_t'), re.compile(r'qw' + rule_identifier)),
    (re.compile(r's\w+_d'), re.compile(r's' + rule_identifier)),
]

rule_typedef = re.compile(r's' + rule_identifier + '_d')


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

    @check_kind(lambda node: node.kind is clang.cindex.CursorKind.TYPEDEF_DECL)
    def check_kind_vardecl(self, node):
        if not rule_typedef.match(node.displayname):
            return NamingIssue(node, '"{}" does not match "{}"'.format(
                node.displayname,
                rule_typedef.pattern,
            ))

    @check_kind(
        lambda node:
        node.kind is clang.cindex.CursorKind.VAR_DECL or
        node.kind is clang.cindex.CursorKind.PARM_DECL
    )
    def check_kind_vardecl(self, node):
        refed_type = list(node.get_children())[0]
        if refed_type.kind is not clang.cindex.CursorKind.TYPE_REF:
            raise ParseError('Wrong kind. Is: {} Excpected: {}'.format(refed_type.kind, clang.cindex.CursorKind.VAR_DECL))

        return self.check_variable_name(node, refed_type.displayname, node.displayname)

    def check_variable_name(self, node, typename, varname):
        # Check for global modifier
        if node.linkage is clang.cindex.LinkageKind.EXTERNAL:
            if not varname.startswith('g_'):
                return NamingIssue(node, 'Global "{}" does not start with "g_"'.format(varname))
            else:
                varname = varname[2:]
        # Check for pointer modifier
        if node.type.kind is clang.cindex.TypeKind.POINTER:
            ptypecount = node.type.spelling.count('*')
            pnamecount = sum(node.displayname[i:].startswith('p') for i in range(len(node.displayname)))
            if ptypecount != pnamecount:
                return NamingIssue(node, 'Pointername "{}" does not match its type "{}"'.format(varname, node.type.spelling))
            else:
                varname = varname[pnamecount:]
            # Optional "rg" prefix (used when length is given)
            if varname.startswith('rg'):
                varname = varname[2:]
        # Check for array modifier
        elif node.type.kind is clang.cindex.TypeKind.CONSTANTARRAY or node.type.kind is clang.cindex.TypeKind.INCOMPLETEARRAY:
            if not varname.startswith('rg'):
                return NamingIssue(node, 'Array "{}" does not start with "rg"'.format(varname))
            else:
                varname = varname[2:]

        # Check for variable name
        for re_type, re_name in rules_variables:
            if re_type.match(typename) and not re_name.match(varname):
                return NamingIssue(node, '"{} {}" does not match "{} {}"'.format(
                    typename,
                    varname,
                    re_type.pattern,
                    re_name.pattern,
                ))
