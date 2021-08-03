from theory.languages.base_lang_def import LanguageDefinition


class StdLangDefinition(LanguageDefinition):
    """Standard language definition."""

    @staticmethod
    def to_single_line_comment(text: str) -> str:
        return f'// {text}'

    @staticmethod
    def to_multi_line_comment(text: str) -> str:
        return f'/* {text} */'
