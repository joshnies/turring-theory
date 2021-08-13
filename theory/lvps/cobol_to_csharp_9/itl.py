import logging
import re
from typing import Optional

from cli import log
from theory.languages.csharp.definition import CSharpDefinition
from theory.lvps.base_template_processor import TemplateProcessor
from theory.lvps.cobol_to_csharp_9.constants import COBOL_TO_CSHARP_IGNORED_SEQS, COBOL_TO_CSHARP_IGNORED_SEQ_REGEXES, \
    COBOL_TO_CSHARP_ITL_MAP, COBOL_TO_CSHARP_ITL_REGEX_MAP, SECTION_CALLS_TAG
from theory.lvps.base_itl import ITL
from theory.languages.cobol.constants import COBOL_PROGRAM_ID_REGEX, COBOL_AUTHOR_REGEX, COBOL_DATE_WRITTEN_REGEX, \
    COBOL_PARAGRAPH_OR_SECTION_REGEX, COBOL_CALL_REGEX, COBOL_PERFORM_CALL_REGEX, COBOL_BOOL_ITEM_WITH_VAL_REGEX, \
    COBOL_BOOL_ITEM_WITH_MULTIPLE_VALS_REGEX, COBOL_BOOL_ITEM_THRU_REGEX, \
    COBOL_READ_AT_END_REGEX, COBOL_READ_INTO_AT_END_REGEX, COBOL_MOVE_REGEX, COBOL_SUBVALUE_REGEX, \
    COBOL_IDMS_OBTAIN_FIRST_REGEX, COBOL_IDMS_OBTAIN_NEXT_REGEX, COBOL_IDMS_DB_END_OF_SET_REGEX, \
    COBOL_IDMS_IF_DB_END_OF_SET_REGEX, COBOL_IDMS_OBTAIN_CALC_REGEX, COBOL_IDMS_OBTAIN_OWNER_REGEX, \
    COBOL_IDMS_OBTAIN_WITHIN_USING_REGEX, COBOL_FILE_DATA_REGEX
from theory.languages.cobol.definition import CobolDefinition
from theory.lvps.cobol_to_csharp_9.store import COBOLToCSharp9Store
from theory.lvps.cobol_to_csharp_9.template_processor import TEMPL_MAIN, TEMPL_MEMBER_VAR_ASSIGNMENTS, \
    TEMPL_MEMBER_VARS, TEMPL_DEL_SORT_FILES, TEMPL_MEMBER_FUNCS
from theory.utils import gen_mask_token, split_upper, rreplace
from theory.veil import Veil


