from __future__ import annotations

import csv
import io
import json

from utils.csv_json_converter import csv_to_json, json_to_csv


def test_csv_to_json_basic():
    result = csv_to_json("name,age\nAlice,30\nBob,25")

    assert result["ok"] is True
    assert json.loads(result["output"]) == [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]


def test_csv_to_json_pads_ragged_row():
    result = csv_to_json("a,b,c\n1,2")

    assert result["ok"] is True
    assert json.loads(result["output"]) == [{"a": "1", "b": "2", "c": ""}]


def test_csv_to_json_rejects_duplicate_header():
    result = csv_to_json("a,a\n1,2")

    assert result["ok"] is False
    assert "duplicate" in result["error"].lower()


def test_csv_to_json_rejects_empty_input():
    result = csv_to_json("")

    assert result["ok"] is False
    assert result["error"] == "Paste CSV or TSV text to convert."


def test_csv_to_json_tsv_delimiter():
    result = csv_to_json("name\tage\nAlice\t30", delimiter="\t")

    assert result["ok"] is True
    assert json.loads(result["output"]) == [{"name": "Alice", "age": "30"}]


def test_json_to_csv_basic():
    result = json_to_csv(json.dumps([{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]))

    assert result["ok"] is True
    assert result["output"] == "name,age\nAlice,30\nBob,25\n"


def test_json_to_csv_union_of_keys():
    result = json_to_csv(json.dumps([{"a": 1}, {"b": 2}]))

    assert result["ok"] is True
    assert result["output"] == "a,b\n1,\n,2\n"


def test_json_to_csv_rejects_non_array():
    result = json_to_csv(json.dumps({"a": 1}))

    assert result["ok"] is False
    assert "array" in result["error"].lower()


def test_json_to_csv_rejects_non_object_elements():
    result = json_to_csv(json.dumps([1, 2, 3]))

    assert result["ok"] is False
    assert "object" in result["error"].lower()


def test_json_to_csv_rejects_invalid_json():
    result = json_to_csv("{not valid json")

    assert result["ok"] is False
    assert "Invalid JSON" in result["error"]


def test_json_to_csv_serializes_nested_values():
    result = json_to_csv(json.dumps([{"tags": ["a", "b"]}]))

    assert result["ok"] is True
    # CSV-quoted (the JSON-serialized cell contains commas), so parse it back
    # rather than checking for a literal substring.
    rows = list(csv.reader(io.StringIO(result["output"])))
    assert rows[1][0] == '["a", "b"]'


def test_round_trip_csv_to_json_to_csv():
    original = "name,age\nAlice,30\nBob,25\n"
    to_json = csv_to_json(original)
    back_to_csv = json_to_csv(to_json["output"])

    assert back_to_csv["ok"] is True
    assert back_to_csv["output"] == original
