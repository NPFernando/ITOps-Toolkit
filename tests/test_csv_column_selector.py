from __future__ import annotations

from utils.csv_column_selector import select_columns


def test_selects_and_reorders_columns():
    result = select_columns("name,age,city\nAlice,30,NYC\nBob,25,LA", "city, name")

    assert result["ok"] is True
    assert result["output"] == "city,name\nNYC,Alice\nLA,Bob\n"


def test_rejects_missing_column():
    result = select_columns("a,b\n1,2", "c")

    assert result["ok"] is False
    assert "not found in header" in result["error"]


def test_rejects_duplicate_header():
    result = select_columns("a,a\n1,2", "a")

    assert result["ok"] is False
    assert "duplicate" in result["error"].lower()


def test_pads_ragged_row():
    result = select_columns("a,b,c\n1,2", "a,c")

    assert result["ok"] is True
    assert result["output"] == "a,c\n1,\n"


def test_rejects_empty_columns_input():
    result = select_columns("a,b\n1,2", "")

    assert result["ok"] is False
    assert "Enter at least one column" in result["error"]


def test_rejects_empty_csv_input():
    result = select_columns("", "a")

    assert result["ok"] is False


def test_tsv_delimiter():
    result = select_columns("a\tb\n1\t2", "b", delimiter="\t")

    assert result["ok"] is True
    assert result["output"] == "b\n2\n"
