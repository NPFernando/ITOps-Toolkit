"""Infer a TypeScript interface (or interfaces) from a JSON document.

Distinct from JSON Formatter (pretty-print, no type inference) and Config
Format Converter (converts between data-serialization formats, not to a
type system). Nested objects get their own named interface; arrays infer
their element type. An empty array's element type can't be inferred from
the data alone, so it's typed unknown[] rather than guessed.
"""

from __future__ import annotations

import json
import re
from typing import Any

MAX_INPUT_LENGTH = 100_000

_INVALID_IDENTIFIER_CHARS_RE = re.compile(r"[^A-Za-z0-9_$]")


def _pascal_case(name: str) -> str:
    words = re.split(r"[^A-Za-z0-9]+", name)
    return "".join(word[:1].upper() + word[1:] for word in words if word) or "Root"


def _field_name(key: str) -> str:
    if re.match(r"^[A-Za-z_$][A-Za-z0-9_$]*$", key):
        return key
    return json.dumps(key)


def _infer_type(value: Any, interface_name: str, interfaces: dict[str, str]) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        if not value:
            return "unknown[]"
        element_types = sorted({_infer_type(item, f"{interface_name}Item", interfaces) for item in value})
        element_type = element_types[0] if len(element_types) == 1 else f"({' | '.join(element_types)})"
        return f"{element_type}[]"
    if isinstance(value, dict):
        _build_interface(value, interface_name, interfaces)
        return interface_name
    return "unknown"


def _build_interface(obj: dict[str, Any], name: str, interfaces: dict[str, str]) -> None:
    lines = [f"interface {name} {{"]
    for key, value in obj.items():
        nested_name = f"{name}{_pascal_case(key)}"
        field_type = _infer_type(value, nested_name, interfaces)
        lines.append(f"  {_field_name(key)}: {field_type};")
    lines.append("}")
    interfaces[name] = "\n".join(lines)


def json_to_typescript(json_text: str, root_name: str = "Root") -> dict[str, Any]:
    """Generate TypeScript interface(s) from a JSON document."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    value = (json_text or "").strip()
    if not value:
        result["error"] = "Paste JSON to convert."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    try:
        data = json.loads(value)
    except json.JSONDecodeError as exc:
        result["error"] = f"Invalid JSON: {exc}"
        return result

    root_name = _pascal_case((root_name or "Root").strip() or "Root")
    interfaces: dict[str, str] = {}

    if isinstance(data, dict):
        _build_interface(data, root_name, interfaces)
    elif isinstance(data, list):
        element_type = _infer_type(data[0] if data else None, f"{root_name}Item", interfaces) if data else "unknown"
        interfaces[root_name] = f"type {root_name} = {element_type}[];"
    else:
        result["error"] = "Top-level JSON must be an object or array to generate an interface."
        return result

    # Interfaces referencing other interfaces should read top-down: emit the
    # root first, then whatever nested interfaces were discovered after it.
    ordered = [interfaces.pop(root_name)] + list(interfaces.values())
    result.update({"ok": True, "output": "\n\n".join(ordered)})
    return result
