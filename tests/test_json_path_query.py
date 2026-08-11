from __future__ import annotations

import json

from utils.json_path_query import query_json_path


DOC = json.dumps({"user": {"name": "Alice", "addresses": [{"city": "NYC"}, {"city": "LA"}], "active": True, "meta": None}})


def test_query_nested_key():
    result = query_json_path(DOC, "user.name")

    assert result["ok"] is True
    assert result["output"] == '"Alice"'


def test_query_array_index():
    result = query_json_path(DOC, "user.addresses[0].city")

    assert result["ok"] is True
    assert result["output"] == '"NYC"'


def test_query_returns_object_pretty_printed():
    result = query_json_path(DOC, "user.addresses[1]")

    assert result["ok"] is True
    assert json.loads(result["output"]) == {"city": "LA"}


def test_query_boolean_and_null_values():
    assert query_json_path(DOC, "user.active")["output"] == "true"
    assert query_json_path(DOC, "user.meta")["output"] == "null"


def test_query_accepts_dollar_prefix():
    result = query_json_path(DOC, "$.user.name")

    assert result["ok"] is True
    assert result["output"] == '"Alice"'


def test_query_rejects_missing_key():
    result = query_json_path(DOC, "user.bogus")

    assert result["ok"] is False
    assert "not found" in result["error"]


def test_query_rejects_out_of_range_index():
    result = query_json_path(DOC, "user.addresses[5]")

    assert result["ok"] is False
    assert "out of range" in result["error"]


def test_query_rejects_indexing_a_non_array():
    result = query_json_path(DOC, "user.name[0]")

    assert result["ok"] is False
    assert "expects an array" in result["error"]


def test_query_rejects_keying_a_non_object():
    result = query_json_path(DOC, "user.name.bogus")

    assert result["ok"] is False
    assert "expects an object" in result["error"]


def test_query_root_level_array_index():
    # Regression: a bare "[0]" path segment (no leading key -- e.g. for a
    # top-level JSON array, which has no object key to index through
    # first) used to be rejected as an "Invalid path segment" even though
    # bracket-index syntax is otherwise supported.
    result = query_json_path('[{"a": 1}, {"a": 2}]', "[0]")

    assert result["ok"] is True
    assert json.loads(result["output"]) == {"a": 1}


def test_query_root_level_array_index_then_key():
    result = query_json_path('[{"a": 1}, {"a": 2}]', "[1].a")

    assert result["ok"] is True
    assert result["output"] == "2"


def test_query_rejects_truly_empty_segment():
    result = query_json_path('{"a": 1}', "a..b")

    assert result["ok"] is False
    assert "Invalid path segment" in result["error"]


def test_query_rejects_empty_path():
    result = query_json_path(DOC, "")

    assert result["ok"] is False
    assert "Enter a path" in result["error"]


def test_query_rejects_invalid_json():
    result = query_json_path("{not valid", "a")

    assert result["ok"] is False
    assert "Invalid JSON" in result["error"]


def test_query_rejects_empty_input():
    result = query_json_path("", "a")

    assert result["ok"] is False
    assert result["error"] == "Paste JSON to query."
