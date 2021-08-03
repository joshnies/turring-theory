from theory.languages.csharp.definition import CSharpDefinition


def test_invert_condition():
    """CSharpDefinition.invert_condition() should invert a C# condition."""

    assert CSharpDefinition.invert_condition('HelloWorld') == '!HelloWorld'
    assert CSharpDefinition.invert_condition('!HelloWorld') == 'HelloWorld'
    assert CSharpDefinition.invert_condition('HelloWorld == null') == 'HelloWorld != null'
    assert CSharpDefinition.invert_condition('HelloWorld == OtherVar') == 'HelloWorld != OtherVar'
