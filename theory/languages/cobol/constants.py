import re

from ...lvps.base_itl_constants import MASK_TOKEN_REGEX_STR
from ...utils import gen_mask_token

COBOL_RESERVED_TOKENS = [
    '.',
    ',',
    '"',
    "'",
    '+',
    '-',
    '*',
    '/',
    '**',
    '>',
    '<',
    '=',
    '==',
    '>=',
    '<=',
    '<>',
    '*>',
    '>>',
    '88',
    'ACCEPT',
    'ACCESS',
    'ACTIVE-CLASS',
    'ADD',
    'ADDRESS',
    'ADVANCING',
    'AFTER',
    'ALIGNED',
    'ALL',
    'ALLOCATE',
    'ALPHABET',
    'ALPHABETIC',
    'ALPHABETIC-LOWER',
    'ALPHABETIC-UPPER',
    'ALPHANUMERIC',
    'ALPHANUMERIC-EDITED',
    'ALSO',
    'ALTER',
    'ALTERNATE',
    'AND',
    'ANY',
    'ANY-ERROR-STATUS',  # IDMS
    'ANYCASE',
    'APPLY',
    'ARE',
    'AREA',
    'AREAS',
    'ASCENDING',
    'ASSIGN',
    'AT',
    'AUTHOR',
    'B-AND',
    'B-NOT',
    'B-OR',
    'B-XOR',
    'BASED',
    'BASIS',
    'BEFORE',
    'BEGINNING',
    'BINARY',
    'BINARY-CHAR',
    'BINARY-DOUBLE',
    'BINARY-LONG',
    'BINARY-SHORT',
    'BIND',  # IDMS
    'BIT',
    'BLANK',
    'BLOCK',
    'BOOLEAN',
    'BOTTOM',
    'BY',
    'CALC',  # IDMS
    'CALL',
    'CANCEL',
    'CBL',
    'CD',
    'CF',
    'CH',
    'CHARACTER',
    'CHARACTERS',
    'CLASS',
    'CLASS-ID',
    'CLOCK-UNITS',
    'CLOSE',
    'COBOL',
    'CODE',
    'CODE-SET',
    'COL',
    'COLLATING',
    'COLS',
    'COLUMN',
    'COLUMNS',
    'COM-REG',
    'COMMA',
    'COMMON',
    'COMMUNICATION',
    'COMP',
    'COMP-1',
    'COMP-2',
    'COMP-3',
    'COMP-4',
    'COMP-5',
    'COMPUTATIONAL',
    'COMPUTATIONAL-1',
    'COMPUTATIONAL-2',
    'COMPUTATIONAL-3',
    'COMPUTATIONAL-4',
    'COMPUTATIONAL-5',
    'COMPUTE',
    'CONDITION',
    'CONFIGURATION',
    'CONSTANT',
    'CONTAINS',
    'CONTENT',
    'CONTINUE',
    'CONTROL',
    'CONTROLS',
    'CONVERTING',
    'COPY',
    'CORR',
    'CORRESPONDING',
    'COUNT',
    'CRT',
    'CURRENCY',
    'CURSOR',
    'DATA',
    'DATA-POINTER',
    'DATE',
    'DATE-COMPILED',
    'DATE-WRITTEN',
    'DAY',
    'DAY-OF-WEEK',
    'DB',  # IDMS
    'DB-END-OF-SET',  # IDMS
    'DBCS',
    'DE',
    'DEBUG-CONTENTS',
    'DEBUG-ITEM',
    'DEBUG-LINE',
    'DEBUG-NAME',
    'DEBUG-SUB-1',
    'DEBUG-SUB-2',
    'DEBUG-SUB-3',
    'DEBUGGING',
    'DECIMAL-POINT',
    'DECLARATIVES',
    'DEFAULT',
    'DELETE',
    'DELIMITED',
    'DELIMITER',
    'DEPENDING',
    'DESCENDING',
    'DESTINATION',
    'DETAIL',
    'DISABLE',
    'DISPLAY',
    'DISPLAY-1',
    'DIVIDE',
    'DIVISION',
    'DOWN',
    'DUPLICATES',
    'DYNAMIC',
    'EC',
    'EGCS',
    'EGI',
    'EJECT',
    'ELSE',
    'EMI',
    'ENABLE',
    'END',
    'END-ACCEPT',
    'END-ADD',
    'END-CALL',
    'END-COMPUTE',
    'END-DELETE',
    'END-DISPLAY',
    'END-DIVIDE',
    'END-EVALUATE',
    'END-EXEC',
    'END-IF',
    'END-INVOKE',
    ' END-JSON',
    'END-MULTIPLY',
    'END-OF-PAGE',
    'END-PERFORM',
    'END-READ',
    'END-RECEIVE',
    'END-RETURN',
    'END-REWRITE',
    'END-SEARCH',
    'END-START',
    'END-STRING',
    'END-SUBTRACT',
    'END-UNSTRING',
    'END-WRITE',
    'END-XML',
    'ENDING',
    'ENTER',
    'ENTRY',
    'ENVIRONMENT',
    'EO',
    'EOP',
    'EQUAL',
    'ERROR',
    'ESI',
    'EVALUATE',
    'EVERY',
    'EXCEPTION',
    'EXCEPTION-OBJECT',
    'EXEC',
    'EXECUTE',
    'EXIT',
    'EXTEND',
    'EXTERNAL',
    'FACTORY',
    'FALSE',
    'FD',
    'FILE',
    'FILE-CONTROL',
    'FILLER',
    'FINAL',
    'FINISH',  # IDMS
    'FIRST',
    'FLOAT-EXTENDED',
    'FLOAT-LONG',
    'FLOAT-SHORT',
    'FOOTING',
    'FOR',
    'FORMAT',
    'FREE',
    'FROM',
    'FUNCTION',
    'FUNCTION-ID',
    'FUNCTION-POINTER',
    'GENERATE',
    'GET',
    'GIVING',
    'GLOBAL',
    'GO',
    'GOBACK',
    'GREATER',
    'GROUP',
    'GROUP-USAGE',
    'HEADING',
    'HIGH-VALUE',
    'HIGH-VALUES',
    'I-O',
    'I-O-CONTROL',
    'ID',
    'IDENTIFICATION',
    'IDMS-CONTROL',  # IDMS
    'IDMS-STATUS',
    'IF',
    'IN',
    'INDEX',
    'INDEXED',
    'INDICATE',
    'INHERITS',
    'INITIAL',
    'INITIALIZE',
    'INITIATE',
    'INPUT',
    'INPUT-OUTPUT',
    'INSERT',
    'INSPECT',
    'INSTALLATION',
    'INTERFACE',
    'INTERFACE-ID',
    'INTO',
    'INVALID',
    'INVOKE',
    'IS',
    'JNIENVPTR',
    'JSON',
    'JSON-CODE',
    'JUST',
    'JUSTIFIED',
    'KANJI',
    'KEY',
    'LABEL',
    'LAST',
    'LEADING',
    'LEFT',
    'LENGTH',
    'LESS',
    'LIMIT',
    'LIMITS',
    'LINAGE',
    'LINAGE-COUNTER',
    'LINE',
    'LINE-COUNTER',
    'LINES',
    'LINKAGE',
    'LOCAL-STORAGE',
    'LOCALE',
    'LOCK',
    'LOW-VALUE',
    'LOW-VALUES',
    'MEMORY',
    'MERGE',
    'MESSAGE',
    'METHOD',
    'METHOD-ID',
    'MINUS',
    'MODE',
    'MODULES',
    'MORE-LABELS',
    'MOVE',
    'MULTIPLE',
    'MULTIPLY',
    'NATIONAL',
    'NATIONAL-EDITED',
    'NATIVE',
    'NEGATIVE',
    'NESTED',
    'NEXT',
    'NO',
    'NOT',
    'NULL',
    'NULLS',
    'NUMBER',
    'NUMERIC',
    'NUMERIC-EDITED',
    'OBJECT',
    'OBJECT-COMPUTER',
    'OBJECT-REFERENCE',
    'OBTAIN',  # IDMS
    'OCCURS',
    'OF',
    'OFF',
    'OMITTED',
    'ON',
    'OPEN',
    'OPTIONAL',
    'OPTIONS',
    'OR',
    'ORDER',
    'ORGANIZATION',
    'OTHER',
    'OUTPUT',
    'OVERFLOW',
    'OVERRIDE',
    'OWNER',  # IDMS
    'PACKED-DECIMAL',
    'PADDING',
    'PAGE',
    'PAGE-COUNTER',
    'PASSWORD',
    'PERFORM',
    'PF',
    'PH',
    'PIC',
    'PICTURE',
    'PLUS',
    'POINTER',
    'POSITION',
    'POSITIVE',
    'PRESENT',
    'PRINTING',
    'PROCEDURE',
    'PROCEDURE-POINTER',
    'PROCEDURES',
    'PROCEED',
    'PROCESSING',
    'PROGRAM',
    'PROGRAM-ID',
    'PROGRAM-POINTER',
    'PROPERTY',
    'PROTOCOL',  # IDMS
    'PROTOTYPE',
    'PURGE',
    'QUEUE',
    'QUOTE',
    'QUOTES',
    'RAISE',
    'RAISING',
    'RANDOM',
    'RD',
    'READ',
    'READY',
    'RECEIVE',
    'RECORD',
    'RECORDING',
    'RECORDS',
    'RECURSIVE',
    'REDEFINES',
    'REEL',
    'REFERENCE',
    'REFERENCES',
    'RELATIVE',
    'RELEASE',
    'RELOAD',
    'REMAINDER',
    'REMOVAL',
    'RENAMES',
    'REPLACE',
    'REPLACING',
    'REPORT',
    'REPORTING',
    'REPORTS',
    'REPOSITORY',
    'RERUN',
    'RESERVE',
    'RESET',
    'RESUME',
    'RETRY',
    'RETURN',
    # 'RETURN-CODE',  # Utilized as the target variable name
    'RETURNING',
    'REVERSED',
    'REWIND',
    'REWRITE',
    'RF',
    'RH',
    'RIGHT',
    'ROUNDED',
    'RUN',
    'SAME',
    'SCHEMA',  # IDMS
    'SCREEN',
    'SD',
    'SEARCH',
    'SECTION',
    'SECURITY',
    'SEGMENT',
    'SEGMENT-LIMIT',
    'SELECT',
    'SELF',
    'SEND',
    'SENTENCE',
    'SEPARATE',
    'SEQUENCE',
    'SEQUENTIAL',
    'SERVICE',
    'SET',
    'SHARING',
    'SHIFT-IN',
    'SHIFT-OUT',
    'SIGN',
    'SIZE',
    'SKIP1',
    'SKIP2',
    'SKIP3',
    'SORT',
    'SORT-CONTROL',
    'SORT-CORE-SIZE',
    'SORT-FILE-SIZE',
    'SORT-MERGE',
    'SORT-MESSAGE',
    'SORT-MODE-SIZE',
    'SORT-RETURN',
    'SOURCE',
    'SOURCE-COMPUTER',
    'SOURCES',
    'SPACE',
    'SPACES',
    'SPECIAL-NAMES',
    'SQL',
    'SQLIMS',
    'STANDARD',
    'STANDARD-1',
    'STANDARD-2',
    'START',
    'STATUS',
    'STOP',
    'STRING',
    'SUB-QUEUE-1',
    'SUB-QUEUE-2',
    'SUB-QUEUE-3',
    'SUBTRACT',
    'SUM',
    'SUPER',
    'SUPPRESS',
    'SYMBOLIC',
    'SYNC',
    'SYNCHRONIZED',
    'SYSTEM-DEFAULT',
    'TABLE',
    'TALLY',
    'TALLYING',
    'TAPE',
    'TERMINAL',
    'TERMINATE',
    'TEST',
    'TEXT',
    'THAN',
    'THEN',
    'THROUGH',
    'THRU',
    'TIME',
    'TIMES',
    'TITLE',
    'TO',
    'TOP',
    'TOP-OF-PAGE',
    'TRACE',
    'TRAILING',
    'TRUE',
    'TYPE',
    'TYPEDEF',
    'UNIT',
    'UNIVERSAL',
    'UNLOCK',
    'UNSTRING',
    'UNTIL',
    'UP',
    'UPON',
    'USAGE',
    'USAGE-MODE',  # IDMS
    'USE',
    'USER-DEFAULT',
    'USING',
    'VAL-STATUS',
    'VALID',
    'VALIDATE',
    'VALIDATE-STATUS',
    'VALUE',
    'VALUES',
    'VARYING',
    'VOLATILE',
    'WHEN',
    'WHEN-COMPILED',
    'WITH',
    'WITHIN',  # IDMS
    'WORDS',
    'WORKING-STORAGE',
    'WRITE',
    'WRITE-ONLY',
    'XML',
    'XML-CODE',
    'XML-EVENT',
    'XML-INFORMATION',
    'XML-NAMESPACE',
    'XML-NAMESPACE-PREFIX',
    'XML-NNAMESPACE',
    'XML-NNAMESPACE-PREFIX',
    'XML-NTEXT',
    'XML-SCHEMA',
    'XML-TEXT',
    'ZERO',
    'ZEROES',
    'ZEROS',
    'XXBXXBX',
    'XXBXXXBX',
]

