from __future__ import annotations

from utils.yaml_formatter import format_yaml


def test_format_yaml_basic():
    result = format_yaml("a: 1\nb:\n  - x\n  - y\n")

    assert result["ok"] is True
    assert result["output"] == "a: 1\nb:\n- x\n- y\n"


def test_format_yaml_scalar_top_level():
    result = format_yaml("just a scalar string")

    assert result["ok"] is True
    assert "just a scalar string" in result["output"]


def test_format_yaml_rejects_malformed_yaml():
    result = format_yaml("a: [1,2\n")

    assert result["ok"] is False
    assert "Invalid YAML" in result["error"]


def test_format_yaml_rejects_empty_input():
    result = format_yaml("")

    assert result["ok"] is False
    assert result["error"] == "Paste YAML to format."


def test_format_yaml_rejects_oversized_input():
    result = format_yaml("a: " + "x" * 100_001)

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_format_yaml_null_document():
    result = format_yaml("null")

    assert result["ok"] is True
    assert "null" in result["output"]


def test_format_yaml_rejects_duplicate_top_level_key():
    # Regression: PyYAML's default loader silently keeps the last value for
    # a duplicate mapping key with no warning -- invalid per the YAML spec,
    # and inconsistent with this page's own stated promise to flag invalid
    # YAML with a clear error.
    result = format_yaml("a: 1\na: 2\n")

    assert result["ok"] is False
    assert "duplicate key" in result["error"]


def test_format_yaml_rejects_duplicate_nested_key():
    result = format_yaml("a:\n  x: 1\n  x: 2\n")

    assert result["ok"] is False
    assert "duplicate key" in result["error"]


def test_format_yaml_allows_non_duplicate_keys():
    result = format_yaml("a: 1\nb: 2\n")

    assert result["ok"] is True
