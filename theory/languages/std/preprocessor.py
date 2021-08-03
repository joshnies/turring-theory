import logging
from typing import List, Tuple, Optional

from cli import log
from theory.utils import match_to_str, replace_str_range, offset_range_tuple
from .constants import *
from ..base_preprocessor import Preprocessor
from ...utils import to_special_token


class StandardPreprocessor(Preprocessor):
    """Base preprocessor for standard languages."""

    def __init__(self, gen_next_mask_token, save_mask_token):
        super().__init__(gen_next_mask_token, save_mask_token)

        # Define line split regex for Veil
        self.line_split_regex = re.compile(r'[^\s|<|>|\(|\)|{|}|\[|\]|\+|-|\/|\*|^|;|,|\?]+')

        # Define tags
        self.member_tag = to_special_token('member')

        # Add all tags to list
        self.tags = [
            self.member_tag
        ]

    def preprocess(self, file_contents: str, request_data=None):
        # Mask
        result = self.__mask_block_comments(file_contents)
        result = self.__mask_single_comments(result)
        result = self.__mask_string_literals(result)

        # Add tags
        result = self.__tag_scopes(result)

        # Separate comments
        return self.__separate_comments(result)

    def should_mask_seq(self, seq: str) -> bool:
        # Skip comments
        if seq.startswith('/*') or seq.startswith('//'):
            return False

        return True

    @staticmethod
    def find_scope(input: str, open_token: str = r'\{', close_token: str = r'\}',
                   should_include_tokens: bool = False) -> Optional[Tuple[int, int]]:
        """
        Find scope of an entity (e.g. class, function, loop structure, etc).

        NOTE: Must only be ran **after** masking all comments.

        :param input: Input text.
        :param open_token: Opening delineator token. **Must be escaped.**
        :param close_token: Closing delineator token. **Must be escaped.**
        :param should_include_tokens: Whether the delineator tokens should be included in the resulting range tuple.
        :returns: Tuple of start and end indices marking text within scope.
        """

        # Define regexes
        open_regex = re.compile(open_token)
        any_regex = re.compile(rf'{open_token}|{close_token}')

        # Get first "open" delineator match
        first_match = re.search(open_regex, input)

        if first_match is None:
            return None

        first_match_start_span = 0 if should_include_tokens else 1
        start_idx = first_match.span()[first_match_start_span]
        end_idx = -1
        count = 1
        is_first = True

        for match in re.finditer(any_regex, input):
            # Skip first match
            if is_first:
                is_first = False
                continue

            if match_to_str(match) == open_token.replace('\\', ''):
                count += 1
            else:
                count -= 1

            if count <= 0:
                match_start_span = 1 if should_include_tokens else 0
                end_idx = match.span()[match_start_span]
                break

        if end_idx <= 0:
            return None

        return start_idx, end_idx

    @staticmethod
    def find_scope_with_depth(input: str, open_token: str = r'\{', close_token: str = r'\}', depth: int = 1) \
            -> List[Tuple[int, int]]:
        """
        Find scope of an entity (e.g. class, function, loop structure, etc) at a specific depth level.

        NOTE: Must only be ran **after** masking all comments.
        NOTE: Includes opening and closing tokens in returned index tuples.

        :param input: Input text.
        :param open_token: Opening delineator token. **Must be escaped.**
        :param close_token: Closing delineator token. **Must be escaped.**
        :param depth: Specific depth level.
        :returns: Array of tuples containing the start and end indices marking text within scope (not including delineator
            tokens).
        """

        # Define regexes
        any_regex = re.compile(rf'{open_token}|{close_token}')

        current_start_idx = 0
        count = 0
        indices = list()

        for match in re.finditer(any_regex, input):
            if match_to_str(match) == open_token.replace('\\', ''):
                count += 1
            else:
                count -= 1

            if count == depth:
                # Start depth
                current_start_idx = match.span()[0]
            elif current_start_idx != -1:
                # End depth
                indices.append((current_start_idx, match.span()[1]))
                current_start_idx = -1

            if count <= 0:
                break

        return indices

    def __mask_block_comments(self, file_contents: str) -> str:
        """
        Mask block comments.

        :param file_contents: File contents.
        :returns: Masked file contents.
        """

        m = re.search(STD_BLOCK_COMMENT_REGEX, file_contents)

        while m is not None:
            match_span = m.span()
            span = m.span(STD_COMMENT_REGEX_GROUP)
            src_str = m.group(STD_COMMENT_REGEX_GROUP)
            mask_token = self.gen_next_mask_token()

            # Mask out source token
            new_file_contents = mask_token.join([file_contents[:span[0]], file_contents[span[1]:]])

            # Add empty newlines to retain line count
            len_diff = len(file_contents) - len(new_file_contents)
            line_count_diff = len(file_contents.splitlines()) - len(new_file_contents.splitlines())

            if line_count_diff > 0:
                added_nl = '\n' * line_count_diff
                new_span_end = match_span[1] - len_diff
                file_contents = new_file_contents[:new_span_end] + added_nl + new_file_contents[new_span_end:]
            else:
                file_contents = new_file_contents

            # Save source token
            self.save_mask_token(mask_token, src_str)

            # Find next match (if any)
            m = re.search(STD_BLOCK_COMMENT_REGEX, file_contents)

        return file_contents

    def __mask_single_comments(self, file_contents: str) -> str:
        """
        Mask single-line comments.

        :param file_contents: File contents.
        :returns: Masked file contents.
        """

        regex = STD_SINGLE_COMMENT_REGEX
        masked_contents = file_contents
        total = len(re.findall(regex, masked_contents))
        itr_idx = 0

        while itr_idx < total:
            # Get match
            match = list(re.finditer(regex, masked_contents))[itr_idx]

            # Increment iteratee index
            itr_idx += 1

            # Get match content group span
            group = STD_COMMENT_REGEX_GROUP
            comment_contents = match.group(group)
            comment_contents_span = match.span(group)

            # Save mask token
            mask_token = self.gen_next_mask_token()
            self.save_mask_token(mask_token, comment_contents)

            # Update masked contents
            masked_contents = replace_str_range(masked_contents, mask_token, comment_contents_span)

        return masked_contents

    def __mask_string_literals(self, file_contents: str) -> str:
        """
        Mask string literals.

        :param file_contents: File contents.
        :returns: Masked file contents.
        """

        m = re.search(STD_STR_REGEX, file_contents)

        while m is not None:
            span = m.span()
            src_str = match_to_str(m)
            mask_token = self.gen_next_mask_token()

            # Mask out source token
            new_file_contents = mask_token.join([file_contents[:span[0]], file_contents[span[1]:]])

            # Add empty newlines to retain line count
            len_diff = len(file_contents) - len(new_file_contents)
            line_count_diff = len(file_contents.splitlines()) - len(new_file_contents.splitlines())

            if line_count_diff > 0:
                added_nl = '\n' * line_count_diff
                new_span_end = span[1] - len_diff
                file_contents = new_file_contents[:new_span_end] + added_nl + new_file_contents[new_span_end:]
            else:
                file_contents = new_file_contents

            # Save source token
            self.save_mask_token(mask_token, src_str)

            # Find next match (if any)
            m = re.search(STD_STR_REGEX, file_contents)

        return file_contents

    @staticmethod
    def __separate_comments(file_contents: str) -> str:
        """
        Separates comments from lines in file contents.

        :param file_contents: File contents.
        :returns: Modified file contents.
        """

        result = file_contents
        all_matches = list(re.finditer(STD_COMMENT_SPLIT_REGEX, result))
        total = len(all_matches)
        itr_idx = 0

        while itr_idx < total:
            # Get match
            match = all_matches[itr_idx]

            # Increment iteratee index
            itr_idx += 1

            # Build split comment
            match_str = match_to_str(match)
            indentation = match.group('indent')
            other_text = match.group('other')
            comment = match.group('comment')

            if other_text.strip() == '':
                continue

            split_comment = f'{indentation}{comment}\n{indentation}{other_text}'

            # Replace in file contents
            result = result.replace(match_str, split_comment)

        return result

    def __tag_scopes(self, file_contents: str) -> str:
        """
        Add scope tags for file contents.
        This includes:
            - member variables
            - member methods

        :param file_contents: File contents.
        :return: Modified file contents.
        """

        result = file_contents

        # Iterate over all parent entity matches (e.g. class or interface).
        # This is used instead of std iterator for-loop since the file contents change, and therefore so do the spans.
        total_count = len(re.findall(STD_MEMBER_SCOPE_REGEX, result))
        itr_idx = 0

        while itr_idx < total_count:
            # Get regex parent entity match
            parent_match = list(re.finditer(STD_MEMBER_SCOPE_REGEX, result))[itr_idx]

            # Increment iteratee index
            itr_idx += 1

            # Find scope of parent entity
            parent_start_idx = parent_match.span()[0]
            parent_entity_contents = result[parent_start_idx:]
            scope = self.find_scope(parent_entity_contents, should_include_tokens=True)

            # Skip if scope not found
            if scope is None:
                log(f'Parent entity scope not found for "{match_to_str(parent_match).strip()}".', level=logging.WARNING)
                continue

            # Find scope ranges at a flat level of depth (1) to tag members
            scoped_file_contents = parent_entity_contents[scope[0]:scope[1]]
            scope_ranges = self.find_scope_with_depth(scoped_file_contents, depth=1)

            # Iterate over scope ranges
            last_range_end = 0
            new_result = ''

            for r in scope_ranges:
                # Add text before scope range to result
                new_result += scoped_file_contents[last_range_end:r[0]]

                # Get lines for scope range
                batch = scoped_file_contents[r[0]:r[1]]
                lines = batch.splitlines()
                new_lines = list()

                # Add tags
                for l in lines:
                    stripped_line = re.sub(r'public|private|protected|final|abstract|static', '', l).strip()

                    # Add member tag
                    if re.match(STD_FUNC_REGEX, stripped_line) is not None or \
                            re.match(STD_VAR_REGEX, stripped_line) is not None:
                        indentation_len = len(l) - len(l.strip())
                        indentation = " " * indentation_len
                        tagged_line = f'{indentation}{self.member_tag} {l.strip()}'
                        new_lines.append(tagged_line)
                    # No applicable tags available
                    else:
                        new_lines.append(l)

                new_result += '\n'.join(new_lines)
                last_range_end = r[1]

            # Add last remaining file contents to new result
            remaining_scoped_contents = scoped_file_contents[scope_ranges[-1][1]:]
            new_result += remaining_scoped_contents

            # Replace result substring
            replacement_range = offset_range_tuple(scope, len(result) - len(parent_entity_contents))
            result = replace_str_range(result, new_result, replacement_range)

        return result