# Add "X" PIC types to reserved tokens list
for i in range(1, 100):
    COBOL_RESERVED_TOKENS.append('X' * i)

# Add "A" PIC types to reserved tokens list
for i in range(1, 100):
    COBOL_RESERVED_TOKENS.append('A' * i)

# Add "9" PIC types to reserved tokens list
for i in range(1, 100):
    COBOL_RESERVED_TOKENS.append('9' * i)
    COBOL_RESERVED_TOKENS.append(f'-{"-" * (i - 1)}9')

# Add "S9" and "V9" PIC types to reserved tokens list
for i in range(1, 100):
    nines = '9' * i
    COBOL_RESERVED_TOKENS.append('S' + nines)
    COBOL_RESERVED_TOKENS.append('V' + nines)

# Add "Z" PIC types to reserved tokens list
for i in range(1, 100):
    z = 'Z' * i
    COBOL_RESERVED_TOKENS.append(z + 'X')
    COBOL_RESERVED_TOKENS.append(z + 'A')
    COBOL_RESERVED_TOKENS.append(z + '9')
    COBOL_RESERVED_TOKENS.append(z + 'S9')
    COBOL_RESERVED_TOKENS.append(z + 'V9')

# Token that will be replaced with the target language scope closing token (e.g. '}')
SCOPE_CLOSE_TOKEN = '%scope_close%'

