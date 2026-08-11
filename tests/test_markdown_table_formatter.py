from __future__ import annotations

from utils.markdown_table_formatter import format_markdown_table


def test_realigns_ragged_columns():
    raw = "| Name | Age |\n|---|---|\n| Alice | 30 |\n| Bob | 25 |"
    result = format_markdown_table(raw)

    assert result["ok"] is True
    assert result["output"] == "| Name  | Age |\n| ----- | --- |\n| Alice | 30  |\n| Bob   | 25  |"


def test_preserves_alignment_markers():
    raw = "| Name | Age | City |\n|---|:---:|---:|\n| Alice | 30 | NYC |\n| Bob | 25 | Los Angeles |"
    result = format_markdown_table(raw)

    assert result["ok"] is True
    lines = result["output"].splitlines()
    assert lines[1] == "| ----- | :-: | ----------: |"
    # Right-aligned column: values should be right-justified.
    assert lines[2].split("|")[3].strip() == "NYC"
    assert lines[2].endswith("NYC |")


def test_escaped_pipe_inside_cell_round_trips():
    # Regression: CSV to Markdown Table's own _escape_cell() produces "\|"
    # for a literal pipe inside a cell -- a table built by that tool must
    # still parse correctly here, not get misread as an extra column.
    raw = r"| Name | Note |" "\n" r"|---|---|" "\n" r"| Alice | a \| b |"
    result = format_markdown_table(raw)

    assert result["ok"] is True
    assert r"a \| b" in result["output"]


def test_rejects_missing_separator_row():
    result = format_markdown_table("| Name | Age |")

    assert result["ok"] is False
    assert "header row and a separator row" in result["error"]


def test_rejects_invalid_separator_row():
    result = format_markdown_table("| Name | Age |\n| foo | bar |")

    assert result["ok"] is False
    assert "valid separator row" in result["error"]


def test_rejects_ragged_body_row():
    result = format_markdown_table("| a | b |\n|---|---|\n| 1 |")

    assert result["ok"] is False
    assert "Every row must have" in result["error"]


def test_rejects_empty_input():
    result = format_markdown_table("")

    assert result["ok"] is False


def test_header_only_table_with_no_body_rows():
    result = format_markdown_table("| a | b |\n|---|---|")

    assert result["ok"] is True
    assert result["output"] == "| a   | b   |\n| --- | --- |"
