from __future__ import annotations

import re

from utils.regex_reference import REGEX_PATTERNS, search_patterns


def test_every_pattern_compiles():
    for entry in REGEX_PATTERNS:
        re.compile(entry.pattern)  # raises re.error if malformed


def test_search_patterns_empty_query_returns_everything():
    assert search_patterns("") == REGEX_PATTERNS
    assert search_patterns("   ") == REGEX_PATTERNS


def test_search_patterns_matches_by_name():
    results = search_patterns("email")

    assert results
    assert all("email" in entry.name.lower() for entry in results)


def test_search_patterns_matches_by_description():
    results = search_patterns("hex")

    assert any(entry.name == "Hex color" for entry in results)


def test_search_patterns_no_match_returns_empty():
    assert search_patterns("not-a-real-pattern-keyword") == ()