COBOL_NAME_SPLIT_REGEX = re.compile(r'-|:')

# Standard syntax regexes
COBOL_SOURCE_REGEX = re.compile(r'^>>SOURCE\s+.+$')
COBOL_DIVISION_REGEX = re.compile(r'^.*DIVISION\s*$')
COBOL_CUSTOM_SECTION_REGEX = re.compile(rf'^{gen_mask_token(0)}\s+SECTION$')
COBOL_IGNORED_SECTION_REGEX = re.compile(r'^(?!%mask_\d+%).+\s+SECTION$')
COBOL_DATE_COMPILED_REGEX = re.compile(r'^DATE-COMPILED\s*.*$')
COBOL_PROGRAM_ID_REGEX = re.compile(r'^PROGRAM-ID\.\s+(?P<name>[^.]*)$')
COBOL_AUTHOR_REGEX = re.compile(r'^AUTHOR\.\s+(?P<name>[^.]*)$')
COBOL_DATE_WRITTEN_REGEX = re.compile(r'^DATE-WRITTEN\.\s+(?P<date>[^.]*)$')
COBOL_COMPUTER_REGEX = re.compile(r'^.+-COMPUTER\s*\..*$')
COBOL_SPECIAL_NAMES_REGEX = re.compile(r'^SPECIAL-NAMES\..*$')
COBOL_PARAGRAPH_OR_SECTION_REGEX = re.compile(
    rf'^(?P<mask>{gen_mask_token(0)})(?P<section>\s+SECTION)?(?P<exit>\.\s+EXIT)?$')
