import unittest
import tempfile
import os

import cnaming
import cnaming.rules
import cnaming.rules.hungarian


class TestHungarian(unittest.TestCase):
    def check_with_tempfile(self, content):
        with tempfile.TemporaryDirectory() as tempdir:
            with open(os.path.join(tempdir, 'tmp.c'), 'w') as fp:
                fp.write(content)

            return cnaming.NamingCheck(cnaming.rules.hungarian.ruleset).check(os.path.join(tempdir, 'tmp.c'))

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
            void *pFoo;
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
            void *pbFoo;
        ''')
        self.assertEqual(len(issues), 7)
        self.assertFalse([i for i in issues if isinstance(i, cnaming.NoRuleIssue)])

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
        self.assertFalse([i for i in issues if isinstance(i, cnaming.NoRuleIssue)])

    def test_globals(self):
        issues = self.check_outside_function('''
            const uint8_t *g_pbFoo;
            const uint32_t g_dwFoobar = 0;
            uint8_t g_bFoobar = 0;
        ''')
        self.assertFalse(issues)

    def test_wrong_globals(self):
        issues = self.check_outside_function('''
            const uint8_t *pbFoo;
            const uint32_t dwFoobar = 0;
            uint8_t bFoobar = 0;
        ''')
        self.assertEqual(len(issues), 3)
        self.assertFalse([i for i in issues if isinstance(i, cnaming.NoRuleIssue)])

    def test_function_parameters(self):
        issues = self.check_outside_function('''
            void foobar(uint32_t dwFoo, uint8_t *pbBar, uint8_t *prgbBaz) {}
        ''')
        self.assertFalse(issues)

    def test_wrong_function_parameters(self):
        issues = self.check_outside_function('''
            void foobar(uint32_t pFoo, uint8_t *bBar, uint8_t *prgBaz) {}
        ''')
        self.assertEqual(len(issues), 3)
        self.assertFalse([i for i in issues if isinstance(i, cnaming.NoRuleIssue)])

    def test_array_declarations(self):
        issues = self.check_inside_function('''
            typedef struct {} sFoobar_d;

            uint8_t rgbFoo[8];
            uint32_t rgdwFoo[];
            sFoobar_d rgsFoo[2];
        ''')
        self.assertFalse(issues)

    def test_wrong_array_declarations(self):
        issues = self.check_inside_function('''
            typedef struct {} sFoobar_d;

            uint8_t gFoo[8];
            uint32_t rgwFoo[];
            sFoobar_d rgsfoo[2];
        ''')
        self.assertEqual(len(issues), 3)

    def test_doublepointer(self):
        issues = self.check_inside_function('''
            const uint8_t **ppbFoo;
            uint8_t **ppbFoo;
        ''')
        self.assertFalse(issues)

    def test_wrong_doublepointer(self):
        issues = self.check_inside_function('''
            const uint8_t **c_pbFoo;
            uint8_t **pbFoo;
        ''')
        self.assertEqual(len(issues), 2)
        self.assertFalse([i for i in issues if isinstance(i, cnaming.NoRuleIssue)])

    def test_struct_member(self):
        issues = self.check_outside_function('''
            typedef struct {} sFoo_d;
            typedef struct
            {
                uint32_t dwX;
                uint16_t wX;
                uint8_t bX;
                uint8_t rgbX[8];
                uint8_t *pbX;
                sFoo_d sFoo;
                sFoo_d *psFoo;
            } sBar_d;
        ''')
        self.assertFalse(issues)

    def test_wrong_struct_member(self):
        issues = self.check_outside_function('''
            typedef struct {} sFoo_d;
            typedef struct
            {
                uint32_t A;
                uint16_t B;
                uint8_t C;
                uint8_t D[8];
                uint8_t *bE;
                sFoo_d sfoo;
                sFoo_d *psbar;
            } sBar_d;
        ''')
        self.assertEqual(len(issues), 7)
        self.assertFalse([i for i in issues if isinstance(i, cnaming.NoRuleIssue)])

    def test_enum(self):
        issues = self.check_outside_function('''
            typedef enum
            {
                A,
                B
            } eEnum_t;
        ''')
        self.assertFalse(issues)

    def test_wrong_enum(self):
        issues = self.check_outside_function('''
            typedef enum
            {
                A,
                B
            } myEnum;
        ''')
        self.assertEqual(len(issues), 1)
        self.assertFalse([i for i in issues if isinstance(i, cnaming.NoRuleIssue)])

    def test_infered_type(self):
        issues = self.check_outside_function('''
            typedef uint8_t *hdl_d;
            static const hdl_d *m_pFoo;
        ''')
        self.assertFalse(issues)

    def test_clang_args(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with open(os.path.join(tempdir, 'tmp.c'), 'w') as fp:
                fp.write('''
                #include <foo.h>

                const sFoo_d g_sBar;
                ''')
            os.mkdir(os.path.join(tempdir, 'foo'))
            with open(os.path.join(tempdir, 'foo', 'foo.h'), 'w') as fp:
                fp.write('''
                typedef struct {} sFoo_d;
                ''')

            checker = cnaming.NamingCheck(cnaming.rules.hungarian.ruleset)
            with self.assertRaises(cnaming.ParseError):
                checker.check(os.path.join(tempdir, 'tmp.c'))

            issues = checker.check(
                os.path.join(tempdir, 'tmp.c'),
                clang_args=['-I{}'.format(os.path.join(tempdir, 'foo'))]
            )
            self.assertFalse(issues)

    def test_comments(self):
        issues = self.check_outside_function('''
            const uint32_t *Foobar = 0; //cnaming -"global starts with g_" -"uint32_t starts with dw" -"pointer starts with p"
        ''')
        self.assertFalse(issues)

    def test_diagnostics(self):
        issues = self.check_outside_function('''
            #include <foo.h>
        ''')
        self.assertEqual(len(issues), 1)
        self.assertIn('file not found', issues[0])
