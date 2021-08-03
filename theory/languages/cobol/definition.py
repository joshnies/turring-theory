import logging
import re
from uuid import uuid4
import boto3

from api.config import AWS_STORAGE_BUCKET_NAME, DEBUG
from cli import log
from theory.languages.base_lang_def import LanguageDefinition
from theory.languages.cobol.constants import COBOL_COPY_REGEX, COBOL_FORMAT_IF_ENDS_REGEX, COBOL_NAME_SPLIT_REGEX, \
    COBOL_FORMAT_MULTILINE_REGEXES, COBOL_THEN_REMOVAL_REGEX, COBOL_FORMAT_PIC_COMMA_RM_REGEX, SCOPE_CLOSE_TOKEN, \
    COBOL_FORMAT_IF_REGEX, COBOL_FORMAT_RM_RECORDING_MODE_REGEX, COBOL_FORMAT_RM_BLOCK_CONTAINS_REGEX, \
    COBOL_FORMAT_RM_RECORD_CONTAINS_REGEX, COBOL_FORMAT_RM_LABEL_REGEX, COBOL_FORMAT_RM_REGEXES, \
    COBOL_FORMAT_DISPLAY_REGEX, COBOL_IGNORED_COPYBOOKS, COBOL_FORMAT_RM_COMMENTS_REGEX
from theory.utils import match_to_str, rreplace