COBOL_PARAGRAPH_OR_SECTION_SRC_REGEX = re.compile(
    rf'^(?P<name>[0-9a-zA-Z\-:]+)(?P<section>\s+SECTION)?$')
COBOL_ENTRY_REGEX = re.compile(r'^ENTRY\s+.*$')
COBOL_CALL_REGEX = re.compile(
    fr'^CALL\s+[\'"]?(?P<name>{gen_mask_token(0)})[\'"]?(?P<using>\s+USING\s+)?(?P<args>.+)?$')
COBOL_PERFORM_CALL_REGEX = re.compile(
    fr'^PERFORM\s+(?P<name>{gen_mask_token(0)})(?:\s+THRU\s+(?P<thru>{gen_mask_token(1)}))?(?:\s+UNTIL\s+(?P<until>.+))?$')
COBOL_THEN_REMOVAL_REGEX = re.compile(r'^\s*(?:ELSE-)?IF.*(?P<then>\sTHEN)$')
COBOL_STOP_RUN_REGEX = re.compile(r'^STOP RUN\s*$')
COBOL_GOBACK_REGEX = re.compile(r'^GOBACK\s*$')
COBOL_SKIP_REGEX = re.compile(r'^SKIP\d+$')
COBOL_COPY_REGEX = re.compile(
    r'^COPY(\s+IDMS)?\s+(?P<name>[0-9a-zA-Z\-:]+)(\s+REPLACING\s+[\'"](?P<old>[0-9a-zA-Z\-:]+)[\'"]\s+BY\s+[\'"](?P<new>[0-9a-zA-Z\-:]+)[\'"])?\s*\.?$'
)
COBOL_SET_ADDRESS_REGEX = re.compile(r'SET ADDRESS OF\s+.*\n+\s+(?:TO)+.*')
COBOL_EXEC_BLOCK_REGEX = re.compile(r'EXEC((?!END-EXEC).)*END-EXEC', re.DOTALL)
COBOL_LENGTH_OF_REGEX = re.compile(
    rf'LENGTH\s+OF\s+(?P<var_name>{MASK_TOKEN_REGEX_STR})')
COBOL_DB_SCHEMA_REGEX = re.compile(r'^DB\s+.+$')
COBOL_SUBVALUE_REGEX = re.compile(
    fr'^(?P<name>{MASK_TOKEN_REGEX_STR})\s*\(\s*(?P<start>{MASK_TOKEN_REGEX_STR})(?:\s*:\s*)?(?P<length>{MASK_TOKEN_REGEX_STR})?\s*\)$')

