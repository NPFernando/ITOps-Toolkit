from __future__ import annotations

from utils.number_to_words import MAX_MAGNITUDE, number_to_words


def test_zero():
    assert number_to_words("0")["output"] == "zero"


def test_teen():
    assert number_to_words("15")["output"] == "fifteen"


def test_compound_tens():
    assert number_to_words("21")["output"] == "twenty-one"


def test_hundreds():
    assert number_to_words("105")["output"] == "one hundred five"


def test_thousand():
    assert number_to_words("1001")["output"] == "one thousand one"


def test_large_number_with_all_scale_words():
    result = number_to_words("123456789")

    assert result["ok"] is True
    assert result["output"] == "one hundred twenty-three million four hundred fifty-six thousand seven hundred eighty-nine"


def test_negative_number():
    assert number_to_words("-5")["output"] == "negative five"


def test_quadrillion_and_quintillion_scale_words_present():
    # Regression: the scale-word list originally skipped "quadrillion"
    # entirely (jumping straight from trillion to a mislabeled
    # "quintillion" one power too early), which also made the list one
    # entry too short and crashed on the largest supported magnitudes.
    assert number_to_words("1000000000000000")["output"] == "one quadrillion"
    assert number_to_words("1000000000000000000")["output"] == "one quintillion"


def test_max_magnitude_does_not_crash():
    result = number_to_words(str(MAX_MAGNITUDE))

    assert result["ok"] is True
    assert "quintillion" in result["output"]


def test_rejects_above_max_magnitude():
    result = number_to_words(str(MAX_MAGNITUDE + 1))

    assert result["ok"] is False
    assert "larger than this tool supports" in result["error"]


def test_rejects_non_integer():
    result = number_to_words("3.14")

    assert result["ok"] is False
    assert result["error"] == "Enter a whole number (no decimals)."


def test_rejects_empty_input():
    result = number_to_words("")

    assert result["ok"] is False
    assert result["error"] == "Enter an integer."
