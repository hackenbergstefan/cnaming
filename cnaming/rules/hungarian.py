from . import Ruleset, Rule

ruleset = Ruleset(
    name='hungarian',
    variable_declarations=[
        # Basic stdint types
        Rule('uint8_t starts with b', type=r'uint8_t|byte', rule=r'b([A-Z][a-z0-9]*)+'),
        Rule('uint16_t starts with w', type=r'uint16_t', rule=r'w([A-Z][a-z0-9]*)+'),
        Rule('uint32_t starts with dw', type=r'uint32_t', rule=r'dw([A-Z][a-z0-9]*)+'),
        Rule('uint64_t starts with qw', type=r'uint64_t', rule=r'qw([A-Z][a-z0-9]*)+'),
        # Enums
        Rule('enum starts with e', type=r'e.+', rule=r'e([A-Z][a-z0-9]*)+'),
        # Struct type
        Rule('struct type starts with s', type=r's.+_d', rule=r's([A-Z][a-z0-9]*)+'),
        # Pointer handling
        Rule('pointer starts with p', type=r'(\S+) \*|p(\S+)', rule=r'p(?:rg)?(.+)', forward=True),
        Rule('pointer to pointer starts with pp', type=r'p(\S+) \*|(\S+) \*\*', rule=r'pp(?:rg)?(.+)', forward=True),
        # Globals
        Rule('global starts with g_', type=r'global (.+)', rule=r'g_(.+)', forward=True),
        # Statics
        Rule('statics starts with m_', type=r'static (.+)', rule=r'm_(.+)', forward=True),
        # Arrays
        Rule('array starts with rg', type=r'(\w+) \[\d*\]', rule=r'rg(.+)', forward=True),
        # Constants
        Rule('Constants are free', type=r'const (.+)', rule=r'(.+)', forward=True),
        # Constants
        Rule('non struct type is unrestricted', type=r'(?!s)\S+_d', rule=r'.+'),
        # void
        Rule('void type starts capital (as pointer)', type=r'void', rule=r'[A-Z].*'),
    ],
    typedef_declarations=[
        # Enum typedef
        Rule('enum type is e..._t', rule=r'e([A-Z][a-z0-9]*)+_t', selector=lambda node: node.kind == 'enum'),
        # Struct typedef
        Rule('struct type is s..._d', rule=r's([A-Z][a-z0-9]*)+_d', selector=lambda node: node.kind == 'struct'),
    ]
)
