import re

from theory.languages.cobol.constants import COBOL_EXEC_BLOCK_REGEX, COBOL_LENGTH_OF_REGEX, \
    COBOL_ISOLATED_KEYWORD_NEWLINE_REGEX, COBOL_ISOLATED_KEYWORD_DOT_REGEX, COBOL_ISOLATED_KEYWORD_SPACE_REGEX, \
    COBOL_RETURN_AT_END_REGEX, COBOL_REPL_FILE_DATA_REFS_REGEX, COBOL_GLOBAL_FILE_DATA_REGEX
from theory.languages.cobol.definition import CobolDefinition
from theory.lvps.base_mtl import MTL
from theory.utils import match_to_str


class COBOLToCSharp9MTL(MTL):
    """COBOL to C# 9 MTL."""

    def translate_all(self, file_contents: str) -> str:
        result = self.__rm_isolated_keywords(file_contents)
        result = self.__translate_length_of(result)
        result = self.__translate_return(result)
        result = self.__fix_file_data_refs(result)
        return self.__comment_exec_blocks(result)

    @staticmethod
    def __rm_isolated_keywords(file_contents: str) -> str:
        """
        Remove isolated keywords (those that don't rely on any context).

        :param file_contents: File contents.
        :returns: New file contents.
        """

        result = re.sub(COBOL_ISOLATED_KEYWORD_NEWLINE_REGEX, '\n', file_contents)
        result = re.sub(COBOL_ISOLATED_KEYWORD_SPACE_REGEX, ' ', result)
        return re.sub(COBOL_ISOLATED_KEYWORD_DOT_REGEX, '.', result)

    def __comment_exec_blocks(self, file_contents: str) -> str:
        """
        Comment-out "EXEC" blocks.

        :param file_contents: File contents.
        :returns: New file contents.
        """

        new_file_contents = file_contents

        # Find matches
        for match in re.finditer(COBOL_EXEC_BLOCK_REGEX, file_contents):
            match_str = match_to_str(match)

            # Unmask to remove any mask tokens
            match_str_unmasked = self.veil.unmask(match_str)

            # Comment-out block for target and save result as source token in Veil
            mask_token = self.veil.gen_next_mask_token()
            self.veil.save_mask_token(mask_token, f'/*\n{match_str_unmasked}\n*/', process_source_token=False)
            new_file_contents = new_file_contents.replace(match_str, mask_token)

        return new_file_contents

    def __translate_length_of(self, file_contents: str) -> str:
        """
        Translate "LENGTH OF" syntax.

        :param file_contents: File contents.
        :returns: New file contents.
        """

        new_file_contents = file_contents

        for match in re.finditer(COBOL_LENGTH_OF_REGEX, new_file_contents):
            match_str = match_to_str(match)
            var_name = match.group('var_name')
            var_name = CobolDefinition.name_to_title_case(var_name)

            # Comment-out block for target and save result as source token in Veil
            mask_token = self.veil.gen_next_mask_token()
            self.veil.save_mask_token(mask_token, f'{var_name}.Length', process_source_token=False)
            new_file_contents = new_file_contents.replace(match_str, mask_token)

        return new_file_contents

    def __translate_return(self, file_contents: str) -> str:
        """
        Translate "RETURN" statements.

        :param file_contents: File contents.
        :returns: New file contents.
        """

        new_file_contents = file_contents

        for match in re.finditer(COBOL_RETURN_AT_END_REGEX, new_file_contents):
            # Replace "RETURN *" statement with only the "AT END" clause
            match_str = match_to_str(match)
            at_end = match.group('at_end').strip()
            new_file_contents = new_file_contents.replace(match_str, at_end)

        return new_file_contents

    def __fix_file_data_refs(self, file_contents: str) -> str:
        """
        Fix file data references in "WRITE" statements.

        :param file_contents: File contents.
        :returns: New file contents.
        """

        new_file_contents = file_contents
        file_data_map = dict()

        # Build file data map
        for match in re.finditer(COBOL_GLOBAL_FILE_DATA_REGEX, new_file_contents):
            data_name_mask_token = match.group('data_name')

            if data_name_mask_token is None:
                continue

            data_name = self.veil.tokens[data_name_mask_token]
            file_name_mask_token = match.group('file_name')
            file_data_map[data_name] = file_name_mask_token

        # Replace references of data variable while writing with file variable name
        for match in re.finditer(COBOL_REPL_FILE_DATA_REFS_REGEX, new_file_contents):
            match_str = match_to_str(match)
            write_to_mask_token = match.group('write_to')
            write_to = self.veil.tokens[write_to_mask_token]

            if write_to in file_data_map.keys():
                new_str = match_str.replace(write_to_mask_token, file_data_map[write_to])
                new_file_contents = new_file_contents.replace(match_str, new_str)

        return new_file_contents
