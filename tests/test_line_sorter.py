from __future__ import annotations

from utils.line_sorter import sort_and_dedupe_lines


def test_dedupe_removes_exact_duplicates():
    result = sort_and_dedupe_lines("banana\napple\napple\ncherry", dedupe=True)

    assert result["ok"] is True
    assert result["output"] == "banana\napple\ncherry"
    assert result["removed_count"] == 1


def test_sort_alphabetical_ascending():
    result = sort_and_dedupe_lines("banana\napple\ncherry", sort_mode="Alphabetical (A-Z)")

    assert result["ok"] is True
    assert result["output"] == "apple\nbanana\ncherry"


def test_sort_alphabetical_descending():
    result = sort_and_dedupe_lines("banana\napple\ncherry", sort_mode="Alphabetical (Z-A)")

    assert result["ok"] is True
    assert result["output"] == "cherry\nbanana\napple"


def test_sort_case_insensitive():
    result = sort_and_dedupe_lines("Banana\napple\nCherry", sort_mode="Alphabetical (A-Z)", case_insensitive=True)

    assert result["ok"] is True
    assert result["output"] == "apple\nBanana\nCherry"


def test_dedupe_case_insensitive():
    result = sort_and_dedupe_lines("Apple\napple\nAPPLE", dedupe=True, case_insensitive=True)

    assert result["ok"] is True
    assert result["output"] == "Apple"


def test_sort_numeric_ascending():
    result = sort_and_dedupe_lines("10\n2\n1", sort_mode="Numeric (ascending)")

    assert result["ok"] is True
    assert result["output"] == "1\n2\n10"


def test_sort_numeric_descending():
    result = sort_and_dedupe_lines("10\n2\n1", sort_mode="Numeric (descending)")

    assert result["ok"] is True
    assert result["output"] == "10\n2\n1"


def test_sort_numeric_rejects_non_numeric_line():
    result = sort_and_dedupe_lines("10\nabc\n1", sort_mode="Numeric (ascending)")

    assert result["ok"] is False
    assert "numeric" in result["error"].lower()


def test_remove_blank_lines():
    result = sort_and_dedupe_lines("a\n\nb\n\n", remove_blank=True)

    assert result["ok"] is True
    assert result["output"] == "a\nb"


def test_rejects_empty_input():
    result = sort_and_dedupe_lines("")

    assert result["ok"] is False
    assert result["error"] == "Paste some text to process."


def test_rejects_oversized_input():
    result = sort_and_dedupe_lines("a" * 200_001)

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_rejects_unknown_sort_mode():
    result = sort_and_dedupe_lines("a\nb", sort_mode="Bogus")

    assert result["ok"] is False
    assert "Unknown sort mode" in result["error"]


def test_no_options_returns_lines_unchanged():
    result = sort_and_dedupe_lines("b\na\na", sort_mode="None", dedupe=False, remove_blank=False)

    assert result["ok"] is True
    assert result["output"] == "b\na\na"
