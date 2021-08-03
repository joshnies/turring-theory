import re

from theory.languages.cobol.definition import CobolDefinition
from theory.languages.cobol.constants import COBOL_PROGRAM_ID_REGEX, COBOL_PARAGRAPH_OR_SECTION_SRC_REGEX, \
    COBOL_RESERVED_TOKENS, \
    COBOL_SRC_FILE_DATA_REGEX
from theory.lvps.base_template_processor import TemplateProcessor

TEMPL_FILE_DETAILS = 'file_details'
TEMPL_PROGRAM_NAME = 'program_name'
TEMPL_CLASS_NAME = 'class_name'
TEMPL_MEMBER_VARS = 'member_vars'
TEMPL_MEMBER_VAR_ASSIGNMENTS = 'member_var_assignments'
TEMPL_FILE_DATA_ATTACHMENTS = 'file_data_attachments'
TEMPL_MEMBER_FUNCS = 'member_funcs'
TEMPL_MAIN = 'main'
TEMPL_DEL_SORT_FILES = 'delete_sort_files'


class COBOLToCSharp9TemplateProcessor(TemplateProcessor):
    """Template processor for COBOL to C# 9."""

    def __init__(self):
        super().__init__()

        # Define template file path
        self.template_file_path += 'cobol_to_csharp.txt'

        # Map of delineators to template tags
        self.delineator_map = {
            re.compile(r'^IDENTIFICATION\s+DIVISION$'): TEMPL_FILE_DETAILS,
            re.compile(r'^FILE-CONTROL$'): TEMPL_MEMBER_VAR_ASSIGNMENTS,
            re.compile(r'^WORKING-STORAGE\s+SECTION$'): TEMPL_MEMBER_VAR_ASSIGNMENTS,
            re.compile(r'^PROCEDURE\s+DIVISION$'): TEMPL_MAIN,
        }

        # Map for tags to replacement content
        self.default_tag_content = {
            TEMPL_FILE_DETAILS: list(),
            TEMPL_PROGRAM_NAME: list(),
            TEMPL_CLASS_NAME: list(),
            TEMPL_MEMBER_VARS: list(),
            TEMPL_MEMBER_VAR_ASSIGNMENTS: list(),
            TEMPL_FILE_DATA_ATTACHMENTS: list(),
            TEMPL_MEMBER_FUNCS: list(),
            TEMPL_MAIN: list(),
            TEMPL_DEL_SORT_FILES: list(),
        }

        self.tag_content = self.default_tag_content.copy()
        self.current_tag = TEMPL_FILE_DETAILS

    def update_delineator(self, src_line: str, indent: int):
        # File data attachments
        match = re.match(COBOL_SRC_FILE_DATA_REGEX, src_line)

        if match is not None:
            self.defer_current_tag()
            self.current_tag = TEMPL_FILE_DATA_ATTACHMENTS
            return

        # COBOL program ID to the C# class name
        match = re.match(COBOL_PROGRAM_ID_REGEX, src_line)

        if match is not None:
            # Set program name tag
            program_name = match.group('name')
            self.tag_content[TEMPL_PROGRAM_NAME].append(program_name)

            # Set class name tag
            class_name = CobolDefinition.name_to_title_case(program_name)
            self.tag_content[TEMPL_CLASS_NAME].append(class_name)
            return

        # COBOL paragraphs and custom sections to member functions
        if indent == 7:
            match = re.match(COBOL_PARAGRAPH_OR_SECTION_SRC_REGEX, src_line)

            if match is not None and match.group('name') not in COBOL_RESERVED_TOKENS:
                self.current_tag = TEMPL_MEMBER_FUNCS
                return

        super().update_delineator(src_line, indent)

    def build(self) -> str:
        # Add scope closing bracket for final member func
        if len(self.tag_content[TEMPL_MEMBER_FUNCS]) > 0:
            self.tag_content[TEMPL_MEMBER_FUNCS].append('}')

        return super().build()
