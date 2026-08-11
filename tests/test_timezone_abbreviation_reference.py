from __future__ import annotations

from utils.timezone_abbreviation_reference import TIMEZONE_ABBREVIATIONS, search_timezone_abbreviations


def test_empty_query_returns_all():
    assert search_timezone_abbreviations("") == TIMEZONE_ABBREVIATIONS


def test_search_by_abbreviation_returns_all_ambiguous_meanings():
    # Regression guard for the whole point of this tool: an ambiguous
    # abbreviation like CST must return every real-world meaning, not one.
    results = search_timezone_abbreviations("CST")

    names = {entry.name for entry in results}
    assert "US Central Standard Time" in names
    assert "China Standard Time" in names
    assert "Cuba Standard Time" in names
    assert len(results) >= 3


def test_search_by_offset():
    results = search_timezone_abbreviations("UTC+05:30")

    assert len(results) == 1
    assert results[0].abbreviation == "IST"
    assert results[0].name == "India Standard Time"


def test_search_by_name_fragment_is_case_insensitive():
    results = search_timezone_abbreviations("pacific")

    assert any(entry.abbreviation == "PST" for entry in results)


def test_search_no_match_returns_empty():
    assert search_timezone_abbreviations("nonexistent-zone-xyz") == ()
