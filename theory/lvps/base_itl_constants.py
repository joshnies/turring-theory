from theory.utils import add_re_begin_end

MASK_TOKEN_REGEX_STR = r'%mask_\d+%'

# List of sequences to copy over during immediate translation for std languages
STD_SEQS_TO_COPY = [
    ',',
    '?',
    '};',
    ');',
    '),',
    ';',
    '(',
    ')',
    '{',
    '}',
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
    'default:',
    'else',
    'else {',
    'do',
    'do {',
    'try',
    'try {',
    'break;',
    'continue;'
]

# List of masked sequences to copy over during immediate translation for std languages to other std languages
STANDARD_MASKED_SEQS_TO_COPY = [
    add_re_begin_end(MASK_TOKEN_REGEX_STR),
    add_re_begin_end(MASK_TOKEN_REGEX_STR + r'[,;]+'),
    add_re_begin_end(MASK_TOKEN_REGEX_STR + r'[)}]+'),
    add_re_begin_end(MASK_TOKEN_REGEX_STR + r'\+{2};?'),
    add_re_begin_end(MASK_TOKEN_REGEX_STR + r'-{2};?')
]

# List of masked sequences to copy over during immediate translation for std languages to Python
STANDARD_TO_PY_MASKED_SEQS_TO_COPY = [
    add_re_begin_end(MASK_TOKEN_REGEX_STR),
    add_re_begin_end(MASK_TOKEN_REGEX_STR + r'[,]+'),
    add_re_begin_end(MASK_TOKEN_REGEX_STR + r'[)}]+')
]
