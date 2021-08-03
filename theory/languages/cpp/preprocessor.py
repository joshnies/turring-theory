from .constants import CPP_RESERVED_TOKENS
from ..std.preprocessor import StandardPreprocessor


class CppPreprocessor(StandardPreprocessor):
    """C++ preprocessor."""

    def __init__(self, gen_next_mask_token, save_mask_token):
        super().__init__(gen_next_mask_token, save_mask_token)

        # Define reserved tokens
        self.reserved_tokens = CPP_RESERVED_TOKENS
