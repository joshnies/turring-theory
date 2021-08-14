import re
from typing import List
from benedict import benedict

from .languages.base_preprocessor import Preprocessor
from .languages.cobol.preprocessor import CobolPreprocessor
from .languages.cpp.preprocessor import CppPreprocessor
from .languages.java.preprocessor import JavaPreprocessor
from .lvp import LVP
from theory.lvps.base_itl_constants import MASK_TOKEN_REGEX_STR
from .utils import match_to_str, replace_str_range, offset_range_tuple, gen_mask_token

MASK_TOKEN_REGEX = re.compile(MASK_TOKEN_REGEX_STR)
RELATIVE_REPLACEMENT_TOKEN = '<rel_repl>'


class Veil:
    """
    Theory preprocessor.
    Masks, transforms, and unmasks file contents.
    """

    def __init__(self, lvp: LVP):
        """
        :param lvp: LVP.
        """

        self.lvp = lvp
        self.preprocessor = self.__get_preprocessor(lvp)
        self.tokens = benedict()
        self.current_relative_tokens = list()

    def reset(self):
        """Reset state."""

        self.tokens = benedict()
        self.current_relative_tokens = list()

    def mask(self, file_path: str = None, text: str = None, request_data=None) -> List[str]:
        """
        Mask file contents or text.

        `file_path` or `text` must be specified.

        :param file_path: Path of file to mask.
        :param text: Text to mask.
        :param request_data: Request body data from "translate" API endpoint.
        :returns: List of masked lines.
        """

        if file_path is not None:
            # Read file
            with open(file_path) as file:
                file_contents = file.read()
        elif text is not None:
            file_contents = text
        else:
            raise Exception(
                '`file_path` or `text` arg is required for `Veil.mask`.')

        processed = list()

        # Preprocess file contents to prepare for line-by-line masking.
        # This may include masking as well, depending on the source language.
        file_contents = self.preprocessor.preprocess(
            file_contents, request_data)

        # Mask individual lines
        for line in file_contents.splitlines():
            stripped_line = line.strip()

            # Skip ignored and empty lines
            if not self.preprocessor.should_mask_seq(stripped_line) or stripped_line == '':
                processed.append(line)
                continue

            # Split line
            processed_line = line
            offset = 0
            split = [(match_to_str(m), m.span())
                     for m in re.finditer(self.preprocessor.line_split_regex, line)]

            for s_tuple in split:
                s = s_tuple[0].strip()
                s_span = s_tuple[1]

                # Skip empty strings
                if s == '':
                    continue

                # Mask all tokens except:
                #   - Reserved tokens for the LVP
                #   - Existing mask tokens
                #   - Preprocessor tags
                #   - Tokens blacklisted by preprocessor
                if s not in self.preprocessor.reserved_tokens and \
                        re.match(MASK_TOKEN_REGEX, s) is None and \
                        s not in self.preprocessor.tags and \
                        self.preprocessor.should_mask_token(s):
                    # Skip reserved tokens based on regex
                    skip = False

                    for regex in self.preprocessor.reserved_token_regexes:
                        if re.match(regex, s) is not None:
                            skip = True
                            break

                    if skip:
                        continue

                    # Mask out source token
                    mask_token = self.gen_next_mask_token()

                    if s in self.tokens.values():
                        for k, v in self.tokens.items():
                            if v == s:
                                mask_token = k
                                break

                    processed_line = replace_str_range(
                        processed_line, mask_token, offset_range_tuple(s_span, offset))

                    # Update offset
                    offset = len(processed_line) - len(line)

                    # Save source token
                    self.save_mask_token(mask_token, s)

            processed.append(processed_line)

        return processed

    def unmask(self, text: str) -> str:
        """
        Unmask text.
        Replaces mask tokens with source tokens in reverse order to cover any recursive masking that may hav
        incorrectly occurred.

        :param text: Text to unmask.
        :returns: Unmasked text.
        """

        unmasked_text = text

        for t in reversed(list(self.tokens.keys())):
            unmasked_text = unmasked_text.replace(t, self.tokens[t])

        return unmasked_text

    def to_relative(self, text: str) -> str:
        """
        Extract mask tokens and replace with relative indices.

        :param text: Masked text to convert to relative form.
        :returns: Relative masked text.
        """

        relative_text = text

        # Reset current relative tokens state
        self.current_relative_tokens = list()

        match_count = len(re.findall(MASK_TOKEN_REGEX, relative_text))

        for i in range(match_count):
            # Get regex match
            all_matches = list(re.finditer(MASK_TOKEN_REGEX, relative_text))
            match = all_matches[i]

            # Relative mask token
            m_str = match_to_str(match)
            relative_mask_token = gen_mask_token(i)
            self.current_relative_tokens.append(m_str)

            # Replace global mask token with relative version
            relative_text = replace_str_range(
                relative_text, relative_mask_token, match.span())

        return relative_text

    def from_relative(self, text: str) -> str:
        """
        Replace relative mask tokens with corresponding global mask tokens.

        :param text: Masked text to convert to global form.
        :returns: Global masked text.
        """

        # Skip if no relative mask tokens
        if len(self.current_relative_tokens) == 0:
            return text

        global_text = text

        for i, m in enumerate(re.finditer(MASK_TOKEN_REGEX, text)):
            m_str = match_to_str(m)
            index = int(m_str[6:-1])

            if index >= len(self.current_relative_tokens) or len(self.current_relative_tokens) == 0:
                raise Exception(
                    'Too many relative mask tokens found during replacement.')

            replace_with = self.current_relative_tokens[index]

            # Replace global mask tokens with relative versions, prefixed with temporary token to prevent overrides
            # during replacement
            global_text = global_text.replace(
                m_str, replace_with[:1] +
                RELATIVE_REPLACEMENT_TOKEN + replace_with[1:], 1
            )

        # Remove relative replacement tokens
        global_text = re.sub(RELATIVE_REPLACEMENT_TOKEN, '', global_text)

        return global_text

    @staticmethod
    def offset(seq: str, offset: int) -> str:
        """
        Offset a sequence's mask token indices.

        :param seq: Masked sequence.
        :param offset: Amount to offset each mask index by.
        :returns: Masked sequence with offset mask tokens.
        """

        result = seq

        # Get mask token count
        match_count = len(re.findall(MASK_TOKEN_REGEX, result))
        regex = re.compile(r'%mask_(?P<idx>\d+)%')

        for i in range(match_count):
            # Get regex match
            all_matches = list(re.finditer(regex, result))
            match = all_matches[i]

            # Offset mask token
            idx = int(match.group('idx'))
            offset_mask_token = f'%mask_{idx + offset}%'

            # Replace global mask token with relative version
            result = replace_str_range(result, offset_mask_token, match.span())

        return result

    def gen_next_mask_token(self) -> str:
        """
        Generate next mask token based on current tokens state.

        :returns: Mask token.
        """

        return gen_mask_token(len(self.tokens.keys()))

    def save_mask_token(self, mask_token: str, source_token: str, process_source_token: bool = True):
        """
        Save mask token to state.

        :param mask_token: Mask token.
        :param source_token: Source token that the mask token replaces.
        :param process_source_token: Whether the source token should be processed before saving.
        """

        if process_source_token:
            saved_token = self.preprocessor.process_src_token(source_token)
        else:
            saved_token = source_token

        self.tokens[mask_token] = saved_token

    def __get_preprocessor(self, lvp: LVP) -> Preprocessor:
        """
        Get preprocessor for an LVP's source language.

        :param lvp: LVP.
        :returns: Preprocessor for LVP source language.
        """

        if lvp == LVP.CPP_17_TO_NODEJS_14:
            return CppPreprocessor(self.gen_next_mask_token, self.save_mask_token)
        elif lvp == LVP.JAVA_14_TO_NODEJS_14:
            return JavaPreprocessor(self.gen_next_mask_token, self.save_mask_token)
        elif lvp == LVP.COBOL_TO_CSHARP_9:
            return CobolPreprocessor(self.gen_next_mask_token, self.save_mask_token)

        raise Exception(f'No preprocessor found for LVP "{lvp.value}".')
