from theory.lvps.base_postprocessor import Postprocessor


def test_postprocess_line():
    """Postprocessor.postprocess_line() should replace special characters."""

    postprocessor = Postprocessor()
    text = '%mask\\&undsc0%'

    assert postprocessor.postprocess_line(text) == '%mask_0%'
