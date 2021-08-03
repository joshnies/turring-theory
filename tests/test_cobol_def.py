from theory.languages.cobol.definition import CobolDefinition


def test_name_to_camel_case():
    """CobolDefinition.name_to_camel_case() should convert the given entity name to camelCase."""

    assert CobolDefinition.name_to_camel_case('PARAGRAPH') == 'paragraph'
    assert CobolDefinition.name_to_camel_case('HELLO-WORLD') == 'helloWorld'
    assert CobolDefinition.name_to_camel_case('A-100-MAIN') == 'a100Main'
    assert CobolDefinition.name_to_camel_case('850-TEST-FUNCTION') == '850TestFunction'


def test_name_to_snake_case():
    """CobolDefinition.name_to_snake_case() should convert the given entity name to snake_case."""

    assert CobolDefinition.name_to_snake_case('PARAGRAPH') == 'paragraph'
    assert CobolDefinition.name_to_snake_case('HELLO-WORLD') == 'hello_world'
    assert CobolDefinition.name_to_snake_case('A-100-MAIN') == 'a_100_main'
    assert CobolDefinition.name_to_snake_case('850-TEST-FUNCTION') == '850_test_function'


def test_name_to_title_case():
    """CobolDefinition.name_to_title_case() should convert the given entity name to TitleCase."""

    assert CobolDefinition.name_to_title_case('PARAGRAPH') == 'Paragraph'
    assert CobolDefinition.name_to_title_case('HELLO-WORLD') == 'HelloWorld'
    assert CobolDefinition.name_to_title_case('A-100-MAIN') == 'A100Main'

    # Escaped first numeric
    assert CobolDefinition.name_to_title_case('850-TEST-FUNCTION') == '_850TestFunction'

    # Non-escaped first numeric
    assert CobolDefinition.name_to_title_case('850-TEST-FUNCTION', escape_first_numeric=False) == '850TestFunction'
