import re

CPP_RESERVED_TOKENS = [
    '#include',
    '#pragma',
    '#define',
    'alignas',  # C++11
    'alignof',  # C++11
    'and',
    'and_eq',
    'asm',
    'atomic_cancel',  # TM TS
    'atomic_commit',  # TM TS
    'atomic_noexcept',  # TM TS
    'auto',
    'bitand',
    'bitor',
    'bool',
    'break',
    'case',
    'catch',
    'char',
    'char16_t',  # C++11
    'char32_t',  # C++11
    'class',
    'compl',
    'concept',  # C++20
    'const',
    'constexpr',  # C++11
    'const_cast',
    'continue',
    'co_await',  # coroutines TS
    'co_return',  # coroutines TS
    'co_yield',  # coroutines TS
    'decltype',
    'default',
    'delete',
    'do',
    'double',
    'dynamic_cast',
    'else',
    'enum',
    'explicit',
    'export',
    'extern',
    'false',
    'float',
    'for',
    'friend',
    'goto',
    'if',
    'import',  # modules TS
    'inline',
    'int',
    'long',
    'module',  # modules TS
    'mutable',
    'namespace',
    'new',
    'noexcept',  # C++11
    'not',
    'not_eq',
    'nullptr',  # C++11
    'operator',
    'or',
    'or_eq',
    'private',
    'protected',
    'public',
    'register',
    'reinterpret_cast',
    'requires',  # C++20
    'return',
    'short',
    'signed',
    'sizeof',
    'static',
    'static_assert',  # C++11
    'static_cast',
    'struct',
    'switch',
    'synchronized',  # TM TS
    'template',
    'this',
    'thread_local',  # C++11
    'throw',
    'true',
    'try',
    'typedef',
    'typeid',
    'typename',
    'union',
    'unsigned',
    'using',
    'virtual',
    'void',
    'volatile',
    'wchar_t',
    'while',
    'xor',
    'xor_eq',
    ';',
    '(',
    ')',
    '{',
    '}',
    '[',
    ']',
    '+',
    '-',
    '*',
    '/',
    '^',
    '=',
    '==',
    '!=',
    '<',
    '<=',
    '>',
    '>=',
    '--',
    '++',
    '?',
    ',',

    # std
    'cout',
    'cin',
    'endl'
]

CPP_IGNORED_SEQS = [
    '#define',
    '#pragma',
    'delete'
]

CPP_IMPORT_REGEX = re.compile(r'#include\s+["<]?(?P<name>[^">]*)[">]?')
CPP_NS_REGEX = re.compile(r'(?:inline\s+)?namespace.*')
CPP_USING_NS_REGEX = re.compile(r'using\s+namespace.*')
