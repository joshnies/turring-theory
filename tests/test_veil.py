from theory.lvp import LVP
from theory.utils import gen_mask_token
from theory.veil import Veil


def test_unmask():
    """Veil.unmask() should unmask text using the current tokens state."""

    veil = Veil(LVP.JAVA_14_TO_NODEJS_14)
    text = 'int %mask_0% = %mask_1%;'

    veil.tokens['%mask_0%'] = 'hello_world'
    veil.tokens['%mask_1%'] = '5'

    assert veil.unmask(text) == 'int hello_world = 5;'


def test_relative():
    """
    Veil.to_relative() and Veil.from_relative() should extract and replace mask tokens between relative and global
    spaces.
    """

    veil = Veil(LVP.JAVA_14_TO_NODEJS_14)
    text = 'int %mask_20% = %mask_25%;'
    expected_relative_text = 'int %mask_0% = %mask_1%;'

    assert veil.to_relative(text) == expected_relative_text
    assert veil.from_relative(expected_relative_text) == text


def test_gen_next_mask_token():
    """Veil.gen_next_mask_token() should generate the next unused mask token."""

    veil = Veil(LVP.JAVA_14_TO_NODEJS_14)

    veil.tokens['%mask_0%'] = 'hello_world'
    veil.tokens['%mask_1%'] = '5'

    assert veil.gen_next_mask_token() == '%mask_2%'


def test_save_mask_token():
    """Veil.save_mask_token() should save the given mask token with the given source token."""

    veil = Veil(LVP.JAVA_14_TO_NODEJS_14)

    mask_token = gen_mask_token(0)
    src_token = 'hello world'
    veil.save_mask_token(mask_token, src_token, process_source_token=False)

    assert veil.tokens[mask_token] == src_token
