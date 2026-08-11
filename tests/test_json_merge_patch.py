from __future__ import annotations

import json

from utils.json_merge_patch import merge_json


def test_replaces_scalar_value():
    result = merge_json('{"a": "b"}', '{"a": "c"}')

    assert result["ok"] is True
    assert json.loads(result["output"]) == {"a": "c"}


def test_adds_new_key():
    result = merge_json('{"a": "b"}', '{"b": "c"}')

    assert json.loads(result["output"]) == {"a": "b", "b": "c"}


def test_null_deletes_key():
    result = merge_json('{"a": "b", "b": "c"}', '{"a": null}')

    assert json.loads(result["output"]) == {"b": "c"}


def test_nested_objects_merge_recursively():
    result = merge_json('{"a": {"b": "c"}}', '{"a": {"b": "d", "c": null}}')

    assert json.loads(result["output"]) == {"a": {"b": "d"}}


def test_arrays_are_replaced_not_merged():
    result = merge_json('{"a": [{"b": "c"}]}', '{"a": [1]}')

    assert json.loads(result["output"]) == {"a": [1]}


def test_patch_scalar_replaces_whole_target():
    result = merge_json('{"a": "foo"}', '"bar"')

    assert json.loads(result["output"]) == "bar"


def test_official_rfc_example_empty_object_nested_delete():
    # RFC 7396 Appendix A: deleting the only key of a nested object leaves
    # an empty object, not an absent key.
    result = merge_json("{}", '{"a": {"bb": {"ccc": null}}}')

    assert json.loads(result["output"]) == {"a": {"bb": {}}}


def test_rejects_invalid_target_json():
    result = merge_json("{not valid", "{}")

    assert result["ok"] is False
    assert "Invalid target JSON" in result["error"]


def test_rejects_invalid_patch_json():
    result = merge_json("{}", "{not valid")

    assert result["ok"] is False
    assert "Invalid patch JSON" in result["error"]


def test_rejects_empty_input():
    result = merge_json("", "{}")

    assert result["ok"] is False
    assert "Paste both" in result["error"]
