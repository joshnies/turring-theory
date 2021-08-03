from theory.languages.cobol.definition import CobolDefinition
from theory.languages.csharp.definition import CSharpDefinition
from theory.languages.std.definition import StdLangDefinition
from theory.lvp import LVP


def get_language_definition(lvp: LVP, is_target: bool = False):
    """
    Get language definition.

    :param lvp: LVP.
    :param is_target: Whether to return the LVP's target language definition.
    :returns: Language definition.
    """

    if is_target:
        # Target
        if lvp == LVP.CPP_17_TO_NODEJS_14 or \
                lvp == LVP.JAVA_14_TO_NODEJS_14 or \
                lvp == LVP.JAVA_14_TO_PYTHON_3:
            return StdLangDefinition
        elif lvp == LVP.COBOL_TO_CSHARP_9:
            return CSharpDefinition
    else:
        # Source
        if lvp == LVP.CPP_17_TO_NODEJS_14 or \
                lvp == LVP.JAVA_14_TO_NODEJS_14 or \
                lvp == LVP.JAVA_14_TO_PYTHON_3:
            return StdLangDefinition
        elif lvp == LVP.COBOL_TO_CSHARP_9:
            return CobolDefinition

    src_tar = 'target' if is_target else 'source'

    raise Exception(f'No language definition class found for LVP "{lvp.value}" {src_tar}.')
