import logging
import re
from typing import Tuple, List

from cli import log


def match_to_str(match) -> str:
    """Get matched string from regex match."""

    span = match.span()
    return match.string[span[0]:span[1]]


def add_re_begin_end(re_str: str) -> str:
    """
    Add regex symbols for sentence begin and end.

    :param re_str: Regex string.
    :returns: Regex string.
    """

    return fr'^{re_str}$'


def replace_str_range(old: str, new: str, range_tuple: Tuple[int, int]) -> str:
    """
    Replace string range.

    :param old: Old string.
    :param new: New string.
    :param range_tuple: Tuple range for replacement.
    :returns: String with injected replacement.
    """

    start, end = range_tuple
    return new.join([old[:start], old[end:]])


def rreplace(s: str, old: str, new: str, occurrences: int = -1):
    """Replace a substring within a string in reverse order."""

    li = s.rsplit(old, maxsplit=occurrences)
    return new.join(li)


def offset_range_tuple(range_tuple: Tuple[int, int], offset: int) -> Tuple[int, int]:
    """
    Offset a range tuple.

    :param range_tuple: Range tuple.
    :param offset: Integer to offset each item in range tuple by.
    :returns: Range tuple
    """

    return range_tuple[0] + offset, range_tuple[1] + offset


def to_special_token(token: str) -> str:
    """
    Transform string to a special token.

    :param token: Token.
    :returns: Special token.
    """

    return f'%{token}%'


def to_special_tokens(tokens: List[str]) -> List[str]:
    """
    Transform list of strings to list of special tokens.

    :param tokens: Tokens.
    :returns: Special tokens.
    """

    return list(map(to_special_token, tokens))


def gen_mask_token(index: int) -> str:
    """
    Generate mask token for index.

    :param index: Index.
    :returns: Mask token.
    """

    return to_special_token(f'mask_{index}')


def log_translation(translation_method: str, src: str, tar: str):
    """
    Log a translation.

    :param translation_method: Method for translation (ITL or NN).
    :param src: Source (input) sequence.
    :param tar: Target (translated) sequence.
    """

    log('-' * 80, level=logging.DEBUG)
    log(f'- From:        {translation_method}', level=logging.DEBUG)
    log(f'- Input:       {src}', level=logging.DEBUG)
    log(f'- Translation: {tar}', level=logging.DEBUG)
    log('-' * 80, level=logging.DEBUG)


def split_upper(s) -> List[str]:
    """
    Split a string by uppercase letters.

    :returns: Split string.
    """

    return list(filter(None, re.split(r'([A-Z][^A-Z]*)', s)))


def key_from_path(keypath: str) -> str:
    """
    Get key from keypath.

    :param keypath: Keypath.
    :returns: Key.
    """

    return keypath.split('.')[-1]
