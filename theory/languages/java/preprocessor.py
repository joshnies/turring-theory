from .constants import JAVA_RESERVED_TOKENS, JAVA_RESERVED_TOKENS_RE
from ..std.preprocessor import StandardPreprocessor


class JavaPreprocessor(StandardPreprocessor):
    """Java preprocessor."""

    def __init__(self, gen_next_mask_token, save_mask_token):
        super().__init__(gen_next_mask_token, save_mask_token)

        # Define reserved tokens
        self.reserved_tokens = JAVA_RESERVED_TOKENS
        self.reserved_token_regexes = JAVA_RESERVED_TOKENS_RE
