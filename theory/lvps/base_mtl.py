from theory.lvps.base_itl import ITL
from theory.veil import Veil


class MTL:
    """
    Base Macro Translation Layer for translating multi-line blocks and portions of sequences.
    Runs before the main neural network translation loop (including the ITL).
    """

    def __init__(self, itl: ITL, veil: Veil):
        """
        :param itl: ITL instance.
        :param veil: Veil instance.
        """

        self.itl = itl
        self.veil = veil

    def translate_all(self, file_contents: str) -> str:
        """
        Perform all micro-translations.

        :param file_contents: File contents.
        :returns: New file contents.
        """
        pass