# Item regexes
COBOL_GROUP_ITEM_REGEX = re.compile(
    r'^(?P<lvl>\d{2})\s+(?P<name>[0-9a-zA-Z\-:]+)(?P<redefines>\s+REDEFINES\s+[0-9a-zA-Z\-:]+)?$'
)
COBOL_ELEM_ITEM_REGEX = re.compile(
    r'^(?P<lvl>\d{2})\s+(?P<name>[0-9a-zA-Z\-:]+)\s+(?:PIC|VALUES?)\s+[^.]+$')
COBOL_GROUP_ITEM_MASKED_REGEX = re.compile(
    rf'^{gen_mask_token(0)}\s+{gen_mask_token(1)}(?P<redefines>\s+REDEFINES\s+{MASK_TOKEN_REGEX_STR})?(?:\s+VALUE\s+.*)?$'
)
COBOL_BOOL_ITEM_WITH_VAL_REGEX = re.compile(
    rf'^88\s+{gen_mask_token(0)}\s+VALUE\s+(?P<quote>[\'"])?{gen_mask_token(1)}(?:[\'"])?$'
)
COBOL_BOOL_ITEM_WITH_MULTIPLE_VALS_REGEX = re.compile(
    rf'^88\s+{gen_mask_token(0)}\s+VALUES?\s+(?P<vals>[^.]+)$'
)
COBOL_BOOL_ITEM_THRU_REGEX = re.compile(
    rf'^88\s+{gen_mask_token(0)}\s+VALUES?\s+(?P<thru_start>[^\s]+)\s+THRU\s+(?P<thru_end>[^\s]+)$'
)

# Reserved value regexes
COBOL_RESERVED_VAR_REGEX = re.compile(
    r'^\d{2}\s+[0-9a-zA-Z\-:]+\s+PIC\s+[XASV9]+\s*\(?(?P<size>\d+)?\)?(?:V9+(?:\((?P<size_2>\d)\))?)?(?:\s+VALUE\s+)?(?P<val>\d+|ZEROE?S?|SPACES?)?$'
)
COBOL_RESERVED_BOOL_VAR_REGEX = re.compile(
    r'^\d{2}\s+[0-9a-zA-Z\-:]+\s+VALUE\s+(?P<val_1>9+)(\s+THRU\s+(?P<val_2>9+))?$'
)
COBOL_RESERVED_MOVE_REGEX = re.compile(
    rf'^MOVE\s+(?P<val>[9]+)\s+TO\s+[0-9a-zA-Z\-:]+$'
)
COBOL_RESERVED_MOVE_SUBVAL_TO_REGEX = re.compile(
    rf'^MOVE\s+[0-9a-zA-Z\-:%]+\s*\(\s*(?P<val>[9]+)\s*\)\s+TO\s+[0-9a-zA-Z\-:]+$'
)
COBOL_RESERVED_MOVE_TO_SUBVAL_REGEX = re.compile(
    rf'^MOVE\s+[\'"]?[0-9a-zA-Z\-:%]+[\'"]?\s+TO\s+[0-9a-zA-Z\-:]+\s*\(\s*(?P<val>[9]+)\s*\)$'
)
COBOL_RESERVED_NUMERIC_REGEXES = [
    COBOL_RESERVED_VAR_REGEX,
    COBOL_RESERVED_BOOL_VAR_REGEX,
    COBOL_RESERVED_MOVE_REGEX,
    COBOL_RESERVED_MOVE_SUBVAL_TO_REGEX,
    COBOL_RESERVED_MOVE_TO_SUBVAL_REGEX,
]

# "MOVE" statement regexes
COBOL_MOVE_REGEX = re.compile(
    rf'^MOVE\s+(?P<corresponding>CORRESPONDING\s+)?(?P<val_quote>[\'"])?{gen_mask_token(0)}[\'"]?\s+TO\s+(?P<destinations>[%mask_\d\s,]+)$'
)

# Switch statement regexes
COBOL_WHEN_REGEX = re.compile(rf'^WHEN\s+[\'"]?{gen_mask_token(0)}[\'"]?$')
COBOL_WHEN_PERFORM_REGEX = re.compile(
    rf'^WHEN\s+[\'"]?{gen_mask_token(0)}[\'"]?\s+PERFORM\s+{gen_mask_token(1)}$')
COBOL_WHEN_MOVE_REGEX = re.compile(
    rf'^WHEN\s+[\'"]?{gen_mask_token(0)}[\'"]?\s+MOVE\s+{gen_mask_token(1)}\s+TO\s+{gen_mask_token(2)}$'
)
COBOL_WHEN_OTHER_REGEX = re.compile(rf'^WHEN\s+OTHER$')
COBOL_WHEN_OTHER_PERFORM_REGEX = re.compile(
    rf'^WHEN\s+OTHER\s+PERFORM\s+{gen_mask_token(0)}$')
COBOL_WHEN_OTHER_MOVE_REGEX = re.compile(
    rf'^WHEN\s+OTHER\s+MOVE\s+{gen_mask_token(0)}\s+TO\s+{gen_mask_token(1)}$')
