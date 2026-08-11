from __future__ import annotations

from utils.csv_cleaner import clean_csv


def test_trims_cell_whitespace():
    result = clean_csv("name, age \n Alice , 30")

    assert result["ok"] is True
    assert result["output"] == "name,age\nAlice,30\n"


def test_drops_empty_rows():
    result = clean_csv("a,b\n1,2\n,\n3,4")

    assert result["ok"] is True
    assert result["output"] == "a,b\n1,2\n3,4\n"
    assert result["removed_count"] == 1


def test_dedupes_exact_duplicate_rows():
    result = clean_csv("a,b\n1,2\n1,2\n3,4", dedupe_rows=True)

    assert result["ok"] is True
    assert result["output"] == "a,b\n1,2\n3,4\n"
    # row_count includes the header row, like every other row.
    assert result["row_count"] == 3


def test_no_options_leaves_content_as_is_besides_reformatting():
    result = clean_csv("a,b\n1,2", trim_cells=False, drop_empty_rows=False)

    assert result["ok"] is True
    assert result["output"] == "a,b\n1,2\n"


def test_rejects_empty_input():
    result = clean_csv("")

    assert result["ok"] is False
    assert result["error"] == "Paste CSV or TSV text to clean."


def test_rejects_oversized_input():
    result = clean_csv("a" * 200_001)

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_all_rows_empty_after_cleaning_is_an_error():
    result = clean_csv(",\n,\n", drop_empty_rows=True)

    assert result["ok"] is False
    assert "Nothing left" in result["error"]


def test_tsv_delimiter():
    result = clean_csv("a\tb\n1 \t2", delimiter="\t")

    assert result["ok"] is True
    assert result["output"] == "a\tb\n1\t2\n"
