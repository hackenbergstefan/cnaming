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
            typedef struct {} sFoobar_d;

            uint32_t dwA;
            uint16_t wB;
            sFoobar_d sFoo;
            uint32_t *pdwFoo;
            uint8_t *pbFoo;
            sFoobar_d *psFoo;
        ''')
        self.assertFalse(issues)

    def test_wrong_declarations(self):
        issues = self.check_inside_function('''
            typedef struct {} sFoobar_d;

            uint32_t wA;
            uint16_t dwB;
            sFoobar_d wFoo;
            uint32_t *pFoo;
            uint8_t *Foo;
            sFoobar_d *sFoo;
        ''')
        self.assertEqual(len(issues), 6)

    def test_typedef(self):
        issues = self.check_outside_function('''
            typedef struct {} sFoobar_d;
        ''')
        self.assertFalse(issues)

    def test_wrong_typedef(self):
        issues = self.check_outside_function('''
            typedef struct {} Foobar_d;
            typedef struct {} sFoobar;
        ''')
        self.assertEqual(len(issues), 2)

    def test_globals(self):
        issues = self.check_outside_function('''
        const uint32_t g_dwFoobar = 0;
        uint8_t g_bFoobar = 0;
        ''')
        self.assertFalse(issues)

    def test_wrong_globals(self):
        issues = self.check_outside_function('''
        const uint32_t dwFoobar = 0;
        uint8_t bFoobar = 0;
        ''')
        self.assertEqual(len(issues), 2)
