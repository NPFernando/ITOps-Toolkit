from __future__ import annotations

from utils.whitespace_visualizer import visualize_whitespace

NBSP = chr(0x00A0)
ZERO_WIDTH_SPACE = chr(0x200B)
BOM = chr(0xFEFF)


def test_visualize_whitespace_flags_non_breaking_space():
    result = visualize_whitespace(f"hello{NBSP}world")

    assert result["ok"] is True
    assert len(result["findings"]) == 1
    assert result["findings"][0]["name"] == "NO-BREAK SPACE"
    assert result["findings"][0]["codepoint"] == "U+00A0"
    assert result["findings"][0]["column"] == 6


def test_visualize_whitespace_flags_zero_width_space():
    result = visualize_whitespace(f"hello{ZERO_WIDTH_SPACE}world")

    assert result["findings"][0]["name"] == "ZERO WIDTH SPACE"


def test_visualize_whitespace_flags_bom():
    result = visualize_whitespace(f"hello{BOM}world")

    assert result["findings"][0]["name"] == "ZERO WIDTH NO-BREAK SPACE"


def test_visualize_whitespace_clean_text_has_no_findings():
    result = visualize_whitespace("clean text, tabs\tand\nnewlines are fine")

    assert result["ok"] is True
    assert result["findings"] == []


def test_visualize_whitespace_tracks_line_number():
    result = visualize_whitespace(f"line one\nline{NBSP}two")

    assert result["findings"][0]["line"] == 2


def test_visualize_whitespace_annotated_text_substitutes_marker():
    result = visualize_whitespace(f"a{NBSP}b")

    assert result["annotated_text"] == "a[NO-BREAK SPACE]b"


def test_visualize_whitespace_rejects_empty_input():
    result = visualize_whitespace("")

    assert result["ok"] is False
    assert result["error"] == "Paste text to check."


def test_visualize_whitespace_rejects_oversized_input():
    result = visualize_whitespace("a" * 50_001)

    assert result["ok"] is False
    assert "longer than" in result["error"]
