import re

from .constants import SECTION_CALLS_TAG
from .itl import COBOLToCSharp9ITL
from ..base_postprocessor import Postprocessor
from ...languages.csharp.constants import CSHARP_USELESS_METHOD_REGEX
from ...utils import match_to_str


class COBOLToCSharp9Postprocessor(Postprocessor):
    """COBOL to C# 9 post-processor."""

    def __init__(self, itl: COBOLToCSharp9ITL):
        self.itl = itl

    def postprocess_file(self, file_contents: str) -> str:
        # Inject final section calls
        result = file_contents.replace(SECTION_CALLS_TAG, self.itl.build_section_calls())

        # Remove useless methods
        result = self.__remove_useless_methods(result)

        return result

    @staticmethod
    def __remove_useless_methods(file_contents: str) -> str:
        """
        Remove useless methods and their references.

        :param file_contents: File contents.
        :returns: New file contents.
        """

        new_file_contents = file_contents
        match = re.search(CSHARP_USELESS_METHOD_REGEX, new_file_contents)

        while match is not None:
            match_str = match_to_str(match)
            name = match.group('name')

            # Replace method and references
            new_file_contents = new_file_contents.replace(match_str, '').replace(f'{name}();\n', '')

            # Get next match
            match = re.search(CSHARP_USELESS_METHOD_REGEX, new_file_contents)

        return new_file_contents
