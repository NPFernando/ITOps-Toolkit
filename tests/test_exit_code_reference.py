from __future__ import annotations

from utils.exit_code_reference import EXIT_CODES, search_exit_codes


def test_empty_query_returns_all():
    assert search_exit_codes("") == EXIT_CODES


def test_search_by_code():
    results = search_exit_codes("137")

    assert len(results) == 1
    assert results[0].code == 137


def test_search_by_keyword_is_case_insensitive():
    results = search_exit_codes("SIGKILL")

    assert len(results) == 1
    assert results[0].code == 137


def test_search_no_match_returns_empty():
    assert search_exit_codes("nonexistent-keyword-xyz") == ()


def test_all_codes_in_valid_range():
    assert all(0 <= entry.code <= 255 for entry in EXIT_CODES)


def test_codes_are_unique():
    codes = [entry.code for entry in EXIT_CODES]
    assert len(codes) == len(set(codes))
