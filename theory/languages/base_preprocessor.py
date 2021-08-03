class Preprocessor:
    """Base preprocessor."""

    def __init__(self, gen_next_mask_token, save_mask_token):
        """
        :param gen_next_mask_token: Callback function for `Veil.gen_next_mask_token`.
        :param save_mask_token: Callback function for `Veil.save_mask_token`.
        """

        self.gen_next_mask_token = gen_next_mask_token
        self.save_mask_token = save_mask_token

        # Line split regex.
        self.line_split_regex = ''

        # Reserved tokens.
        self.reserved_tokens = list()

        # Regular expressions for finding specific reserved tokens.
        self.reserved_token_regexes = list()

        # All possible tags for this source language.
        self.tags = list()

    def preprocess(self, file_contents: str, request_data=None) -> str:
        """
        Preprocess file contents.

        :param file_contents: File contents.
        :param request_data: Request body data from "/translate" API endpoint.
        :returns: File contents with tags.
        """
        pass

    def should_mask_seq(self, seq: str) -> bool:
        """
        :param seq: Sequence.
        :returns: Whether the given sequence should be masked.
        """
        return True

    def should_mask_token(self, token: str) -> bool:
        """
        :param token: Token.
        :returns: Whether the given token should be masked.
        """
        return True

    def process_src_token(self, src_token: str) -> str:
        """
        Process source token once masked.

        :param src_token: Source token.
        :returns: New source token.
        """

        return src_token
