"""Merge two JSON documents per RFC 7396 (JSON Merge Patch).

Distinct from JSON Diff Viewer (compares, doesn't combine) and JSON Path
Query (extracts a value, doesn't merge documents). Useful for config
layering (a base config + an environment-specific override). Per the RFC:
a null value in the patch deletes the key from the target; any other
non-object value replaces the target's value outright; objects are merged
recursively.
"""

from __future__ import annotations

import json
from typing import Any

MAX_INPUT_LENGTH = 100_000


def _merge_patch(target: Any, patch: Any) -> Any:
    if not isinstance(patch, dict):
        return patch
    if not isinstance(target, dict):
        target = {}
    result = dict(target)
    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
        else:
            result[key] = _merge_patch(result.get(key), value)
    return result


def merge_json(target_text: str, patch_text: str) -> dict[str, Any]:
    """Apply ``patch_text`` onto ``target_text`` per RFC 7396 JSON Merge Patch."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    target_value = (target_text or "").strip()
    patch_value = (patch_text or "").strip()
    if not target_value or not patch_value:
        result["error"] = "Paste both the target JSON and the patch JSON."
        return result
    if len(target_value) > MAX_INPUT_LENGTH or len(patch_value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    try:
        target = json.loads(target_value)
    except json.JSONDecodeError as exc:
        result["error"] = f"Invalid target JSON: {exc}"
        return result
    try:
        patch = json.loads(patch_value)
    except json.JSONDecodeError as exc:
        result["error"] = f"Invalid patch JSON: {exc}"
        return result

    merged = _merge_patch(target, patch)
    result.update({"ok": True, "output": json.dumps(merged, indent=2, ensure_ascii=False)})
    return result
