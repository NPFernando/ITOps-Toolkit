from __future__ import annotations

from utils.csv_to_markdown import convert_csv_to_markdown


def test_convert_csv_to_markdown_basic():
    result = convert_csv_to_markdown("name,age\nAlice,30\nBob,25")

    assert result["ok"] is True
    assert result["output"] == "| name | age |\n| --- | --- |\n| Alice | 30 |\n| Bob | 25 |"


def test_convert_csv_to_markdown_tsv_delimiter():
    result = convert_csv_to_markdown("name\tage\nAlice\t30", delimiter="\t")

    assert result["ok"] is True
    assert result["output"] == "| name | age |\n| --- | --- |\n| Alice | 30 |"


def test_convert_csv_to_markdown_escapes_pipe_characters():
    result = convert_csv_to_markdown("name,note\nAlice,likes | pipes")

    assert result["ok"] is True
    assert "likes \\| pipes" in result["output"]


def test_convert_csv_to_markdown_pads_ragged_short_row():
    result = convert_csv_to_markdown("name,age\nAlice,30\nBob")

    assert result["ok"] is True
    assert "| Bob |  |" in result["output"]


def test_convert_csv_to_markdown_truncates_ragged_long_row():
    result = convert_csv_to_markdown("name,age\nAlice,30,extra")

    assert result["ok"] is True
    assert "extra" not in result["output"]


def test_convert_csv_to_markdown_rejects_empty_input():
    result = convert_csv_to_markdown("")

    assert result["ok"] is False
    assert result["error"] == "Paste CSV or TSV text to convert."


def test_convert_csv_to_markdown_rejects_oversized_input():
    result = convert_csv_to_markdown("a" * 100_001)

    assert result["ok"] is False
    assert "longer than" in result["error"]
