from utils import case_tools


def test_convert_case_from_spaced_words():
    result = case_tools.convert_case("hello world example")

    assert result["ok"] is True
    assert result["slug_case"] == "hello-world-example"
    assert result["snake_case"] == "hello_world_example"
    assert result["camel_case"] == "helloWorldExample"
    assert result["pascal_case"] == "HelloWorldExample"
    assert result["title_case"] == "Hello World Example"
    assert result["upper_snake_case"] == "HELLO_WORLD_EXAMPLE"


def test_convert_case_from_mixed_delimiters_and_camel_input():
    result = case_tools.convert_case("helloWorld_fooBar-BAZQux")

    assert result["ok"] is True
    assert result["snake_case"] == "hello_world_foo_bar_baz_qux"
    assert result["camel_case"] == "helloWorldFooBarBazQux"


def test_convert_case_strips_non_alphanumeric_characters():
    result = case_tools.convert_case("hello, world!")

    assert result["ok"] is True
    assert result["slug_case"] == "hello-world"


def test_convert_case_requires_input():
    result = case_tools.convert_case("   ")

    assert result["ok"] is False
    assert "Enter some text" in result["error"]


def test_convert_case_rejects_input_with_no_alphanumeric_characters():
    result = case_tools.convert_case("!!!---")

    assert result["ok"] is False
    assert "No alphanumeric characters" in result["error"]


def test_convert_case_rejects_oversized_input():
    oversized = "a " * (case_tools.MAX_INPUT_LENGTH)

    result = case_tools.convert_case(oversized)

    assert result["ok"] is False
    assert "longer than" in result["error"]
