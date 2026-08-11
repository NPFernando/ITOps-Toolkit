from __future__ import annotations

from utils.line_numberer import add_line_numbers


def test_basic_numbering():
    result = add_line_numbers("a\nb\nc")

    assert result["ok"] is True
    assert result["output"] == "1: a\n2: b\n3: c"


def test_custom_start_and_separator():
    result = add_line_numbers("a\nb", start_at=100, separator=" | ")

    assert result["ok"] is True
    assert result["output"] == "100 | a\n101 | b"


def test_numbers_are_right_aligned_to_widest():
    result = add_line_numbers("\n".join(["x"] * 11))

    lines = result["output"].splitlines()
    assert lines[0] == " 1: x"
    assert lines[10] == "11: x"


def test_rejects_empty_input():
    result = add_line_numbers("")

    assert result["ok"] is False
    assert result["error"] == "Paste some text."


def test_rejects_oversized_input():
    result = add_line_numbers("a" * 200_001)

    assert result["ok"] is False
    assert "longer than" in result["error"]
