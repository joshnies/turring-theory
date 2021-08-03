import re

from theory.lvps.base_itl import ITL
from theory.languages.java.constants import JAVA_IGNORED_RE_SEQS, JAVA_IMPORT_REGEX, JAVA_PACKAGE_REGEX


class Java14ToPython3ITL(ITL):
    """ITL for Java 14 to Python 3."""

    def translate(self, seq: str, indent: int = 0):
        # Standard language translation
        translated = self.translate_std_to_python_3(seq)

        if translated is not None:
            return translated

        # Java-specific translation
        # Ignores
        for ignored_regex in JAVA_IGNORED_RE_SEQS:
            match = re.match(ignored_regex, seq)

            if match is not None:
                return ''

        # Imports
        match = re.match(JAVA_IMPORT_REGEX, seq)

        if match is not None:
            name = match.group('name')
            return f'# import {name}'

        # Package declarations
        match = re.match(JAVA_PACKAGE_REGEX, seq)

        if match is not None:
            return f'# {seq}'

        return None
