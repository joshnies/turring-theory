from typing import List


class LanguageDefinition:
    """Language definition containing general constants and methods."""

    @staticmethod
    def get_translated_file_name(filename: str):
        """
        :returns: Translated file name.
        """

        return filename

    @staticmethod
    def create_project_files(project_path: str, added_file_paths: List[str] = None) -> str:
        """
        Create supporting project files for a translated file.

        :param project_path: Project path.
        :param added_file_paths: List of paths for files to add to the project.
        :returns: Project path.
        """
        pass

    @staticmethod
    def format_file(file_path: str, request_data=None) -> List[str]:
        """
        Format file.

        :param file_path: File path.
        :param request_data: Request body data from "/translate" API endpoint.
        :returns: Formatted file lines.
        """

        return open(file_path).readlines()

    @staticmethod
    def format_project_files(project_path: str) -> List[str]:
        """
        Format project files.

        :param project_path: Project path.
        """
        pass

    @staticmethod
    def to_single_line_comment(text: str) -> str:
        """
        Convert a line of text to a single-line comment.

        :param text: Line of text.
        :returns: Single-line comment.
        """
        pass

    @staticmethod
    def to_multi_line_comment(text: str) -> str:
        """
        Convert a line of text to a multi-line comment.

        :param text: Line of text.
        :returns: Multi-line comment.
        """
        pass