COBOL_END_EVALUATE_REGEX = re.compile(r'^END-EVALUATE$')

# IO regexes
COBOL_FILE_SELECT_REGEX = re.compile(
    rf'^SELECT\s+{gen_mask_token(0)}\s+ASSIGN(?:\s+TO)?\s+[\'"]?{gen_mask_token(1)}[\'"]?[^.]*$'
)
COBOL_SRC_FILE_DATA_REGEX = re.compile(
    rf'^(?:FD|SD)\s+(?P<file_name>[0-9a-zA-Z\-:]+)(?:\s+DATA\s+RECORD\s+IS\s+(?P<data_name>[0-9a-zA-Z\-:]+))?$')
COBOL_FILE_DATA_REGEX = re.compile(
    rf'^(?P<type>FD|SD)\s+{gen_mask_token(0)}(?:\s+DATA\s+RECORD\s+IS\s+{gen_mask_token(1)})?$')
COBOL_OPEN_INPUT_REGEX = re.compile(
    rf'^OPEN\s+INPUT\s+{gen_mask_token(0)}\s*?$')
COBOL_OPEN_EXTEND_REGEX = re.compile(
    rf'^OPEN\s+EXTEND\s+{gen_mask_token(0)}\s*?$')
COBOL_OPEN_OUTPUT_REGEX = re.compile(
    rf'^OPEN\s+OUTPUT\s+{gen_mask_token(0)}\s*?$')
COBOL_END_READ_REGEX = re.compile(r'^END-READ\s*$')
COBOL_END_WRITE_REGEX = re.compile(r'^END-WRITE\s*$')
COBOL_CLOSE_FILE_REGEX = re.compile(rf'^CLOSE\s+(?P<files>[^.]*)$')
COBOL_WRITE_REGEX = re.compile(
    rf'^WRITE\s+{gen_mask_token(0)}\s+FROM\s+{gen_mask_token(1)}$')
COBOL_WRITE_AFTER_ADVANCING_REGEX = re.compile(
    rf'^WRITE\s+{gen_mask_token(0)}\s+FROM\s+{gen_mask_token(1)}\s+AFTER\s+ADVANCING(?:\s+(?:PAGE|LINE))?$')
COBOL_WRITE_AFTER_ADVANCING_N_LINES_REGEX = re.compile(
    rf'^WRITE\s+{gen_mask_token(0)}\s+FROM\s+{gen_mask_token(1)}\s+AFTER\s+ADVANCING\s+{gen_mask_token(2)}(?:\s+LINES?|PAGE)?$')
COBOL_WRITE_AFTER_ADVANCING_TOP_OF_PAGE_REGEX = re.compile(
    rf'^WRITE\s+{gen_mask_token(0)}\s+FROM\s+{gen_mask_token(1)}\s+AFTER\s+ADVANCING\s+TOP-OF-PAGE$')
COBOL_WRITE_BEFORE_ADVANCING_REGEX = re.compile(
    rf'^WRITE\s+{gen_mask_token(0)}\s+FROM\s+{gen_mask_token(1)}\s+BEFORE\s+ADVANCING(?:\s+(?:PAGE|LINE))?$')
COBOL_WRITE_BEFORE_ADVANCING_N_LINES_REGEX = re.compile(
    rf'^WRITE\s+{gen_mask_token(0)}\s+FROM\s+{gen_mask_token(1)}\s+BEFORE\s+ADVANCING\s+{gen_mask_token(2)}(?:\s+LINES?|PAGE)?$')
COBOL_READ_REGEX = re.compile(rf'^READ\s+{gen_mask_token(0)}$')
COBOL_READ_AT_END_REGEX = re.compile(
    rf'^READ\s+{gen_mask_token(0)}\s+AT\s+END\s+(?P<at_end>.+)$')
COBOL_READ_INTO_REGEX = re.compile(
    rf'^READ\s+{gen_mask_token(0)}\s+INTO\s+{gen_mask_token(1)}$')
COBOL_READ_INTO_AT_END_REGEX = re.compile(
    rf'^READ\s+{gen_mask_token(0)}\s+INTO\s+{gen_mask_token(1)}\s+AT\s+END\s+(?P<at_end>.+)$')
COBOL_RELEASE_REGEX = re.compile(rf'^RELEASE\s+{gen_mask_token(0)}$')

