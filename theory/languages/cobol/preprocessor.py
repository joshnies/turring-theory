import re

from .constants import COBOL_RESERVED_TOKENS, COBOL_PROGRAM_ID_REGEX, COBOL_AUTHOR_REGEX, COBOL_DATE_WRITTEN_REGEX, \
    SCOPE_CLOSE_TOKEN, COBOL_RESERVED_NUMERIC_REGEXES
from .definition import CobolDefinition
from ..std.constants import STD_STR_REGEX, STD_MASKED_STR_REGEX
from ..std.preprocessor import Preprocessor
from ...utils import replace_str_range, offset_range_tuple


class CobolPreprocessor(Preprocessor):
    """COBOL preprocessor."""

    def __init__(self, gen_next_mask_token, save_mask_token):
        super().__init__(gen_next_mask_token, save_mask_token)

        # Define line split regex for Veil
        self.line_split_regex = re.compile(r'[^\s|<|>|\(|\)|{|}|\[|\]|\+|-|\/|\*|^|;|,|\?|.]+')

        # Define reserved tokens
        self.reserved_tokens = COBOL_RESERVED_TOKENS

    def preprocess(self, file_contents: str, request_data=None):
        result = self.__mask_string_literals(file_contents)
        result = self.__mask_numeric_values(result)
        return result

    def should_mask_seq(self, seq: str) -> bool:
        if seq.startswith('*') or \
                re.match(COBOL_PROGRAM_ID_REGEX, seq) is not None or \
                re.match(COBOL_AUTHOR_REGEX, seq) is not None or \
                re.match(COBOL_DATE_WRITTEN_REGEX, seq) is not None:
            return False

        return True

    def should_mask_token(self, token: str) -> bool:
        if re.match(STD_MASKED_STR_REGEX, token) is not None or \
                token == SCOPE_CLOSE_TOKEN:
            return False

        return True

    def process_src_token(self, src_token: str) -> str:
        if src_token.isnumeric():
            return src_token

        return CobolDefinition.name_to_title_case(src_token)

    def __mask_string_literals(self, file_contents: str) -> str:
        """
        Mask string literals.

        :param file_contents: File contents.
        :returns: Masked file contents.
        """

        new_file_contents = file_contents

        for m in re.finditer(STD_STR_REGEX, file_contents):
            group_name = 'content'
            src_str = m.group(group_name)
            mask_token = self.gen_next_mask_token()

            # Build regex for replacing string content
            replace_regex = re.compile(rf'["\']+(?P<content>{re.escape(src_str)})["\']+')
            replacement_match = re.search(replace_regex, new_file_contents)

            if replacement_match is None:
                continue

            replacement_span = replacement_match.span(group_name)

            # Replace source token (string content) with mask token
            new_file_contents = mask_token.join(
                [
                    new_file_contents[:replacement_span[0]],
                    new_file_contents[replacement_span[1]:],
                ]
            )

            # Save source token
            self.save_mask_token(mask_token, src_str)

        return new_file_contents

    def __mask_numeric_values(self, file_contents: str) -> str:
        """
        Mask numeric values that are in the reserved tokens list.

        :param file_contents: File contents.
        :returns: Masked file contents.
        """

        result_lines = file_contents.splitlines()

        for regex in COBOL_RESERVED_NUMERIC_REGEXES:
            new_lines = list()

            for line in result_lines:
                line_stripped = line.strip()
                match = re.match(regex, line_stripped)
                nl = line

                # Initialize string length difference as indent length
                # (line is already stripped of right-side whitespace in CobolDefinition.format())
                diff = len(line) - len(line_stripped)

                if match is not None:
                    for group_name, val_str in match.groupdict().items():
                        if val_str is None or re.match(re.compile(r'^9+$'), val_str) is None:
                            continue

                        val_span = match.span(group_name)
                        mask_token = self.gen_next_mask_token()

                        # Mask value
                        nl = replace_str_range(nl, mask_token, offset_range_tuple(val_span, diff))
                        self.save_mask_token(mask_token, val_str)

                        # Update string length difference
                        diff = len(line) - len(nl)

                new_lines.append(nl)
            result_lines = new_lines
        return '\n'.join(result_lines)
