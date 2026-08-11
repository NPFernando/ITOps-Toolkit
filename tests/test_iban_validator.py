from __future__ import annotations

from utils.iban_validator import validate_iban


def test_valid_german_iban():
    result = validate_iban("DE89370400440532013000")

    assert result["ok"] is True
    assert result["valid"] is True
    assert result["country"] == "DE"


def test_valid_uk_iban_with_spaces():
    result = validate_iban("GB29 NWBK 6016 1331 9268 19")

    assert result["ok"] is True
    assert result["valid"] is True
    assert result["formatted"] == "GB29 NWBK 6016 1331 9268 19"


def test_invalid_checksum():
    result = validate_iban("DE89370400440532013001")

    assert result["ok"] is True
    assert result["valid"] is False


def test_rejects_unknown_country_code():
    result = validate_iban("XX89370400440532013000")

    assert result["ok"] is False
    assert "not a recognized IBAN country code" in result["error"]


def test_rejects_wrong_length_for_country():
    result = validate_iban("DE8937040044053201300")

    assert result["ok"] is False
    assert "22 characters" in result["error"]


def test_rejects_lowercase_letters_normalized():
    result = validate_iban("de89370400440532013000")

    assert result["ok"] is True
    assert result["valid"] is True


def test_rejects_non_alphanumeric_characters():
    result = validate_iban("DE89-3704-0044-0532-0130-00")

    assert result["ok"] is False
    assert "only letters and digits" in result["error"]


def test_rejects_empty_input():
    result = validate_iban("")

    assert result["ok"] is False
    assert result["error"] == "Enter an IBAN."


def test_rejects_non_numeric_check_digits():
    result = validate_iban("DEAB370400440532013000")

    assert result["ok"] is False
    assert "Check digits must be numeric" in result["error"]
