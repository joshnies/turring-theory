from theory.languages.cobol.constants import *
from theory.utils import gen_mask_token

SECTION_CALLS_TAG = '%section_calls%'

COBOL_TO_CSHARP_IGNORED_SEQS = [
    'FILE-CONTROL',
    'EJECT',
    'GOBACK',
    # IDMS
    'FINISH',
]

COBOL_TO_CSHARP_IGNORED_SEQ_REGEXES = [
    COBOL_SOURCE_REGEX,
    COBOL_DIVISION_REGEX,
    COBOL_IGNORED_SECTION_REGEX,
    COBOL_DATE_COMPILED_REGEX,
    COBOL_COMPUTER_REGEX,
    COBOL_SPECIAL_NAMES_REGEX,
    COBOL_STOP_RUN_REGEX,
    COBOL_SKIP_REGEX,
    COBOL_ENTRY_REGEX,
    COBOL_GROUP_ITEM_MASKED_REGEX,
    COBOL_OPEN_INPUT_REGEX,
    COBOL_OPEN_OUTPUT_REGEX,
    COBOL_OPEN_EXTEND_REGEX,
    COBOL_CLOSE_FILE_REGEX,
    COBOL_END_READ_REGEX,
    COBOL_END_WRITE_REGEX,
    COBOL_READ_REGEX,
    COBOL_DB_SCHEMA_REGEX,
    re.compile(r'^DISPLAY\s+NULL$'),
    re.compile(r'^NEXT\s+SENTENCE$'),
    # IDMS
    COBOL_IDMS_BIND_REGEX,
    COBOL_IDMS_READY_REGEX,
    COBOL_PERFORM_IDMS_STATUS_REGEX,
]

# TODO: Move items that dont have single-token keys to "COBOL_TO_CSHARP_ITL_REGEX_MAP" instead
COBOL_TO_CSHARP_ITL_MAP = {
    # Formatted/preprocessed tokens
    SCOPE_CLOSE_TOKEN: '}',
    # Standard syntax
    'EXIT': 'return;',
    'ELSE': '} else {',
    'END-IF': '}',
    'END-PERFORM': '}',
    # GO TO statements
    f'GO TO {gen_mask_token(0)}': f'{gen_mask_token(0)}();',
    f'GO TO {gen_mask_token(0)} DEPENDING ON {gen_mask_token(1)}': f'COBOLUtils.CallByNum({gen_mask_token(1)}, new Action[] {{ {gen_mask_token(0)} }});',
    f'GO TO {gen_mask_token(0)} {gen_mask_token(1)} DEPENDING ON {gen_mask_token(2)}': f'COBOLUtils.CallByNum({gen_mask_token(2)}, new Action[] {{ {gen_mask_token(0)}, {gen_mask_token(1)} }});',
    f'GO TO {gen_mask_token(0)} {gen_mask_token(1)} {gen_mask_token(2)} DEPENDING ON {gen_mask_token(3)}': f'COBOLUtils.CallByNum({gen_mask_token(3)}, new Action[] {{ {gen_mask_token(0)}, {gen_mask_token(1)}, {gen_mask_token(2)} }});',
    f'GO TO {gen_mask_token(0)} {gen_mask_token(1)} {gen_mask_token(2)} {gen_mask_token(3)} DEPENDING ON {gen_mask_token(4)}': f'COBOLUtils.CallByNum({gen_mask_token(4)}, new Action[] {{ {gen_mask_token(0)}, {gen_mask_token(1)}, {gen_mask_token(2)}, {gen_mask_token(3)} }});',
    # "CALL" statements
    f"CALL '{gen_mask_token(0)}'": f"{gen_mask_token(0)}();",
    f"CALL '{gen_mask_token(0)}' USING {gen_mask_token(1)}": f"{gen_mask_token(0)}({gen_mask_token(1)});",
    f"CALL '{gen_mask_token(0)}' USING {gen_mask_token(1)}, {gen_mask_token(2)}": f"{gen_mask_token(0)}({gen_mask_token(1)}, {gen_mask_token(2)});",
    f"CALL '{gen_mask_token(0)}' USING {gen_mask_token(1)}, {gen_mask_token(2)}, {gen_mask_token(3)}": f"{gen_mask_token(0)}({gen_mask_token(1)}, {gen_mask_token(2)}, {gen_mask_token(3)});",
    f"CALL '{gen_mask_token(0)}' USING {gen_mask_token(1)}, {gen_mask_token(2)}, {gen_mask_token(3)}, {gen_mask_token(4)}": f"{gen_mask_token(0)}({gen_mask_token(1)}, {gen_mask_token(2)}, {gen_mask_token(3)}, {gen_mask_token(4)});",
    f"CALL '{gen_mask_token(0)}' USING {gen_mask_token(1)}, {gen_mask_token(2)}, {gen_mask_token(3)}, {gen_mask_token(4)}, {gen_mask_token(5)}": f"{gen_mask_token(0)}({gen_mask_token(1)}, {gen_mask_token(2)}, {gen_mask_token(3)}, {gen_mask_token(4)}, {gen_mask_token(5)});",
    # Loops
    f'PERFORM {gen_mask_token(0)} {gen_mask_token(1)} TIMES': f'for (int i = 0; i < {gen_mask_token(1)}; i++) {{ {gen_mask_token(0)}(); }}',
    # Switch statements
    f'EVALUATE {gen_mask_token(0)}': f'switch({gen_mask_token(0)}) {{',
    # IDMS
    'ANY-ERROR-STATUS': 'false'
}

