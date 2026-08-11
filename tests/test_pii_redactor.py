from __future__ import annotations

from utils.pii_redactor import LABELS, redact


def test_redacts_email():
    result = redact("Contact alice@example.com now", ["email"])

    assert result["ok"] is True
    assert result["output"] == "Contact [REDACTED_EMAIL] now"
    assert result["counts"]["email"] == 1


def test_redacts_only_selected_types():
    result = redact("alice@example.com and 192.168.1.1", ["email"])

    assert "[REDACTED_EMAIL]" in result["output"]
    assert "192.168.1.1" in result["output"]


def test_credit_card_does_not_swallow_ssn():
    # Regression guard: credit_card's broad 13-19-digit pattern must be
    # tried last so it doesn't consume a more specific SSN/phone match
    # sitting inside a longer digit run.
    result = redact("SSN 123-45-6789", ["ssn", "credit_card"])

    assert result["output"] == "SSN [REDACTED_SSN]"
    assert result["counts"]["ssn"] == 1
    assert result["counts"]["credit_card"] == 0


def test_credit_card_still_matches_long_digit_run():
    result = redact("Card 4111 1111 1111 1111", ["credit_card"])

    assert result["output"] == "Card [REDACTED_CREDIT_CARD]"


def test_all_types_together():
    text = "alice@example.com 555-123-4567 192.168.1.10 123-45-6789 4111111111111111"
    result = redact(text, list(LABELS.keys()))

    assert result["ok"] is True
    assert all(count == 1 for count in result["counts"].values())


def test_rejects_empty_input():
    result = redact("", ["email"])

    assert result["ok"] is False
    assert result["error"] == "Paste some text."


def test_rejects_no_types_selected():
    result = redact("hello", [])

    assert result["ok"] is False
    assert "at least one type" in result["error"]


def test_rejects_unknown_type():
    result = redact("hello", ["bogus"])

    assert result["ok"] is False
    assert "Unknown type" in result["error"]
