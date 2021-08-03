import re

from theory.lvps.base_itl import ITL
from theory.lvps.base_itl_constants import MASK_TOKEN_REGEX_STR
from theory.languages.cpp.constants import CPP_IGNORED_SEQS, CPP_IMPORT_REGEX, CPP_NS_REGEX, CPP_USING_NS_REGEX


class CPP17ToNodeJS14ITL(ITL):
    """ITL for C++17 to Node.js 14."""

    def translate(self, seq: str, indent: int = 0):
        # Standard language translation
        translated = self.translate_std_to_nodejs(seq)

        if translated is not None:
            return translated

        # C++-specific translation
        # Ignores
        for ignored in CPP_IGNORED_SEQS:
            if seq.startswith(ignored):
                return ''

        # Imports
        match = re.match(CPP_IMPORT_REGEX, seq)

        if match is not None:
            name = match.group('name')

            # If masked, strip quotes from source token
            if re.match(MASK_TOKEN_REGEX_STR, name):
                self.veil.tokens[name] = self.veil.tokens[name].strip('"')

            return f'require("{name}");'

        # Namespaces
        match = re.match(CPP_NS_REGEX, seq)

        if match is not None:
            return f'// {seq}'

        # "using namespace" sequences
        match = re.match(CPP_USING_NS_REGEX, seq)

        if match is not None:
            return f'// {seq}'

        return None
