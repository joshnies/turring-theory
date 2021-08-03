from abc import ABC


class Store(ABC):
    """Base state storage."""

    def scan(self, file_path: str):
        """
        Scan masked lines to build state before translation begins.

        :param file_path: Path to file for scanning.
        """
        pass

    def update(self, line: str):
        """
        Update state.

        :param line: Original source line.
        """
        pass

    def post_translation_hook(self, seq: str):
        """
        Update state based on the translated sequence.

        :param seq: Translated sequence.
        """
        pass
