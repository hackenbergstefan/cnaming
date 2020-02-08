import os

import clang
import clang.cindex


class NamingCheck:
    def __init__(self):
        self.index = clang.cindex.Index.create()

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
            i.node.hash not in issue_hashes and
            (issue_hashes.add(i.node.hash) or True)
        ]

    def check_node(self, node):
        pass


class ParseError(Exception):
    pass


class NamingIssue:
    def __init__(self, node, text):
        self.node = node
        self.text = text

    def __repr__(self):
        return '<NamingIssue "{}">'.format(self.text)
