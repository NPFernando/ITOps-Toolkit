from __future__ import annotations

from utils.csv_diff import diff_csv

CSV_A = "id,name,status\n1,Alice,active\n2,Bob,active\n3,Carol,inactive\n"
CSV_B = "id,name,status\n1,Alice,active\n2,Bob,inactive\n4,Dave,active\n"


def test_diff_csv_classifies_added_removed_changed():
    result = diff_csv(CSV_A, CSV_B, "id")

    assert result["ok"] is True
    by_key = {d["key"]: d for d in result["differences"]}
    assert by_key["3"]["type"] == "removed"
    assert by_key["4"]["type"] == "added"
    assert by_key["2"]["type"] == "changed"
    assert by_key["2"]["fields"]["status"] == {"old": "active", "new": "inactive"}
    assert "1" not in by_key


def test_diff_csv_identical_when_no_differences():
    result = diff_csv(CSV_A, CSV_A, "id")

    assert result["ok"] is True
    assert result["identical"] is True
    assert result["differences"] == []


def test_diff_csv_rejects_missing_key_column():
    result = diff_csv(CSV_A, CSV_B, "")

    assert result["ok"] is False
    assert "Enter the key column" in result["error"]


def test_diff_csv_rejects_key_column_not_in_headers():
    result = diff_csv(CSV_A, CSV_B, "nonexistent")

    assert result["ok"] is False
    assert "was not found" in result["error"]


def test_diff_csv_rejects_empty_input():
    result = diff_csv("", CSV_B, "id")

    assert result["ok"] is False
    assert "header row" in result["error"]


def test_diff_csv_rejects_oversized_input():
    huge = "id,name\n" + "1,x\n" * 100_000
    result = diff_csv(huge, CSV_B, "id")

    assert result["ok"] is False
    assert "longer than" in result["error"]
