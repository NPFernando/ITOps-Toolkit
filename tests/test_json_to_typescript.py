from __future__ import annotations

import json

from utils.json_to_typescript import json_to_typescript


def test_flat_object():
    result = json_to_typescript(json.dumps({"name": "Alice", "age": 30, "active": True, "nickname": None}))

    assert result["ok"] is True
    assert "name: string;" in result["output"]
    assert "age: number;" in result["output"]
    assert "active: boolean;" in result["output"]
    assert "nickname: null;" in result["output"]


def test_nested_object_becomes_own_interface():
    result = json_to_typescript(json.dumps({"address": {"city": "NYC"}}))

    assert "address: RootAddress;" in result["output"]
    assert "interface RootAddress {" in result["output"]
    assert "city: string;" in result["output"]


def test_array_of_strings():
    result = json_to_typescript(json.dumps({"tags": ["a", "b"]}))

    assert "tags: string[];" in result["output"]


def test_mixed_type_array_becomes_union():
    result = json_to_typescript(json.dumps({"mixed": [1, "a"]}))

    assert "mixed: (number | string)[];" in result["output"]


def test_empty_array_is_unknown():
    result = json_to_typescript(json.dumps({"empty": []}))

    assert "empty: unknown[];" in result["output"]


def test_top_level_array_of_objects():
    result = json_to_typescript(json.dumps([{"id": 1}, {"id": 2}]))

    assert result["ok"] is True
    assert "type Root = RootItem[];" in result["output"]
    assert "interface RootItem {" in result["output"]
    assert "id: number;" in result["output"]


def test_field_name_needing_quotes():
    result = json_to_typescript(json.dumps({"user-name": "Alice"}))

    assert '"user-name": string;' in result["output"]


def test_custom_root_name():
    result = json_to_typescript(json.dumps({"a": 1}), root_name="MyType")

    assert "interface MyType {" in result["output"]


def test_rejects_scalar_top_level():
    result = json_to_typescript("42")

    assert result["ok"] is False
    assert "object or array" in result["error"]


def test_rejects_invalid_json():
    result = json_to_typescript("{not valid")

    assert result["ok"] is False
    assert "Invalid JSON" in result["error"]


def test_rejects_empty_input():
    result = json_to_typescript("")

    assert result["ok"] is False
