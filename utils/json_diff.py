"""Structural (key-aware) JSON diff, complementing the line-based Text Diff Checker."""

from __future__ import annotations

import json
from typing import Any

from utils.text_tools import MAX_JSON_LENGTH, validate_length


MAX_DIFF_RESULTS = 500


def _path_str(path: list[Any]) -> str:
    if not path:
        return "$"
    parts = ["$"]
    for key in path:
        parts.append(f"[{key}]" if isinstance(key, int) else f".{key}")
    return "".join(parts)


def _diff_values(a: Any, b: Any) -> list[dict[str, Any]]:
    """Iteratively diff two parsed JSON values, capped at MAX_DIFF_RESULTS entries.

    Walks with an explicit stack (not recursion) for the same reason
    utils.text_tools.json_stats does: a short but deeply-nested JSON string can
    exceed Python's recursion limit even though it's well under MAX_JSON_LENGTH.
    """
    differences: list[dict[str, Any]] = []
    stack: list[tuple[list[Any], Any, Any]] = [([], a, b)]

    while stack and len(differences) < MAX_DIFF_RESULTS:
        path, left, right = stack.pop()

        if isinstance(left, dict) and isinstance(right, dict):
            for key in left:
                if key not in right:
                    differences.append({"path": _path_str([*path, key]), "type": "removed", "old": left[key], "new": None})
                else:
                    stack.append(([*path, key], left[key], right[key]))
            for key in right:
                if key not in left:
                    differences.append({"path": _path_str([*path, key]), "type": "added", "old": None, "new": right[key]})
        elif isinstance(left, list) and isinstance(right, list):
            for index in range(max(len(left), len(right))):
                if index >= len(left):
                    differences.append({"path": _path_str([*path, index]), "type": "added", "old": None, "new": right[index]})
                elif index >= len(right):
                    differences.append({"path": _path_str([*path, index]), "type": "removed", "old": left[index], "new": None})
                else:
                    stack.append(([*path, index], left[index], right[index]))
        elif left != right:
            differences.append({"path": _path_str(path), "type": "changed", "old": left, "new": right})

    return differences


def diff_json(text_a: str, text_b: str) -> dict[str, Any]:
    """Parse two JSON documents and return their structural differences."""
    result: dict[str, Any] = {"ok": False, "differences": [], "truncated": False, "identical": False, "error": None}

    ok_a, error_a = validate_length(text_a, MAX_JSON_LENGTH, "First JSON document")
    if not ok_a:
        result["error"] = error_a
        return result
    ok_b, error_b = validate_length(text_b, MAX_JSON_LENGTH, "Second JSON document")
    if not ok_b:
        result["error"] = error_b
        return result

    try:
        parsed_a = json.loads(text_a)
    except json.JSONDecodeError as exc:
        result["error"] = f"First JSON document is invalid: {exc}"
        return result
    try:
        parsed_b = json.loads(text_b)
    except json.JSONDecodeError as exc:
        result["error"] = f"Second JSON document is invalid: {exc}"
        return result

    differences = _diff_values(parsed_a, parsed_b)
    result.update(
        {
            "ok": True,
            "differences": differences[:MAX_DIFF_RESULTS],
            "truncated": len(differences) >= MAX_DIFF_RESULTS,
            "identical": not differences,
        }
    )
    return result
