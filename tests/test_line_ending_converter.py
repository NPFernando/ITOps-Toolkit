from __future__ import annotations

from utils.line_ending_converter import convert_line_endings


def test_convert_crlf_to_lf():
    result = convert_line_endings("a\r\nb\r\nc", "LF")

    assert result["ok"] is True
    assert result["output"] == "a\nb\nc"
    assert result["detected_input_style"] == "CRLF"


def test_convert_lf_to_crlf():
    result = convert_line_endings("a\nb\nc", "CRLF")

    assert result["ok"] is True
    assert result["output"] == "a\r\nb\r\nc"
    assert result["detected_input_style"] == "LF"


def test_convert_to_cr():
    result = convert_line_endings("a\nb", "CR")

    assert result["ok"] is True
    assert result["output"] == "a\rb"


def test_convert_detects_mixed_input():
    result = convert_line_endings("a\r\nb\nc\r", "LF")

    assert result["ok"] is True
    assert result["detected_input_style"] == "Mixed"
    assert result["output"] == "a\nb\nc\n"


def test_convert_round_trip_does_not_double_convert_crlf():
    # A CRLF pair must become exactly one LF, not two.
    result = convert_line_endings("a\r\nb", "LF")

    assert result["output"] == "a\nb"
    assert result["output"].count("\n") == 1


def test_convert_single_line_no_breaks():
    result = convert_line_endings("just one line", "CRLF")

    assert result["ok"] is True
    assert result["detected_input_style"] == "None (single line, no line breaks)"


def test_convert_rejects_empty_input():
    result = convert_line_endings("", "LF")

    assert result["ok"] is False
    assert result["error"] == "Paste text to convert."


def test_convert_rejects_unknown_target():
    result = convert_line_endings("a\nb", "BOGUS")

    assert result["ok"] is False
    assert "Unknown target" in result["error"]


def test_convert_rejects_oversized_input():
    result = convert_line_endings("a" * 100_001, "LF")

    assert result["ok"] is False
    assert "longer than" in result["error"]