class COBOLToCSharp9ITL(ITL):
    """ITL for COBOL to C# 9."""

    def __init__(self, data_map_path: str, veil: Veil, store: COBOLToCSharp9Store,
                 template_processor: Optional[TemplateProcessor], translate_callback):
        super().__init__(data_map_path, veil, store, template_processor, translate_callback)

        # Reassign store for correct type detection
        self.store = store

        if store is None:
            raise Exception("Store is required for COBOL --> C# 9 ITL.")

        if template_processor is None:
            raise Exception("Template processor is required for COBOL --> C# 9 ITL.")

        self.current_section: Optional[str] = None
        self.current_paragraph: Optional[str] = None
        self.current_section_tag_idx: Optional[int] = None
        self.current_section_paragraphs = list()
        self.uses_db = False

        # IDMS
        self.last_obtained_record = None

    def translate(self, seq: str, indent: int = 0):
        # Ignores via equality
        for ignored_seq in COBOL_TO_CSHARP_IGNORED_SEQS:
            if seq == ignored_seq:
                return ''

        # Ignores via regex
        for ignored_regex in COBOL_TO_CSHARP_IGNORED_SEQ_REGEXES:
            match = re.match(ignored_regex, seq)

            if match is not None:
                return ''

        # Translate based on map
        for src, translation in COBOL_TO_CSHARP_ITL_MAP.items():
            if seq == src:
                return translation

        # Translate based on map
        for src_regex, translation in COBOL_TO_CSHARP_ITL_REGEX_MAP.items():
            if re.match(src_regex, seq):
                return translation

        # Program ID
        match = re.match(COBOL_PROGRAM_ID_REGEX, seq)
        if match is not None:
            name = match.group('name')
            return f'// {name}'

        # Author
        match = re.match(COBOL_AUTHOR_REGEX, seq)
        if match is not None:
            name = match.group('name')
            return f'// Author: {name}'

        # Date written
        match = re.match(COBOL_DATE_WRITTEN_REGEX, seq)
        if match is not None:
            date = match.group('date')
            return f'// Date written: {date}'

        # Bool items with value-based conditions
        match = re.match(COBOL_BOOL_ITEM_WITH_VAL_REGEX, seq)
        if match is not None:
            parent_item = self.store.last_item_name

            if parent_item is None:
                return f'// [Turring Theory] ERROR: The following bool item has no parent item:\n// {seq}'

            quote = '' if match.group('quote') is None else '"'

            return f'{gen_mask_token(0)} = new COBOLVar(\n\t' \
                   f'null,\n\t' \
                   f'size: 1,\n\t' \
                   f'conditionVar: {parent_item},\n\t' + \
                   f'conditionFunc: item => item.value == {quote}{gen_mask_token(1)}{quote}\n' \
                   f');'

        # Bool items with multiple value-based conditions
        match = re.match(COBOL_BOOL_ITEM_WITH_MULTIPLE_VALS_REGEX, seq)
        if match is not None:
            parent_item = self.store.last_item_name

            if parent_item is None:
                return f'// [Turring Theory] ERROR: The following bool item has no parent item:\n// {seq}'

            vals = list()
            list_type = 'dynamic'

            for val in match.group('vals').split(' '):
                is_str = val.startswith("'") or val.startswith('"')
                quote = '"' if is_str else ''
                vals.append(f'{quote}{gen_mask_token(0)}{quote}')

            vals = ', '.join(vals)

            return f'{gen_mask_token(0)} = new COBOLVar(\n\t' \
                   f'null,\n\t' \
                   f'size: 1,\n\t' \
                   f'conditionVar: {parent_item},\n\t' \
                   f'conditionFunc: item => new List<{list_type}>(new {list_type}[] {{ {vals} }})' + \
                   '.Contains(item.value)' \
                   '\n);'

        # Bool items with "THRU" condition
        match = re.match(COBOL_BOOL_ITEM_THRU_REGEX, seq)
        if match is not None:
            parent_item = self.store.last_item_name

            if parent_item is None:
                return f'// [Turring Theory] ERROR: The following bool item has no parent item:\n// {seq}'

            thru_start = match.group('thru_start')
            thru_end = match.group('thru_end')

            return f'{gen_mask_token(0)} = new COBOLVar(\n\t' \
                   f'null,\n\t' \
                   f'size: 1,\n\t' \
                   f'conditionVar: {parent_item},\n\t' \
                   f'conditionFunc: item => item.value >= {thru_start} && item.value <= {thru_end}\n' \
                   f');'

        # Translate file data attachments
        match = re.match(COBOL_FILE_DATA_REGEX, seq)
        if match is not None:
            # If for sort file, add ".delete()" statement at end of "Run()" method
            if match.group('type') == 'SD':
                file_var_name = self.veil.from_relative(gen_mask_token(0))
                file_var_name = self.veil.unmask(file_var_name)

                if len(self.template_processor.tag_content[TEMPL_DEL_SORT_FILES]) == 0:
                    self.template_processor.tag_content[TEMPL_DEL_SORT_FILES].append('\n// Delete temporary sort files')

                self.template_processor.tag_content[TEMPL_DEL_SORT_FILES].append(f'{file_var_name}.delete();')

            return f'{gen_mask_token(0)}.AttachData({gen_mask_token(1)});'

        # Translate "MOVE" statements
        match = re.match(COBOL_MOVE_REGEX, seq)
        if match is not None:
            result_lines = list()
            tar_set_method = 'SetMatched' if match.group('corresponding') else 'Set'
            tar_quote = '"' if match.group('val_quote') is not None else ''
            destinations = re.split(r',?\s', match.group('destinations'))

            for d in destinations:
                if d.strip() == '':
                    continue

                result_lines.append(f'{d}.{tar_set_method}({tar_quote}{gen_mask_token(0)}{tar_quote});')

            return '\n'.join(result_lines)

        # Translate paragraph and custom section names (which always have an indentation of 7 spaces)
        if indent == 7:
            match = re.match(COBOL_PARAGRAPH_OR_SECTION_REGEX, seq)

            if match is not None:
                mask_token = match.group('mask')
                name = self.veil.unmask(self.veil.from_relative(mask_token))

                section_calls_tag = f'{SECTION_CALLS_TAG}\n' if self.current_section is not None \
                                                                and len(self.current_section_paragraphs) == 0 else ''

                # Set index in member funcs tag content of "section calls" tag
                if section_calls_tag != '':
                    self.current_section_tag_idx = len(self.template_processor.tag_content[TEMPL_MEMBER_FUNCS])

                prefix = '' if self.current_paragraph is None else f'{section_calls_tag}}}\n\n'

                closes = match.group('exit') is not None
                closing_bracket = '}' if closes else ''

                if closes:
                    # Reset current paragraph to None since empty paragraph immediately closes
                    self.current_paragraph = None
                else:
                    # Set current paragraph
                    self.current_paragraph = name

                if match.group('section') is not None:
                    # Add section calls to current section
                    if self.current_section is not None:
                        # Get section calls
                        section_calls = self.build_section_calls()

                        # Replace section calls tag with section calls in template processor
                        section_translation = \
                            self.template_processor.tag_content[TEMPL_MEMBER_FUNCS][self.current_section_tag_idx]

                        self.template_processor.tag_content[TEMPL_MEMBER_FUNCS][self.current_section_tag_idx] = \
                            section_translation.replace(SECTION_CALLS_TAG, section_calls)

                    # Set new current section
                    self.current_section = name
                    self.current_section_paragraphs.clear()
                elif self.current_section is not None:
                    # Add paragraph to current section
                    added_paragraph = self.current_paragraph if self.current_paragraph is not None else name
                    self.current_section_paragraphs.append(added_paragraph)

                # Add call to paragraph method into app "Run()" method
                self.template_processor.tag_content[TEMPL_MAIN].append(f'{name}();')

                return f'{prefix}public void {name}()\n{{{closing_bracket}'

        # Translate "CALL" statements
        match = re.match(COBOL_CALL_REGEX, seq)

        if match is not None:
            # Translate paragraph/section name
            name = self.veil.from_relative(match.group('name'))
            name = self.veil.unmask(name)
            name = CobolDefinition.name_to_title_case(name)
            args = ''

            if match.group('using') is not None:
                # Translate args
                src_args_list = re.split(re.compile(r'\s+'), match.group('args'))
                tar_args_list = list()

                for src_arg in src_args_list:
                    tar_arg = src_arg

                    # Translate subvalues
                    subval_match = re.match(COBOL_SUBVALUE_REGEX, src_arg)

                    if subval_match is not None:
                        subval_name = subval_match.group('name')
                        subval_start = subval_match.group('start')
                        len_group = subval_match.group('length')
                        subval_len = '' if len_group is None else f', length: {len_group}'
                        tar_arg = f'{subval_name}.GetSubvalue(start: {subval_start}{subval_len})'

                    # Translate arg
                    tar_arg = self.veil.from_relative(tar_arg)
                    tar_arg = self.veil.unmask(tar_arg)
                    tar_args_list.append(tar_arg)

                args = ', '.join(tar_args_list)

            return f'{name}({args});'

        # Translate "PERFORM" call without args
        match = re.match(COBOL_PERFORM_CALL_REGEX, seq)

        if match is not None:
            name = self.veil.from_relative(match.group('name'))
            name = self.veil.unmask(name)

            result = f'{name}();'

            # Translate "THRU" clause
            thru = match.group('thru')
            if thru is not None:
                last_func_name = self.veil.from_relative(thru)
                last_func_name = self.veil.unmask(last_func_name)
                start_idx = self.store.method_names.index(name)
                end_idx = self.store.method_names.index(last_func_name)
                funcs = self.store.method_names[start_idx:end_idx + 1]
                funcs = list(map(lambda f: f'{f}();', funcs))
                result = '\n'.join(funcs)

            # Translate "UNTIL" clause
            until = match.group('until')
            if until is not None:
                offset = 1 if thru is None else 2
                # Offset mask indices by -2
                until = self.veil.offset(until, offset * -1)

                # Translate
                if until == gen_mask_token(0):
                    condition_masked = until
                else:
                    condition_masked = self.translate_callback(until, from_relative=False, unmask=False)

                # Offset by mask indices +2
                condition_masked = self.veil.offset(condition_masked, offset)
                # Convert to global space and unmask
                condition = self.veil.from_relative(condition_masked)
                condition = self.veil.unmask(condition)
                # Invert condition if possible (for simplification)
                inverted_condition = CSharpDefinition.invert_condition(condition)
                condition_was_inverted = inverted_condition is not None
                condition = inverted_condition if condition_was_inverted else condition
                # Determine prefix and suffix
                prefix = '!(' if not condition_was_inverted else ''
                suffix = ')' if not condition_was_inverted else ''

                result = f'while ({prefix}{condition}{suffix}) {{\n{result}\n}}'

            return result

        # Translate "READ %mask_0% AT END" statements
        match = re.match(COBOL_READ_AT_END_REGEX, seq)

        if match is not None:
            # Only return translated "AT END" clause since the empty read seems to be useless
            return self.translate(match.group('at_end'))

        # Translate "READ %mask_0% INTO %mask_1% AT END" statements
        match = re.match(COBOL_READ_INTO_AT_END_REGEX, seq)

        if match is not None:
            at_end = self.translate(match.group('at_end'))
            return f'{gen_mask_token(1)}.Set({gen_mask_token(0)}.Read());\n{at_end}'

        # Translate IDMS "OBTAIN FIRST * WITHIN *" statements
        match = re.match(COBOL_IDMS_OBTAIN_FIRST_REGEX, seq)

        if match is not None:
            self.__use_db()

            var_name = self.veil.from_relative(gen_mask_token(0))
            var_name = self.veil.unmask(var_name)
            self.last_obtained_record = var_name

            from_name_csharp = self.veil.from_relative(gen_mask_token(1))
            from_name_csharp = self.veil.unmask(from_name_csharp)
            from_name = CobolDefinition.camel_case_to_mysql(from_name_csharp)

            # If "FROM" name is unknown, use view defined in DB
            if from_name_csharp not in self.store.layout.keys() and not from_name.endswith('_view'):
                prefix = CobolDefinition.name_to_snake_case(var_name)
                suffix = rreplace(from_name, '_view', '')
                from_name = f'{prefix}_{suffix}'

            query = f'SQLQueryBuilder.Select().From("{from_name}").Limit(1)'
            return f'{var_name}.Set(Db.Query({query}));'

        # Translate IDMS "OBTAIN NEXT * WITHIN *" statements
        match = re.match(COBOL_IDMS_OBTAIN_NEXT_REGEX, seq)

        if match is not None:
            self.__use_db()

            var_name = self.veil.from_relative(gen_mask_token(0))
            var_name = self.veil.unmask(var_name)
            self.last_obtained_record = var_name

            return f'{var_name}.Set(Db.QueryNext());'

        # Translate IDMS "OBTAIN OWNER WITHIN *" statements
        match = re.match(COBOL_IDMS_OBTAIN_OWNER_REGEX, seq)

        if match is not None:
            self.__use_db()

            set_name = self.veil.from_relative(gen_mask_token(0))
            set_name = self.veil.unmask(set_name)

            table_names = split_upper(set_name)

            if len(table_names) != 2:
                raise Exception(f'Unhandled IDMS set name format in "OBTAIN OWNER WITHIN *" statement: "{seq}"')

            parent_table_name = table_names[0].lower()
            child_table_name = table_names[1].lower()
            child_table_prefix = child_table_name[:4] if len(child_table_name) > 4 else child_table_name
            join_column_name = CobolDefinition.name_to_title_case(
                f'{child_table_prefix.upper()}-{parent_table_name.upper()}'
            )

            var_name = CobolDefinition.name_to_title_case(parent_table_name)

            query = f'SQLQueryBuilder.Select("{parent_table_name}.*")' + \
                    f'.From("{parent_table_name}", "{child_table_name}")' + \
                    f'.Where($"{child_table_prefix}_{parent_table_name} = \'{{{join_column_name}.value}}\'")' + \
                    '.Limit(1)'

            return f'{var_name}.Set(Db.Query({query}));'

        # Translate IDMS "OBTAIN * WITHIN * USING *" statements
        match = re.match(COBOL_IDMS_OBTAIN_WITHIN_USING_REGEX, seq)

        if match is not None:
            self.__use_db()

            var_name = self.veil.from_relative(gen_mask_token(0))
            var_name = self.veil.unmask(var_name)
            self.last_obtained_record = var_name

            from_name = CobolDefinition.name_to_snake_case(var_name)
            from_prefix = from_name[:4] if len(from_name) > 4 else from_name

            join_column_name = self.veil.from_relative(gen_mask_token(2))
            join_column_name = self.veil.unmask(join_column_name)

            from_join_name = split_upper(join_column_name)[1].lower()

            query = f'SQLQueryBuilder.Select()' + \
                    f'.From("{from_name}")' + \
                    f'.Where($"{from_prefix}_{from_join_name} = \'{{{join_column_name}.value}}\'")' + \
                    '.Limit(1)'

            return f'{var_name}.Set(Db.Query({query}));'

        # Translate IDMS "OBTAIN CALC *" statements
        match = re.match(COBOL_IDMS_OBTAIN_CALC_REGEX, seq)

        if match is not None:
            # TODO: Translate IDMS "OBTAIN CALC *" statements
            return f'// {seq}\t// [Turring Theory] "OBTAIN CALC *" statements are currently not supported.\n'

        # Translate IDMS "DB-END-OF-SET" rogue conditions (used within "UNTIL" statements)
        match = re.match(COBOL_IDMS_DB_END_OF_SET_REGEX, seq)

        if match is not None:
            if self.last_obtained_record is None:
                log('No records were obtained before checking for DB-END-OF-SET.', level=logging.ERROR)
                return 'true'

            op = '==' if match.group('not') is None else '!='
            return f'{self.last_obtained_record} {op} null'

        # Translate IDMS "DB-END-OF-SET" IF statements
        match = re.match(COBOL_IDMS_IF_DB_END_OF_SET_REGEX, seq)

        if match is not None:
            if self.last_obtained_record is None:
                log('No records were obtained before checking for DB-END-OF-SET.', level=logging.ERROR)
                return 'if (true) {'

            op = '==' if match.group('not') is None else '!='
            return f'if ({self.last_obtained_record} {op} null) {{'

        return None

    def __use_db(self):
        """
        Add required variable to template contents for a database connection.
        """

        if not self.uses_db:
            self.uses_db = True
            summary_comment = '/// <summary>\n/// MySQL database connection instance.\n/// </summary>\n'
            host_env = 'Environment.GetEnvironmentVariable("DB_HOST")'
            user_env = 'Environment.GetEnvironmentVariable("DB_USER")'
            pass_env = 'Environment.GetEnvironmentVariable("DB_PASS")'
            db_name_env = 'Environment.GetEnvironmentVariable("DB_NAME")'
            self.template_processor.tag_content[TEMPL_MEMBER_VARS].append(
                f'{summary_comment}private DatabaseConnection Db;'
            )
            self.template_processor.tag_content[TEMPL_MEMBER_VAR_ASSIGNMENTS].append(
                'Db = new DatabaseConnection(\n\t' +
                f'host: {host_env},\n\t'
                f'user: {user_env},\n\t'
                f'password: {pass_env},\n\t'
                f'databaseName: {db_name_env}\n'
                f');'
            )

    def build_section_calls(self) -> str:
        """Build section calls for current section."""

        section_calls = list(map(lambda p: f'{p}();', self.current_section_paragraphs))
        return '\n'.join(section_calls)
