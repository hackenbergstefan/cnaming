ruleset = {
    'variable_declarations': {
        # Basic stdint types
        'uint8_t starts with b': {'type': r'uint8_t|byte', 'rule': r'b([A-Z][a-z0-9]*)+'},
        'uint16_t starts with w': {'type': r'uint16_t', 'rule': r'w([A-Z][a-z0-9]*)+'},
        'uint32_t starts with dw': {'type': r'uint32_t', 'rule': r'dw([A-Z][a-z0-9]*)+'},
        'uint64_t starts with qw': {'type': r'uint64_t', 'rule': r'qw([A-Z][a-z0-9]*)+'},
        # Enums
        'enum starts with e': {'type': r'e.+', 'rule': r'e([A-Z][a-z0-9]*)+'},
        # Struct type
        'struct type starts with s': {'type': r's.+_d', 'rule': r's([A-Z][a-z0-9]*)+'},
        # Pointer handling
        'pointer starts with p': {'type': r'.+ \*|p.+', 'rule': r'p(?:rg)?(.+)', 'forward': True},
        'pointer to pointer starts with pp': {'type': r'p.+ \*|.+ \*\*', 'rule': r'pp(?:rg)?(.+)', 'forward': True},
        # Globals
        'global starts with g_': {'type': r'global .+', 'rule': r'g_(.+)', 'forward': True},
        # Arrays
        'array starts with rg': {'type': r'\w+ \[\d*\]', 'rule': r'rg(.+)', 'forward': True},
    },

    'typedef_declarations': {
        # Enum typedef
        'enum type is e..._t': {'rule': r'e([A-Z][a-z0-9]*)+_t', 'selector': lambda node: node.kind == 'enum'},
        # Struct typedef
        'struct type is s..._d': {'rule': r's([A-Z][a-z0-9]*)+_d', 'selector': lambda node: node.kind == 'struct'},
    }
}
