from utils.base_converter import MAX_DIGITS, convert_base


def test_convert_base_decimal_to_all():
    result = convert_base("255", "Decimal")

    assert result["ok"] is True
    assert result["values"] == {"Binary": "11111111", "Octal": "377", "Decimal": "255", "Hexadecimal": "FF"}


def test_convert_base_hex_input_lowercase():
    result = convert_base("ff", "Hexadecimal")

    assert result["ok"] is True
    assert result["decimal"] == 255


def test_convert_base_strips_same_base_prefix():
    assert convert_base("0xFF", "Hexadecimal")["decimal"] == 255
    assert convert_base("0b1010", "Binary")["decimal"] == 10
    assert convert_base("0o377", "Octal")["decimal"] == 255


def test_convert_base_handles_negative_numbers():
    result = convert_base("-42", "Decimal")

    assert result["ok"] is True
    assert result["values"]["Hexadecimal"] == "-2A"
    assert result["values"]["Binary"] == "-101010"


def test_convert_base_rejects_empty_input():
    result = convert_base("", "Decimal")

    assert result["ok"] is False
    assert "Enter a number" in result["error"]


def test_convert_base_rejects_invalid_digits_for_base():
    result = convert_base("xyz", "Decimal")

    assert result["ok"] is False
    assert "not a valid decimal number" in result["error"]

    result_binary = convert_base("102", "Binary")
    assert result_binary["ok"] is False


def test_convert_base_rejects_unknown_base_label():
    result = convert_base("255", "Base64")

    assert result["ok"] is False
    assert "Unknown base" in result["error"]


def test_convert_base_rejects_oversized_input():
    result = convert_base("1" * (MAX_DIGITS + 1), "Binary")

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_convert_base_round_trips_across_all_bases():
    original = convert_base("12345", "Decimal")
    for label, value in original["values"].items():
        assert convert_base(value, label)["decimal"] == 12345