COBOL_TO_CSHARP_ITL_REGEX_MAP = {
    re.compile(r'^DISPLAY\s+SPACES?$'): 'Console.WriteLine(" ");',
    re.compile(r'^DISPLAY\s+ZEROE?S?$'): 'Console.WriteLine("0");',
    re.compile(rf'^ACCEPT\s+{gen_mask_token(0)}$'): f'{gen_mask_token(0)}.Set(Console.Read());',
    re.compile(rf'^ACCEPT\s+{gen_mask_token(0)}\s+FROM\s+DATE$'):
        f'{gen_mask_token(0)}.Set(int.Parse(DateTime.Today.ToString("yyMMdd")));',
    re.compile(rf'^ACCEPT\s+{gen_mask_token(0)}\s+FROM\s+DATE\s+YYYYMMDD$'):
        f'{gen_mask_token(0)}.Set(int.Parse(DateTime.Today.ToString("yyyyMMdd")));',
    re.compile(rf'^ACCEPT\s+{gen_mask_token(0)}\s+FROM\s+DAY$'):
        f'{gen_mask_token(0)}.Set(int.Parse(DateTime.Today.ToString("yydd")));',
    re.compile(rf'^ACCEPT\s+{gen_mask_token(0)}\s+FROM\s+DAY\s+YYYYDDD$'):
        f'{gen_mask_token(0)}.Set(int.Parse(DateTime.Today.ToString("yyyydd")));',
    re.compile(rf'^ACCEPT\s+{gen_mask_token(0)}\s+FROM\s+DAY-OF-WEEK$'):
        f'{gen_mask_token(0)}.Set(DateTime.Today.DayOfWeek);',
    re.compile(rf'^ACCEPT\s+{gen_mask_token(0)}\s+FROM\s+TIME$'):
        f'{gen_mask_token(0)}.Set(int.Parse(DateTime.Today.ToString("HHmmssff")));',
    re.compile(rf'^PERFORM\s+{gen_mask_token(0)}\s*$'): f'{gen_mask_token(0)}();',
    # "SET" variable assignments
    re.compile(rf'^SET\s+(?:ADDRESS\s+OF\s+)?{gen_mask_token(0)}\s+TO\s+{gen_mask_token(1)}$'):
        f'{gen_mask_token(0)}.Set({gen_mask_token(1)});',
    re.compile(rf'^SET\s+{gen_mask_token(0)}\s+TO\s+[\'"]+{gen_mask_token(1)}[\'"]+$'):
        f'{gen_mask_token(0)}.Set("{gen_mask_token(1)}");',
    re.compile(rf'^SET\s+{gen_mask_token(0)}\s+TO\s+NULL$'):
        f'{gen_mask_token(0)}.Set(null);',
    re.compile(rf'^SET\s+{gen_mask_token(0)}\s+TO\s+SPACES?$'):
        f"{gen_mask_token(0)}.Set(new string(' ', {gen_mask_token(0)}.size));",
    re.compile(rf'^SET\s+{gen_mask_token(0)}\s+TO\s+ZEROE?S?$'):
        f'{gen_mask_token(0)}.Set(0);',
    # Set to var subvalue
    re.compile(rf'^MOVE\s+{gen_mask_token(0)}\s*\(\s*{gen_mask_token(1)}\s*\)\s+TO\s+{gen_mask_token(2)}$'):
        f'{gen_mask_token(2)}.Set({gen_mask_token(0)}.GetSubvalue(start: {gen_mask_token(1)}));',
    re.compile(
        rf'^MOVE\s+{gen_mask_token(0)}\s*\(\s*{gen_mask_token(1)}\s*:\s*{gen_mask_token(2)}\s*\)\s+TO\s+{gen_mask_token(3)}$'):
        f'{gen_mask_token(3)}.Set({gen_mask_token(0)}.GetSubvalue(start: {gen_mask_token(1)}, length: {gen_mask_token(2)}));',
    # Set var subvalue
    re.compile(rf'^MOVE\s+{gen_mask_token(0)}\s+TO\s+{gen_mask_token(1)}\s*\(\s*{gen_mask_token(2)}\s*\)$'):
        f'{gen_mask_token(1)}.SetSubvalue(newValue: {gen_mask_token(0)}, start: {gen_mask_token(2)});',
    re.compile(rf"^MOVE\s+'{gen_mask_token(0)}'\s+TO\s+{gen_mask_token(1)}\s*\(\s*{gen_mask_token(2)}\s*\)$"):
        f'{gen_mask_token(1)}.SetSubvalue(newValue: "{gen_mask_token(0)}", start: {gen_mask_token(2)});',
    re.compile(rf'^MOVE\s+"{gen_mask_token(0)}"\s+TO\s+{gen_mask_token(1)}\s*\(\s*{gen_mask_token(2)}\s*\)$'):
        f'{gen_mask_token(1)}.SetSubvalue(newValue: "{gen_mask_token(0)}", start: {gen_mask_token(2)});',
    re.compile(rf'^MOVE\s+SPACES?\s+TO\s+{gen_mask_token(0)}\s*\(\s*{gen_mask_token(1)}\s*\)$'):
        f'{gen_mask_token(0)}.SetSubvalue(newValue: new string(" ", {gen_mask_token(0)}.size), start: {gen_mask_token(1)});',
    re.compile(rf'^MOVE\s+ZEROE?S?\s+TO\s+{gen_mask_token(0)}\s*\(\s*{gen_mask_token(1)}\s*\)$'):
        f'{gen_mask_token(0)}.SetSubvalue(newValue: 0, start: {gen_mask_token(1)});',
    re.compile(
        rf'^MOVE\s+{gen_mask_token(0)}\s+TO\s+{gen_mask_token(1)}\s*\(\s*{gen_mask_token(2)}\s*:\s*{gen_mask_token(3)}\s*\)$'):
        f'{gen_mask_token(1)}.SetSubvalue(newValue: {gen_mask_token(0)}, start: {gen_mask_token(2)}, length: {gen_mask_token(3)});',
    re.compile(
        rf"^MOVE\s+'{gen_mask_token(0)}'\s+TO\s+{gen_mask_token(1)}\s*\(\s*{gen_mask_token(2)}\s*:\s*{gen_mask_token(3)}\s*\)$"):
        f'{gen_mask_token(1)}.SetSubvalue(newValue: "{gen_mask_token(0)}", start: {gen_mask_token(2)}, length: {gen_mask_token(3)});',
    re.compile(
        rf'^MOVE\s+"{gen_mask_token(0)}"\s+TO\s+{gen_mask_token(1)}\s*\(\s*{gen_mask_token(2)}\s*:\s*{gen_mask_token(3)}\s*\)$'):
        f'{gen_mask_token(1)}.SetSubvalue(newValue: "{gen_mask_token(0)}", start: {gen_mask_token(2)}, length: {gen_mask_token(3)});',
    # Set var to constant
    re.compile(rf'MOVE\s+SPACE\s+TO\s+{gen_mask_token(0)}'): f'{gen_mask_token(0)}.Set(" ", fill: true);',
    re.compile(rf'MOVE\s+SPACES\s+TO\s+{gen_mask_token(0)}'): f'{gen_mask_token(0)}.Set(" ", fill: true);',
    re.compile(rf'MOVE\s+ZERO\s+TO\s+{gen_mask_token(0)}'): f'{gen_mask_token(0)}.Set(0, fill: true);',
    re.compile(rf'MOVE\s+ZEROS\s+TO\s+{gen_mask_token(0)}'): f'{gen_mask_token(0)}.Set(0, fill: true);',
    re.compile(rf'MOVE\s+ZEROES\s+TO\s+{gen_mask_token(0)}'): f'{gen_mask_token(0)}.Set(0, fill: true);',
    re.compile(rf'MOVE\s+HIGH-VALUES\s+TO\s+{gen_mask_token(0)}'): f'{gen_mask_token(0)}.Set("F", fill: true);',
    re.compile(rf'MOVE\s+LOW-VALUES\s+TO\s+{gen_mask_token(0)}'): f'{gen_mask_token(0)}.Set("0", fill: true);',
    re.compile(rf'MOVE\s+NULL\s+TO\s+{gen_mask_token(0)}'): f'{gen_mask_token(0)}.Set(null);',
    # Switch statements
    COBOL_WHEN_REGEX: f'case "{gen_mask_token(0)}":',
    COBOL_WHEN_PERFORM_REGEX: f'case "{gen_mask_token(0)}":\n{gen_mask_token(1)}();\nbreak;',
    COBOL_WHEN_MOVE_REGEX: f'case "{gen_mask_token(0)}":\n{gen_mask_token(2)}.Set({gen_mask_token(1)});\nbreak;',
    COBOL_WHEN_OTHER_REGEX: f'default:',
    COBOL_WHEN_OTHER_PERFORM_REGEX: f'default:\n{gen_mask_token(0)}();\nbreak;',
    COBOL_WHEN_OTHER_MOVE_REGEX: f'default:\n{gen_mask_token(1)}.Set({gen_mask_token(0)});\nbreak;',
    COBOL_END_EVALUATE_REGEX: '}',
    # File IO
    COBOL_FILE_SELECT_REGEX: f'{gen_mask_token(0)} = new COBOLFile(@"{gen_mask_token(1)}");',
    COBOL_WRITE_REGEX: f'{gen_mask_token(0)}.Append({gen_mask_token(1)});',
    COBOL_WRITE_AFTER_ADVANCING_REGEX: f'{gen_mask_token(0)}.AppendLine({gen_mask_token(1)}.ToString());',
    COBOL_WRITE_AFTER_ADVANCING_N_LINES_REGEX: rf"{gen_mask_token(0)}.Append(new string('\n', {gen_mask_token(2)}) + {gen_mask_token(1)}.ToString());",
    COBOL_WRITE_BEFORE_ADVANCING_REGEX: rf'{gen_mask_token(0)}.Append({gen_mask_token(1)}.ToString() + "\n");',
    COBOL_WRITE_BEFORE_ADVANCING_N_LINES_REGEX: rf"{gen_mask_token(0)}.Append({gen_mask_token(1)}.ToString() + new string('\n', {gen_mask_token(2)}));",
    COBOL_READ_INTO_REGEX: f'{gen_mask_token(1)}.Set({gen_mask_token(0)}.Read());',
    COBOL_RELEASE_REGEX: f'{gen_mask_token(0)}.AppendLine();',
    # IDMS
    COBOL_IDMS_NOT_ANY_ERROR_STATUS_REGEX: f'true',
    COBOL_IDMS_IF_ANY_ERROR_STATUS_REGEX: f'if (false) {{',
    COBOL_IDMS_IF_NOT_ANY_ERROR_STATUS_REGEX: f'if (true) {{',
}
