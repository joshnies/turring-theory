import re

from theory.utils import match_to_str, add_re_begin_end, replace_str_range, offset_range_tuple, rreplace, \
    to_special_token, to_special_tokens, gen_mask_token


def test_match_to_str():
    """match_to_str() should return matched string from regex match."""

    text = 'Hello world!'
    match = re.match(r'Hello', text)

    assert match_to_str(match) == 'Hello'


def test_add_re_begin_end():
    """add_re_begin_end() should return string with regex begin and end characters."""

    text = 'hello|world'

    assert add_re_begin_end(text) == rf'^{text}$'


def test_replace_str_range():
    """replace_str_range() should return string with replacement at range."""

    text = 'The quick brown fox jumps over the lazy dog'

    assert replace_str_range(text, 'slow grey', (4, 15)) == 'The slow grey fox jumps over the lazy dog'


def test_rreplace():
    """rreplace() should return string with reverse-replaced string."""

    text = 'foo foo foo'

    assert rreplace(text, 'foo', 'bar') == 'bar bar bar'
    assert rreplace(text, 'foo', 'bar', occurrences=1) == 'foo foo bar'


def test_offset_range_tuple():
    """offset_range_tuple() should return range tuple offset by given int."""

    assert offset_range_tuple((0, 10), 2) == (2, 12)
    assert offset_range_tuple((5, 25), 10) == (15, 35)
    assert offset_range_tuple((1, 35), -1) == (0, 34)


def test_to_special_token():
    """to_special_token() should return a special token."""

    assert to_special_token('foo') == '%foo%'


def test_to_special_tokens():
    """to_special_tokens() should map all given strings into special tokens."""

    assert to_special_tokens(['foo', 'bar']) == ['%foo%', '%bar%']


def test_gen_mask_token():
    """gen_mask_token() should return mask token with given index."""

    for i in range(101):
        assert gen_mask_token(i) == f'%mask_{i}%'
