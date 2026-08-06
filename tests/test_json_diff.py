import json

from utils.json_diff import MAX_DIFF_RESULTS, diff_json


def test_diff_json_rejects_invalid_first_document():
    result = diff_json("not json", "{}")

    assert result["ok"] is False
    assert "First JSON document is invalid" in result["error"]


def test_diff_json_rejects_invalid_second_document():
    result = diff_json("{}", "not json")

    assert result["ok"] is False
    assert "Second JSON document is invalid" in result["error"]


def test_diff_json_identical_documents():
    a = json.dumps({"a": 1, "b": [1, 2, 3]})

    result = diff_json(a, a)

    assert result["ok"] is True
    assert result["identical"] is True
    assert result["differences"] == []


def test_diff_json_key_reordering_is_not_a_difference():
    a = json.dumps({"a": 1, "b": 2})
    b = json.dumps({"b": 2, "a": 1})

    result = diff_json(a, b)

    assert result["ok"] is True
    assert result["identical"] is True


def test_diff_json_detects_added_and_removed_keys():
    a = json.dumps({"a": 1, "b": 2})
    b = json.dumps({"a": 1, "c": 3})

    result = diff_json(a, b)
    paths = {(d["path"], d["type"]) for d in result["differences"]}

    assert ("$.b", "removed") in paths
    assert ("$.c", "added") in paths


def test_diff_json_detects_changed_scalar():
    a = json.dumps({"port": 8080})
    b = json.dumps({"port": 9090})

    result = diff_json(a, b)

    assert len(result["differences"]) == 1
    entry = result["differences"][0]
    assert entry["path"] == "$.port"
    assert entry["type"] == "changed"
    assert entry["old"] == 8080
    assert entry["new"] == 9090


def test_diff_json_detects_nested_and_array_differences():
    a = json.dumps({"nested": {"tags": ["prod", "east"]}})
    b = json.dumps({"nested": {"tags": ["prod", "west", "extra"]}})

    result = diff_json(a, b)
    paths = {d["path"] for d in result["differences"]}

    assert "$.nested.tags[1]" in paths
    assert "$.nested.tags[2]" in paths


def test_diff_json_type_change_reports_as_changed():
    a = json.dumps({"value": 1})
    b = json.dumps({"value": "1"})

    result = diff_json(a, b)

    assert len(result["differences"]) == 1
    assert result["differences"][0]["type"] == "changed"


def test_diff_json_truncates_at_max_results():
    a = json.dumps({str(i): i for i in range(MAX_DIFF_RESULTS + 50)})
    b = json.dumps({})

    result = diff_json(a, b)

    assert result["ok"] is True
    assert result["truncated"] is True
    assert len(result["differences"]) == MAX_DIFF_RESULTS
