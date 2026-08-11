from __future__ import annotations

from utils.pattern_extractor import extract_matches
from utils.regex_tools import MATCH_TIMEOUT_SECONDS


def test_extract_matches_basic():
    text = "error: connection failed\ninfo: retrying\nerror: timeout\n"

    result = extract_matches(r"^error:", text)

    assert result["ok"] is True
    assert result["match_count"] == 2
    assert [m["line_number"] for m in result["matching_lines"]] == [1, 3]


def test_extract_matches_captures_groups():
    text = "user=alice status=active\nuser=bob status=inactive\n"

    result = extract_matches(r"user=(\w+)", text)

    assert result["ok"] is True
    assert result["matching_lines"][0]["groups"] == ["alice"]


def test_extract_matches_no_matches():
    result = extract_matches(r"zzz", "hello\nworld\n")

    assert result["ok"] is True
    assert result["match_count"] == 0
    assert result["matching_lines"] == []


def test_extract_matches_rejects_empty_pattern():
    result = extract_matches("", "text")

    assert result["ok"] is False
    assert result["error"] == "Enter a regex pattern."


def test_extract_matches_rejects_invalid_pattern():
    result = extract_matches("(", "text")

    assert result["ok"] is False
    assert "Invalid pattern" in result["error"]


def test_extract_matches_rejects_oversized_text():
    result = extract_matches("a", "a" * 50_001)

    assert result["ok"] is False
    assert "Text is longer than" in result["error"]


def test_extract_matches_stops_catastrophic_backtracking():
    # Regression: this MUST be evaluated via the subprocess-isolated
    # mechanism in utils.regex_tools, not a direct re.search call -- a
    # naive implementation would hang here instead of returning a clean
    # timeout error. This test intentionally takes ~MATCH_TIMEOUT_SECONDS.
    result = extract_matches(r"(a+)+$", "a" * 30 + "!")

    assert result["ok"] is False
    assert f"{MATCH_TIMEOUT_SECONDS:g}s" in result["error"]
