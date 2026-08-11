from __future__ import annotations

from utils.luhn_validator import validate_luhn


def test_validate_luhn_valid_test_card():
    result = validate_luhn("4532015112830366")

    assert result["ok"] is True
    assert result["is_valid"] is True
    assert result["digits_only"] == "4532015112830366"
    assert result["check_digit"] == 6


def test_validate_luhn_invalid_mutated_card():
    result = validate_luhn("4532015112830367")

    assert result["ok"] is True
    assert result["is_valid"] is False


def test_validate_luhn_strips_spaces_and_hyphens():
    result = validate_luhn("4532 0151-1283 0366")

    assert result["ok"] is True
    assert result["digits_only"] == "4532015112830366"
    assert result["is_valid"] is True


def test_validate_luhn_rejects_empty_input():
    result = validate_luhn("")

    assert result["ok"] is False
    assert result["error"] == "Enter a number to validate."


def test_validate_luhn_rejects_non_digit_characters():
    result = validate_luhn("123abc456")

    assert result["ok"] is False
    assert result["error"] == "Enter only digits, spaces, or hyphens."


def test_validate_luhn_rejects_single_digit():
    result = validate_luhn("5")

    assert result["ok"] is False
    assert "at least 2 digits" in result["error"]


def test_validate_luhn_rejects_oversized_input():
    result = validate_luhn("1" * 33)

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_validate_luhn_computed_check_digit_makes_number_valid():
    # Feeding the payload + its own computed check digit back in must
    # always validate.
    payload = "453201511283036"
    first = validate_luhn(payload + "0")
    check_digit = first["check_digit"]

    second = validate_luhn(payload + str(check_digit))

    assert second["is_valid"] is True