# Formatter regexes
COBOL_FORMAT_CALL_REGEX = re.compile(r'CALL\s+[^.]*\s*\.', re.DOTALL)
COBOL_FORMAT_SELECT_REGEX = re.compile(r'SELECT\s+[^.]*\s*\.', re.DOTALL)
COBOL_FORMAT_PERFORM_REGEX = re.compile(
    r'PERFORM\s+[0-9a-zA-Z\-:]+(?:\s+(?:UNTIL|VARYING)\s+[^.]+)?(?:\s+THRU\s+[0-9a-zA-Z\-:]+(?:\s+UNTIL\s+[0-9a-zA-Z\-:]+)?)?\s*\.',
    re.DOTALL
)
COBOL_FORMAT_SORT_REGEX = re.compile(
    r'SORT\s+[0-9a-zA-Z\-:]+\s+ON\s+(?:ASCENDING|DESCENDING)\s+KEY\s+.*(?:\s+INPUT\s+PROCEDURE\s+IS\s+[0-9a-zA-Z\-:]+)(?:\s+OUTPUT\s+PROCEDURE\s+IS\s+[0-9a-zA-Z\-:]+)\.',
    re.DOTALL
)
COBOL_FORMAT_WRITE_REGEX = re.compile(
    r'WRITE\s+[0-9a-zA-Z\-:]+\s+FROM\s+[0-9a-zA-Z\-:]+(?:\s+AFTER\s+ADVANCING\s+(?:\d+\s+(?:LINES?|PAGES?))?(?:[0-9a-zA-Z\-:]+)?)?\.',
    re.DOTALL
)
COBOL_FORMAT_RETURN_REGEX = re.compile(
    r'RETURN\s+[0-9a-zA-Z\-:]+(?:\s+AT\s+END\s+[^.]+)?\s*\.', re.DOTALL)
COBOL_FORMAT_DISPLAY_REGEX = re.compile(r'DISPLAY\s+[^.]+\.', re.DOTALL)
COBOL_FORMAT_REDEFINES_REGEX = re.compile(
    r'\d{2}\s+[0-9a-zA-Z\-:]+\s+REDEFINES\s+[0-9a-zA-Z\-:]+\s+PIC\s+[^.]*\.', re.DOTALL
)
COBOL_FORMAT_PIC_REGEX = re.compile(
    r'\d{2}\s+(?P<name>[0-9a-zA-Z\-:]+)(?:\s+PIC\s+[^.]+)?(?:\s+VALUE[\'"]?(?P<val>[^.]*)?[\'"]?)?\s*\.', re.DOTALL
)
COBOL_FORMAT_PIC_COMMA_RM_REGEX = re.compile(
    r'\d{2}\s+(?P<name>[0-9a-zA-Z\-:]+)(?:\s+PIC\s+[^.\s]+)?'
)
COBOL_FORMAT_FILE_DATA_REGEX = re.compile(
    r'(?:FD|SD)\s+[^.]*\s*\.?', re.DOTALL)
COBOL_FORMAT_ENTRY_REGEX = re.compile(r'ENTRY\s+[^.]*\.', re.DOTALL)
COBOL_FORMAT_IF_REGEX = re.compile(r'IF\s+\([^\)]+\)', re.DOTALL)
COBOL_FORMAT_IF_ENDS_REGEX = re.compile(
    rf'IF\s+[^.]+\.(?!\s*{SCOPE_CLOSE_TOKEN})', re.DOTALL)
COBOL_FORMAT_RM_PROTOCOL_REGEX = re.compile(
    r'PROTOCOL\.\s+[\w\s-]+\.', re.DOTALL)
COBOL_FORMAT_RM_RECORDING_MODE_REGEX = re.compile(
    r'RECORDING\s+MODE\s+IS\s+[0-9a-zA-Z\-:]+', re.DOTALL)
COBOL_FORMAT_RM_BLOCK_CONTAINS_REGEX = re.compile(
    r'BLOCK\s+CONTAINS\s+\d+\s+RECORDS', re.DOTALL)
COBOL_FORMAT_RM_RECORD_CONTAINS_REGEX = re.compile(
    r'RECORD\s+CONTAINS\s+\d+\s+CHARACTERS', re.DOTALL)
COBOL_FORMAT_RM_LABEL_REGEX = re.compile(
    r'LABEL\s+RECORDS\s+ARE\s+STANDARD', re.DOTALL)
COBOL_FORMAT_RM_COMMENTS_REGEX = re.compile(r'\*.*')

COBOL_FORMAT_RM_REGEXES = [
    COBOL_FORMAT_RM_PROTOCOL_REGEX
]

COBOL_FORMAT_MULTILINE_REGEXES = [
    COBOL_FORMAT_PIC_REGEX,
    COBOL_FORMAT_REDEFINES_REGEX,
    COBOL_FORMAT_SELECT_REGEX,
    COBOL_FORMAT_FILE_DATA_REGEX,
    COBOL_FORMAT_CALL_REGEX,
    COBOL_FORMAT_ENTRY_REGEX,
    COBOL_FORMAT_PERFORM_REGEX,
    COBOL_FORMAT_SORT_REGEX,
    COBOL_FORMAT_WRITE_REGEX,
    COBOL_FORMAT_RETURN_REGEX,
]

