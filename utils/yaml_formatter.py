"""Format/validate arbitrary YAML.

Distinct from Config Format Converter's YAML support (which only converts
a JSON-shaped object model between formats, not format/validate YAML
as-is) -- same relationship XML Formatter has to Config Format Converter's
XML support.
"""

from __future__ import annotations

from typing import Any

import yaml

MAX_INPUT_LENGTH = 100_000


def format_yaml(text: str) -> dict[str, Any]:
    """Parse and re-serialize YAML with consistent formatting."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    value = (text or "").strip()
    if not value:
        result["error"] = "Paste YAML to format."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    try:
        data = yaml.safe_load(value)
    except yaml.YAMLError as exc:
        result["error"] = f"Invalid YAML: {exc}"
        return result

    output = yaml.safe_dump(data, sort_keys=False, default_flow_style=False, allow_unicode=True)
    result.update({"ok": True, "output": output})
    return result
