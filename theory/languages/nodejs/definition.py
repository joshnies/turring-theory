import os

from theory.languages.std.definition import StdLangDefinition


class NodeJSDefinition(StdLangDefinition):
    """Node.js language definition."""

    @staticmethod
    def format_file(file_path: str):
        os.system(f'npx prettier --write {file_path}')