# Add multiline formatting regexes for "MOVE" statements
for count in range(2, 6):
    destinations = [
        r'(?!PERFORM|MOVE|NEXT|ELSE|ELIF|OBTAIN)[0-9a-zA-Z\-:]+'] * count
    destinations = r'\s+'.join(destinations)
    move_re = re.compile(
        f'MOVE\s+(?:CORRESPONDING\s+)?[\'"]?[0-9a-zA-Z\-:]+[\'"]?\s+TO\s+{destinations}\.?',
        re.DOTALL
    )
    COBOL_FORMAT_MULTILINE_REGEXES.append(move_re)

# MTL regexes
COBOL_ISOLATED_KEYWORDS = r'COMP(?:-\d+)?|BINARY|PACKED-DECIMAL'
COBOL_ISOLATED_KEYWORD_NEWLINE_REGEX = re.compile(
    rf'\s(?:{COBOL_ISOLATED_KEYWORDS})\n')
COBOL_ISOLATED_KEYWORD_SPACE_REGEX = re.compile(
    rf'\s(?:{COBOL_ISOLATED_KEYWORDS})\s')
COBOL_ISOLATED_KEYWORD_DOT_REGEX = re.compile(
    rf'\s(?:{COBOL_ISOLATED_KEYWORDS})\.')
COBOL_RETURN_AT_END_REGEX = re.compile(
    fr'RETURN\s+{MASK_TOKEN_REGEX_STR}\s+AT\s+END\s+(?P<at_end>.+)')
COBOL_GLOBAL_FILE_DATA_REGEX = re.compile(
    rf'(?:FD|SD)\s+(?P<file_name>{MASK_TOKEN_REGEX_STR})(?:\s+DATA\s+RECORD\s+IS\s+(?P<data_name>{MASK_TOKEN_REGEX_STR}))?'
)
COBOL_REPL_FILE_DATA_REFS_REGEX = re.compile(
    rf'WRITE\s+(?P<write_to>{MASK_TOKEN_REGEX_STR})\s+FROM\s+{MASK_TOKEN_REGEX_STR}(?:\s+(?:AFTER|BEFORE)\s+ADVANCING\s+(?:{MASK_TOKEN_REGEX_STR}\s+)?(?:LINES?|PAGES?)?)?'
)

# IDMS
COBOL_IDMS_BIND_REGEX = re.compile(r'^BIND\s+.+$')
COBOL_IDMS_READY_REGEX = re.compile(r'^READY\s+.+\s+USAGE-MODE\s+.+$')
COBOL_IDMS_OBTAIN_FIRST_REGEX = re.compile(
    rf'^OBTAIN\s+FIRST\s+{gen_mask_token(0)}\s+WITHIN\s+{gen_mask_token(1)}$')
COBOL_IDMS_OBTAIN_NEXT_REGEX = re.compile(
    rf'^OBTAIN\s+NEXT\s+{gen_mask_token(0)}\s+WITHIN\s+{gen_mask_token(1)}$')
COBOL_IDMS_OBTAIN_OWNER_REGEX = re.compile(
    rf'^OBTAIN\s+OWNER\s+WITHIN\s+{gen_mask_token(0)}$')
COBOL_IDMS_OBTAIN_WITHIN_USING_REGEX = re.compile(
    rf'^OBTAIN\s+{gen_mask_token(0)}\s+WITHIN\s+{gen_mask_token(1)}\s+USING\s+{gen_mask_token(2)}$'
)
COBOL_IDMS_OBTAIN_CALC_REGEX = re.compile(
    rf'^OBTAIN\s+CALC\s+{gen_mask_token(0)}$')
COBOL_PERFORM_IDMS_STATUS_REGEX = re.compile(r'^PERFORM\s+IDMS-STATUS$')
COBOL_IDMS_DB_END_OF_SET_REGEX = re.compile(r'^(?P<not>NOT\s+)?DB-END-OF-SET$')
COBOL_IDMS_IF_DB_END_OF_SET_REGEX = re.compile(
    r'^IF\s+(?P<not>NOT\s+)?DB-END-OF-SET(?:\s+THEN)?$')
COBOL_IDMS_NOT_ANY_ERROR_STATUS_REGEX = re.compile(r'^NOT\s+ANY-ERROR-STATUS$')
COBOL_IDMS_IF_ANY_ERROR_STATUS_REGEX = re.compile(
    r'^IF\s+ANY-ERROR-STATUS(?:\s+THEN)?$')
COBOL_IDMS_IF_NOT_ANY_ERROR_STATUS_REGEX = re.compile(
    r'^IF\s+NOT\s+ANY-ERROR-STATUS(?:\s+THEN)?$')

COBOL_IGNORED_COPYBOOKS = [
    # IDMS
    'SUBSCHEMA-CONTROL',
    'IDMS-STATUS',
]
