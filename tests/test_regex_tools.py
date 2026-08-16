import time

from utils import regex_tools


def test_test_regex_finds_all_matches_with_positions():
    result = regex_tools.test_regex(r"\d+", "abc 123 def 456")

    assert result["ok"] is True
    assert result["match_count"] == 2
    assert result["matches"][0] == {"match": "123", "start": 4, "end": 7, "groups": []}
    assert result["matches"][1]["match"] == "456"


def test_test_regex_captures_groups():
    result = regex_tools.test_regex(r"(\w+)@(\w+)", "contact: alice@example")

    assert result["ok"] is True
    assert result["matches"][0]["groups"] == ["alice", "example"]


def test_test_regex_rejects_invalid_pattern():
    result = regex_tools.test_regex(r"(unclosed", "text")

    assert result["ok"] is False
    assert "Invalid pattern" in result["error"]


def test_test_regex_requires_a_pattern():
    result = regex_tools.test_regex("", "text")

    assert result["ok"] is False
    assert "Enter a regex pattern" in result["error"]


def test_test_regex_rejects_oversized_pattern_and_text():
    oversized_pattern = "a" * (regex_tools.MAX_PATTERN_LENGTH + 1)
    oversized_text = "a" * (regex_tools.MAX_TEXT_LENGTH + 1)

    assert regex_tools.test_regex(oversized_pattern, "text")["ok"] is False
    assert regex_tools.test_regex(r"\d+", oversized_text)["ok"] is False


def test_test_regex_ignorecase_flag():
    no_flag = regex_tools.test_regex("hello", "HELLO world")
    with_flag = regex_tools.test_regex("hello", "HELLO world", flag_names=("IGNORECASE",))

    assert no_flag["match_count"] == 0
    assert with_flag["match_count"] == 1


def test_test_regex_truncates_at_max_matches():
    result = regex_tools.test_regex(r"a", "a" * (regex_tools.MAX_MATCHES + 50))

    assert result["ok"] is True
    assert result["match_count"] == regex_tools.MAX_MATCHES
    assert result["truncated"] is True


def test_test_regex_kills_catastrophic_backtracking_within_timeout():
    start = time.time()
    result = regex_tools.test_regex(r"(a+)+$", "a" * 30 + "!")
    elapsed = time.time() - start

    assert result["ok"] is False
    assert "took longer than" in result["error"]
    # Generous margin over MATCH_TIMEOUT_SECONDS for process spawn/teardown
    # overhead -- the important assertion is "seconds", not "the 55+ seconds
    # this pattern would otherwise take uninterrupted".
    assert elapsed < regex_tools.MATCH_TIMEOUT_SECONDS + 5
