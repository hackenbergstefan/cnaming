import unittest
import tempfile
import os

import cnaming
import cnaming.hungarian


class TestHungarian(unittest.TestCase):
    def check_with_tempfile(self, content):
        with tempfile.TemporaryDirectory() as tempdir:
            with open(os.path.join(tempdir, 'tmp.c'), 'w') as fp:
                 fp.write(content)

            return cnaming.hungarian.HungarianNamingCheck().check(os.path.join(tempdir, 'tmp.c'))

    def check_inside_function(self, declaration):
        return self.check_with_tempfile('''
            #include <stdint.h>
            void main() {{
                {}
            }}
            '''.format(declaration))

    def check_outside_function(self, declaration):
        return self.check_with_tempfile('''
            #include <stdint.h>
            {}
            '''.format(declaration))

    def test_declarations(self):
        issues = self.check_inside_function('''
            uint32_t dwA;
            uint16_t wB;
            sFoobar_d sFoo;
        ''')
        self.assertFalse(issues)

    def test_wrong_declarations(self):
        issues = self.check_inside_function('''
            typedef struct {} sFoobar_d;
            uint32_t wA;
            uint16_t dwB;
            sFoobar_d wFoo;
        ''')
        self.assertEqual(len(issues), 3)
