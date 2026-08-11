from __future__ import annotations

from utils.password_policy_checker import check_password_policy


def test_compliant_password():
    result = check_password_policy("Abc123!@#xyz")

    assert result["ok"] is True
    assert result["compliant"] is True
    assert all(rule["passed"] for rule in result["rules"])


def test_too_short_fails_length_rule():
    result = check_password_policy("short", min_length=12)

    assert result["ok"] is True
    assert result["compliant"] is False
    length_rule = next(r for r in result["rules"] if "characters" in r["rule"])
    assert length_rule["passed"] is False


def test_missing_symbol_fails_symbol_rule():
    result = check_password_policy("Abcdefgh123", min_length=8)

    assert result["compliant"] is False
    symbol_rule = next(r for r in result["rules"] if "symbol" in r["rule"])
    assert symbol_rule["passed"] is False


def test_whitespace_fails_whitespace_rule():
    result = check_password_policy("Abc 123!@#xyz")

    whitespace_rule = next(r for r in result["rules"] if "whitespace" in r["rule"])
    assert whitespace_rule["passed"] is False


def test_disabled_rules_are_not_checked():
    result = check_password_policy("alllowercase", require_upper=False, require_digit=False, require_symbol=False, min_length=8)

    assert result["compliant"] is True
    assert len(result["rules"]) == 3  # length, lowercase, no-whitespace


def test_rejects_empty_password():
    result = check_password_policy("")

    assert result["ok"] is False
    assert result["error"] == "Enter a password to check."


def test_rejects_invalid_min_length():
    result = check_password_policy("abc", min_length=0)

    assert result["ok"] is False
    assert "at least 1" in result["error"]
