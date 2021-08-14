import csv
import re
from typing import Optional

from cli import log
from theory.lvps.base_store import Store
from theory.lvps.base_template_processor import TemplateProcessor
from theory.veil import Veil
from theory.lvps.base_itl_constants import STD_SEQS_TO_COPY, STANDARD_MASKED_SEQS_TO_COPY, \
    STANDARD_TO_PY_MASKED_SEQS_TO_COPY
from theory.languages.nodejs.constants import STD_TO_JS_SEQ_MAP


class ITL:
    """Base Immediate Translation Layer. A rule-based translator for simple entities."""

    def __init__(self, data_map_path: str, veil: Veil, store: Optional[Store],
                 template_processor: Optional[TemplateProcessor], translate_callback):
        """
        :param data_map_path: Data map path.
        :param veil: Veil instance used for token state modifications.
        :param store: Store instance used for state reference.
        :param template_processor: Template processor.
        :param translate_callback: Reference to Theory.Translate method.
        """

        self.veil = veil
        self.store = store
        self.template_processor = template_processor
        self.data_map = {}
        self.translate_callback = translate_callback

        # Build in-memory data map
        log('Building data map...')
        with open(data_map_path) as data_map_file:
            for item in csv.DictReader(data_map_file):
                src = self.__rm_all_whitespace(item['source'])
                tar = item['target']
                self.data_map[src] = tar

        log('Data map built successfully.')

    def reset(self):
        """Reset state."""
        pass

    @staticmethod
    def __rm_all_whitespace(seq: str):
        return re.sub(re.compile(r'\s+'), '', seq)

    def map(self, seq: str):
        """
        Map the given source sequence to the target sequence.

        :param seq: Sequence to translate. Assumed to be stripped.
        :returns: Target sequence (translation).
        """

        seq_stripped = self.__rm_all_whitespace(seq)

        if seq_stripped in self.data_map.keys():
            return self.data_map[seq_stripped]

        return None

    def translate(self, seq: str, indent: int = 0):
        """
        Translate sequence for the given LVP **without neural translation.**

        **NOTE: Must run AFTER entire masking process from Veil.**

        :param seq: Sequence to translate. Assumed to be stripped.
        :param indent: Source indentation length.
        :returns: Translated sequence. If no translation available, returns `None`.
        """
        pass

    @staticmethod
    def translate_std_to_nodejs(seq: str):
        """Translate sequence for a std language to Node.js."""

        # Copy certain sequences directly to target
        if seq in STD_SEQS_TO_COPY or seq.startswith('//') or seq.startswith('/*'):
            return seq

        # Map certain sequences to JS equivalents
        if seq in STD_TO_JS_SEQ_MAP.keys():
            return STD_TO_JS_SEQ_MAP[seq]

        # Copy certain masked sequences directly to target
        for regex in STANDARD_MASKED_SEQS_TO_COPY:
            if re.match(re.compile(regex), seq) is not None:
                return seq

        return None

    @staticmethod
    def translate_std_to_python_3(seq: str):
        """Translate sequence for a std language to Python 3."""

        # Copy certain sequences directly to target
        if seq in STD_SEQS_TO_COPY or seq.startswith('//') or seq.startswith('/*'):
            return seq.strip(';').replace(' {', ':')

        # Copy certain masked sequences directly to target
        for regex in STANDARD_TO_PY_MASKED_SEQS_TO_COPY:
            if re.match(re.compile(regex), seq) is not None:
                return seq

        # Add error for "switch" structures
        if seq.startswith('switch'):
            return '# [Turring Theory] ERROR: "switch" structures are currently unsupported for Python targets.\n' + \
                   '# We recommend replacing the following source with an "if" statement chain instead.\n' + \
                   f'#\n# {seq}'

        return None
