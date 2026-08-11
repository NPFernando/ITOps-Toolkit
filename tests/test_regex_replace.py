from __future__ import annotations

from utils.regex_replace import find_and_replace
from utils.regex_tools import MATCH_TIMEOUT_SECONDS


def test_find_and_replace_basic():
    result = find_and_replace(r"foo", "XXX", "foo bar foo baz")

    assert result["ok"] is True
    assert result["output"] == "XXX bar XXX baz"
    assert result["replacement_count"] == 2


def test_find_and_replace_backreferences():
    result = find_and_replace(r"(\w+) (\w+)", r"\2 \1", "hello world")

    assert result["ok"] is True
    assert result["output"] == "world hello"


def test_find_and_replace_no_matches():
    result = find_and_replace(r"zzz", "x", "hello world")

    assert result["ok"] is True
    assert result["output"] == "hello world"
    assert result["replacement_count"] == 0


def test_find_and_replace_rejects_empty_pattern():
    result = find_and_replace("", "x", "text")

    assert result["ok"] is False
    assert result["error"] == "Enter a regex pattern."


def test_find_and_replace_rejects_invalid_pattern():
    result = find_and_replace("(", "x", "text")

    assert result["ok"] is False
    assert "Invalid pattern" in result["error"]


def test_find_and_replace_rejects_invalid_backreference():
    result = find_and_replace(r"(\w)", r"\9", "a")

    assert result["ok"] is False
    assert "Invalid replacement" in result["error"]


def test_find_and_replace_rejects_oversized_pattern():
    result = find_and_replace("a" * 501, "x", "text")

    assert result["ok"] is False
    assert "Pattern is longer than" in result["error"]


def test_find_and_replace_rejects_oversized_text():
    result = find_and_replace("a", "x", "a" * 50_001)

    assert result["ok"] is False
    assert "Text is longer than" in result["error"]


def test_find_and_replace_stops_catastrophic_backtracking():
    # Regression: this MUST be evaluated via the subprocess-isolated
    # mechanism in utils.regex_tools, not a direct re.sub call -- a naive
    # implementation would hang here instead of returning a clean timeout
    # error. This test intentionally takes ~MATCH_TIMEOUT_SECONDS to run.
    result = find_and_replace(r"(a+)+$", "x", "a" * 30 + "!")

    assert result["ok"] is False
    assert f"{MATCH_TIMEOUT_SECONDS:g}s" in result["error"]
