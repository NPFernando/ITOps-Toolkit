"""Extract a value from JSON using a simple dotted-path expression.

Deliberately scoped to a small, predictable subset -- dotted keys and
bracket array indices only (e.g. "user.addresses[0].city") -- not a full
JSONPath/JMESPath implementation (no wildcards, filters, or slicing), so
this stays honest about what it supports without adding a new dependency.
"""

from __future__ import annotations

import json
import re
from typing import Any

MAX_INPUT_LENGTH = 100_000
MAX_PATH_LENGTH = 500

# One path segment: a bare key, optionally followed by one or more [index]
# array accessors (e.g. "addresses[0]", "tags[1][0]").
_SEGMENT_RE = re.compile(r"^([^.\[\]]+)((?:\[\d+\])*)$")
_INDEX_RE = re.compile(r"\[(\d+)\]")


def _parse_path(path: str) -> list[str | int]:
    """Split a dotted path into a list of string keys and int indices."""
    steps: list[str | int] = []
    for raw_segment in path.split("."):
        match = _SEGMENT_RE.match(raw_segment)
        if not match:
            raise ValueError(f"Invalid path segment: '{raw_segment}'.")
        key, indices = match.groups()
        steps.append(key)
        steps.extend(int(i) for i in _INDEX_RE.findall(indices))
    return steps


def query_json_path(json_text: str, path: str) -> dict[str, Any]:
    """Evaluate a dotted-path expression against a JSON document."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    value = (json_text or "").strip()
    if not value:
        result["error"] = "Paste JSON to query."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    path = (path or "").strip().removeprefix("$.").removeprefix("$")
    if not path:
        result["error"] = "Enter a path, e.g. user.addresses[0].city."
        return result
    if len(path) > MAX_PATH_LENGTH:
        result["error"] = f"Path is longer than {MAX_PATH_LENGTH:,} characters."
        return result

    try:
        data = json.loads(value)
    except json.JSONDecodeError as exc:
        result["error"] = f"Invalid JSON: {exc}"
        return result

    try:
        steps = _parse_path(path)
    except ValueError as exc:
        result["error"] = str(exc)
        return result

    current = data
    walked = ""
    for step in steps:
        walked = f"{walked}[{step}]" if isinstance(step, int) else f"{walked}.{step}" if walked else str(step)
        if isinstance(step, str):
            if not isinstance(current, dict):
                result["error"] = f"'{walked}' expects an object, but the value at that point is {type(current).__name__}."
                return result
            if step not in current:
                result["error"] = f"Key '{step}' not found at '{walked}'."
                return result
            current = current[step]
        else:
            if not isinstance(current, list):
                result["error"] = f"'{walked}' expects an array, but the value at that point is {type(current).__name__}."
                return result
            if not (0 <= step < len(current)):
                result["error"] = f"Index {step} out of range at '{walked}' (length {len(current)})."
                return result
            current = current[step]

    if isinstance(current, (dict, list)):
        output = json.dumps(current, indent=2, ensure_ascii=False)
    else:
        output = json.dumps(current, ensure_ascii=False)

    result.update({"ok": True, "output": output})
    return result
