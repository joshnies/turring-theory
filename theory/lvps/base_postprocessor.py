class Postprocessor:
    """Base post-processor."""

    @staticmethod
    def __replace_special_chars(line: str):
        """Replace special characters in the given text."""

        # Unescape underscores
        res = line.replace(r'\&undsc', '_')

        # Escape newlines except when within string literals
        res = res.replace(r'\n', '\n').replace("'\n'", r"'\n'").replace('"\n"', r'"\n"')

        return res

    def postprocess_line(self, line: str) -> str:
        """Postprocess the given line."""
        return self.__replace_special_chars(line)

    def postprocess_file(self, file_contents: str) -> str:
        """Postprocess the given file contents."""
        return file_contents
