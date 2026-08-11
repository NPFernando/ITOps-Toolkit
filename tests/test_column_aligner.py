from __future__ import annotations

from utils.column_aligner import align_columns


def test_aligns_whitespace_separated_columns():
    result = align_columns("USER PID CPU\nroot 1 0.0\nwww-data 1234 12.5")

    assert result["ok"] is True
    lines = result["output"].splitlines()
    # Every line's first column should start at the same position.
    assert all(line.startswith(("USER", "root", "www-data")) for line in lines)
    assert lines[0].index("PID") == lines[1].index("1") == lines[2].index("1234")


def test_no_trailing_padding_on_last_column():
    result = align_columns("a bb\nccc d")

    for line in result["output"].splitlines():
        assert line == line.rstrip()


def test_custom_delimiter():
    result = align_columns("a,bb,c\nxx,y,zzz", delimiter=",")

    assert result["ok"] is True
    lines = result["output"].splitlines()
    assert lines[0].index("bb") == lines[1].index("y")


def test_ragged_rows_do_not_crash():
    result = align_columns("a b c\nx y")

    assert result["ok"] is True
    assert len(result["output"].splitlines()) == 2


def test_blank_lines_preserved():
    result = align_columns("a b\n\nc d")

    assert result["ok"] is True
    lines = result["output"].splitlines()
    assert lines[1] == ""


def test_rejects_empty_input():
    result = align_columns("")

    assert result["ok"] is False
    assert result["error"] == "Paste some columnar text."


def test_rejects_oversized_input():
    result = align_columns("a b\n" * 100_000)

    assert result["ok"] is False
    assert "longer than" in result["error"]