class CobolDefinition(LanguageDefinition):
    """COBOL language definition."""

    @staticmethod
    def format_file(file_path: str, request_data=None):
        # Read file
        result = open(file_path).read()

        # Remove line numbers and inject copybooks
        result = CobolDefinition.__format_loop(result, request_data)

        # Remove unnecessary syntax
        result = CobolDefinition.__rm_general(result)
        result = CobolDefinition.__rm_comments(result)
        result = CobolDefinition.__rm_positive_signs(result)
        result = CobolDefinition.__rm_pointers(result)
        result = CobolDefinition.__rm_comp_keywords(result)
        result = CobolDefinition.__rm_upon_console(result)
        result = CobolDefinition.__rm_file_attributes(result)
        result = CobolDefinition.__rm_upon(result)
        result = CobolDefinition.__sub_comparison_ops(result)

        # Format statements
        result = CobolDefinition.__format_multiline_strings(result)
        result = CobolDefinition.__format_column_dashes(result)
        result = CobolDefinition.__format_multilines(result)
        result = CobolDefinition.__format_if(result)
        result = CobolDefinition.__format_display(result)
        result = CobolDefinition.__close_if_scopes(result)
        result = CobolDefinition.__add_filler_indices(result)

        # Remove commas in "PIC" statements
        result = CobolDefinition.__rm_pic_commas(result)

        # Remove dot syntax
        result = CobolDefinition.__rm_dots(result)

        # Remove "THEN" keywords
        result = CobolDefinition.__rm_then_keywords(result)

        # Write result to file
        open(file_path, 'w').write(result)

        return result.splitlines()

    @staticmethod
    def to_single_line_comment(text: str) -> str:
        return f'* {text}'

    @staticmethod
    def to_multi_line_comment(text: str) -> str:
        return CobolDefinition.to_single_line_comment(text)

    @staticmethod
    def name_to_camel_case(name: str) -> str:
        """
        Convert a COBOL or IDMS entity name to camelCase.

        :param name: Name.
        :return: Name formatted in camelCase.
        """

        s = name.lower().split('-')

        if len(name) == 0:
            return name

        return s[0] + ''.join(i.capitalize() for i in s[1:])

    @staticmethod
    def name_to_snake_case(name: str) -> str:
        """
        Convert a COBOL or IDMS entity name to snake_case.

        :param name: Name.
        :return: Name formatted in snake_case.
        """

        # From COBOL entity
        if '-' in name or name.isupper():
            return name.strip().lower().replace('-', '_')

        # From camelCase
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name.strip()).lower()

    @staticmethod
    def name_to_title_case(name: str, escape_first_numeric: bool = True) -> str:
        """
        Convert a COBOL or IDMS entity name to TitleCase.

        :param name: Name.
        :param escape_first_numeric: Whether to add an "_" as a prefix when the name begins with a number.
        :return: Name formatted in TitleCase.
        """

        text_stripped = name.strip()

        # Skip empty strings and '-'
        if text_stripped == '' or text_stripped == '-':
            return text_stripped

        res = ''
        text_split = re.split(COBOL_NAME_SPLIT_REGEX, text_stripped)

        if len(text_split) > 1:
            # Convert to title case
            for word in text_split:
                res += word.title()
        else:
            res = re.sub(COBOL_NAME_SPLIT_REGEX, '', text_stripped).title()

        # Prefix with an underscore if name starts with a number
        if escape_first_numeric and len(res) > 0 and res[0].isdigit():
            res = '_' + res

        return res

    @staticmethod
    def camel_case_to_mysql(name: str) -> str:
        """
        Convert a camelCase COBOL or IDMS entity name to the MySQL equivalent.

        :param name: Source name.
        :return: MySQL name.
        """

        view_name = name

        # Convert to MySQL view name
        idx_prefix = 'Ix'
        if view_name.startswith(idx_prefix):
            view_name = view_name.replace(idx_prefix, '', 1)
            return CobolDefinition.name_to_snake_case(view_name) + '_view'

        return CobolDefinition.name_to_snake_case(view_name)

    @staticmethod
    def __format_loop(file_contents: str, request_data=None):
        # Remove line numbers
        result = CobolDefinition.__remove_line_numbers(file_contents)

        # Inject copybooks
        return CobolDefinition.__inject_copybooks(result, request_data)

    @staticmethod
    def __remove_line_numbers(file_contents: str) -> str:
        """
        Remove line numbers (characters 1-6) and all characters past character 72.

        :param file_contents: File contents.
        :returns: New file contents
        """

        spaces = ' ' * 6
        result = ''

        for line in file_contents.splitlines():
            new_line = spaces + line[6:72].rstrip()
            result += new_line + '\n'

        return result

    @staticmethod
    def __inject_copybooks(file_contents: str, request_data=None) -> str:
        """
        Inject copybooks into main source contents via COBOL's "COPY" syntax.

        :param file_contents: File contents.
        :param request_data: Request body data from "/translate" API endpoint.
        :returns: New file contents.
        """

        new_file_contents = ''
        copybook_ext_key = 'cobol_copybook_ext'
        copybook_ext = '' if request_data[copybook_ext_key] is None else f'.{request_data[copybook_ext_key]}'

        for src_line in file_contents.splitlines():
            line = src_line.strip()

            # Translate "COPY" statements
            match = re.match(COBOL_COPY_REGEX, line)

            if match is None:
                # Append original source line
                new_file_contents += src_line + '\n'
            else:
                request_data_key = 'cobol_default_copybooks_path'

                # Comment out if no request data given
                if request_data is None or request_data[request_data_key] is None:
                    new_file_contents += ' ' * 6 + f'* [Turring Theory] ERROR: No default copybooks path given.\n* {line}\n'
                    continue

                name = match.group('name')

                # Skip ignore copybooks
                if name in COBOL_IGNORED_COPYBOOKS:
                    continue

                replaced_old = match.group('old')
                replaced_new = match.group('new')
                copybooks_path = request_data[request_data_key].strip('/')

                try:
                    # Download matching file from S3
                    remote_path = f'inputs/{copybooks_path}/{name}{copybook_ext}'
                    local_path = f'temp/inputs/{str(uuid4())}'

                    try:
                        s3 = boto3.resource('s3')
                        s3.Bucket(AWS_STORAGE_BUCKET_NAME).download_file(remote_path, local_path)
                    except Exception as e:
                        if DEBUG:
                            log(e, level=logging.ERROR)

                        log(f'Failed to download COBOL copybook file "{remote_path}" from S3.', level=logging.ERROR)

                    # Format local file
                    copybook = open(local_path).read()
                    copybook = CobolDefinition.__format_loop(copybook, request_data)

                    # Replace text if specified
                    if replaced_old is not None and replaced_new is not None:
                        copybook = copybook.replace(replaced_old, replaced_new)

                    # Append copybook to new file contents
                    new_file_contents += copybook + '\n'
                except:
                    pass

        return new_file_contents

    @staticmethod
    def __format_multiline_strings(file_contents: str) -> str:
        """
        Format multi-line strings by adding single quotes to end of lines.

        :param file_contents: File contents.
        :returns: New file contents.
        """

        result_lines = list()

        for line in file_contents.splitlines():
            line_stripped = line.strip()

            if re.match(re.compile(r'^(?:DISPLAY\s+)?\'[^\']+$'), line_stripped) is not None:
                result_lines.append(f"{line}'")
            else:
                result_lines.append(line)

        return '\n'.join(result_lines)

    @staticmethod
    def __format_column_dashes(file_contents: str) -> str:
        """
        Merge multiline statements into single line based on column 7 dash character.

        :param file_contents: File contents.
        :returns: New file contents.
        """

        result_lines = list()

        for line in file_contents.splitlines():
            if line.startswith(' ' * 6 + '-'):
                result_lines[-1] += f' {line[7:]}'
            else:
                result_lines.append(line)

        return '\n'.join(result_lines)

    @staticmethod
    def __format_multilines(file_contents: str) -> str:
        """
        Format multi-line statements into single-line.

        :param file_contents: File contents.
        :returns: New file contents.
        """

        new_file_contents = file_contents

        for regex in COBOL_FORMAT_MULTILINE_REGEXES:
            for match in re.finditer(regex, file_contents):
                match_str = match_to_str(match)
                new_str = match_str.replace('\n', ' ')
                new_file_contents = new_file_contents.replace(match_str, new_str)

        return new_file_contents

    @staticmethod
    def __format_if(file_contents: str) -> str:
        """
        Format "IF" statements into single-line.

        :param file_contents: File contents.
        :returns: New file contents.
        """

        new_file_contents = file_contents

        for match in re.finditer(COBOL_FORMAT_IF_REGEX, new_file_contents):
            match_str = match_to_str(match)
            new_str = match_str

            # Remove outer parentheses
            new_str = new_str.replace('(', '', 1)
            new_str = rreplace(new_str, ')', '', 1)

            # Replace newlines with spaces
            new_str = new_str.replace('\n', ' ')

            # Replace match string with formatted string
            new_file_contents = new_file_contents.replace(match_str, new_str)

        return new_file_contents

    @staticmethod
    def __format_display(file_contents: str) -> str:
        """
        Format "DISPLAY" statements into single-line.

        :param file_contents: File contents.
        :returns: New file contents.
        """

        new_file_contents = file_contents

        for match in re.finditer(COBOL_FORMAT_DISPLAY_REGEX, file_contents):
            match_str = match_to_str(match)

            # Skip "DISPLAY" statements within "IF-ELSE" blocks
            if re.search(re.compile(r'\s+ELSE\s+'), match_str) is not None:
                continue

            new_str = match_str.replace('\n', ' ')
            new_file_contents = new_file_contents.replace(match_str, new_str)

        return new_file_contents

    @staticmethod
    def __close_if_scopes(file_contents: str) -> str:
        """
        Close scopes for "IF" statements.

        :param file_contents: File contents.
        :returns: New file contents.
        """

        new_file_contents = file_contents
        match = re.search(COBOL_FORMAT_IF_ENDS_REGEX, new_file_contents)

        while match is not None:
            match_str = match_to_str(match)

            # Generate end tokens
            next_sentence_count = len(re.findall(r'NEXT\s+SENTENCE(?!\.)(?!\s+ELSE)', match_str))
            if_count = max(match_str.count('IF') - match_str.count('END-IF') - next_sentence_count, 0)
            end_tokens = f'\n{SCOPE_CLOSE_TOKEN}' * if_count
            end_tokens += '\n'

            # Append end tokens
            match_end = match.end()
            new_file_contents = new_file_contents[:match_end] + end_tokens + new_file_contents[match_end:]

            # Get next match
            match = re.search(COBOL_FORMAT_IF_ENDS_REGEX, new_file_contents)

        return new_file_contents

    @staticmethod
    def __rm_general(file_contents: str) -> str:
        """
        Remove any statements or keywords that can be replaced with an empty string.

        :param file_contents: File contents.
        :return: New file contents.
        """

        new_file_contents = file_contents

        for regex in COBOL_FORMAT_RM_REGEXES:
            for match in re.finditer(regex, file_contents):
                match_str = match_to_str(match)
                new_file_contents = new_file_contents.replace(match_str, '')

        return new_file_contents

    @staticmethod
    def __rm_comments(file_contents: str) -> str:
        """
        Remove comments.

        :param file_contents: File contents.
        :return: New file contents.
        """

        new_file_contents = list(
            filter(
                lambda l: re.match(COBOL_FORMAT_RM_COMMENTS_REGEX, l.strip()) is None,
                file_contents.splitlines()
            )
        )

        return '\n'.join(new_file_contents)

    @staticmethod
    def __rm_pic_commas(file_contents: str) -> str:
        """
        Remove commas from "PIC" statements.

        :param file_contents: File contents.
        :return: New file contents.
        """

        new_file_contents = file_contents

        for match in re.finditer(COBOL_FORMAT_PIC_COMMA_RM_REGEX, file_contents):
            match_str = match_to_str(match)
            new_str = match_str.replace(',', '')
            new_file_contents = new_file_contents.replace(match_str, new_str)

        return new_file_contents

    @staticmethod
    def __rm_dots(file_contents: str) -> str:
        """
        Remove "." line delineators.

        :param file_contents: File contents.
        :return: New file contents.
        """

        result_lines = list()

        for l in file_contents.splitlines():
            # Remove right whitespace and "." chars
            line = l.rstrip().rstrip('.')
            result_lines.append(line)

        return '\n'.join(result_lines)

    @staticmethod
    def __rm_then_keywords(file_contents: str) -> str:
        """
        Remove "THEN" keywords for "IF" statements to align with COBOL datasets.

        :param file_contents: File contents.
        :return: New file contents.
        """

        result_lines = list()

        for line in file_contents.splitlines():
            match = re.match(COBOL_THEN_REMOVAL_REGEX, line)

            if match is None:
                result_lines.append(line)
                continue

            then_span = match.span('then')
            result_lines.append(line[:then_span[0]])

        return '\n'.join(result_lines)

    @staticmethod
    def __rm_positive_signs(file_contents: str) -> str:
        """
        Remove positive numeric signs (+).

        :param file_contents: File contents.
        :return: New file contents.
        """

        new_file_contents = file_contents
        new_file_contents = re.sub(r'VALUE\s+\+', 'VALUE ', new_file_contents)
        new_file_contents = re.sub(r'MOVE\s+\+', 'MOVE ', new_file_contents)
        new_file_contents = re.sub(r'THRU\s+\+', 'THRU ', new_file_contents)
        new_file_contents = re.sub(r'ADD\s+\+', 'ADD ', new_file_contents)
        new_file_contents = re.sub(r'SUBTRACT\s+\+', 'SUBTRACT ', new_file_contents)
        new_file_contents = re.sub(r'MULTIPLY\s+\+', 'MULTIPLY ', new_file_contents)
        new_file_contents = re.sub(r'DIVIDE\s+\+', 'DIVIDE ', new_file_contents)
        new_file_contents = re.sub(r'BY\s+\+', 'BY ', new_file_contents)
        new_file_contents = re.sub(r'INTO\s+\+', 'INTO ', new_file_contents)
        new_file_contents = re.sub(r'FROM\s+\+', 'FROM ', new_file_contents)

        return new_file_contents

    @staticmethod
    def __rm_pointers(file_contents: str) -> str:
        """
        Remove "POINTER" keywords.

        :param file_contents: File contents.
        :return: New file contents.
        """

        result_lines = list()

        for l in file_contents.splitlines():
            line = re.sub(r'\s*POINTER\s*', ' ', l)
            result_lines.append(line)

        return '\n'.join(result_lines)

    @staticmethod
    def __rm_comp_keywords(file_contents: str) -> str:
        """
        Remove "COMP-*" keywords.

        :param file_contents: File contents.
        :return: New file contents.
        """

        result_lines = list()

        for l in file_contents.splitlines():
            line = re.sub(r'\s+COMP(?:-\d+)?\s+', ' ', l)
            result_lines.append(line)

        return '\n'.join(result_lines)

    @staticmethod
    def __rm_upon_console(file_contents: str) -> str:
        """
        Remove "UPON CONSOLE" keyword pairs.

        :param file_contents: File contents.
        :return: New file contents.
        """

        return re.sub(r'\s+UPON\s+CONSOLE\s+', ' ', file_contents)

    @staticmethod
    def __rm_file_attributes(file_contents: str) -> str:
        """
        Remove file attribute clauses.

        :param file_contents: File contents.
        :returns: New file contents.
        """

        result = re.sub(COBOL_FORMAT_RM_RECORDING_MODE_REGEX, ' ', file_contents)
        result = re.sub(COBOL_FORMAT_RM_BLOCK_CONTAINS_REGEX, ' ', result)
        result = re.sub(COBOL_FORMAT_RM_RECORD_CONTAINS_REGEX, ' ', result)
        result = re.sub(COBOL_FORMAT_RM_LABEL_REGEX, ' ', result)

        return result

    @staticmethod
    def __rm_upon(file_contents: str) -> str:
        """
        Remove "UPON" clauses.

        :param file_contents: File contents.
        :returns: New file contents.
        """

        regex = re.compile(r'\s+UPON\s+CONSOLE')
        return re.sub(regex, ' ', file_contents)

    @staticmethod
    def __sub_comparison_ops(file_contents: str) -> str:
        """
        Substitute comparison operators with common keyword/token.

        :param file_contents: File contents.
        :returns: New file contents.
        """

        return re.sub(r'(?:IS\s+)?EQUALS?(?:\s+TO)?', '=', file_contents)

    @staticmethod
    def __add_filler_indices(file_contents: str) -> str:
        result_lines = list()
        idx = 0

        for l in file_contents.splitlines():
            line = re.sub(r'\s+FILLER\s+', f' FILLER-{idx} ', l)
            result_lines.append(line)

            if l != line:
                idx += 1

        return '\n'.join(result_lines)
