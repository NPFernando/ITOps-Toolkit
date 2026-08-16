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


class _DuplicateKeyLoader(yaml.SafeLoader):
    """SafeLoader that raises on a duplicate mapping key instead of silently keeping the last value.

    Duplicate keys are invalid per the YAML spec, but PyYAML's default
    loader accepts them anyway and keeps the last value with no warning --
    the same silent-last-value-wins failure mode this app's CSV Diff Viewer
    and .env File Linter both explicitly guard against elsewhere.
    """


def _no_duplicate_keys(loader: yaml.SafeLoader, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark, f"found duplicate key {key!r}", key_node.start_mark
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_DuplicateKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicate_keys)


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
        data = yaml.load(value, Loader=_DuplicateKeyLoader)
    except yaml.YAMLError as exc:
        result["error"] = f"Invalid YAML: {exc}"
        return result

    output = yaml.safe_dump(data, sort_keys=False, default_flow_style=False, allow_unicode=True)
    result.update({"ok": True, "output": output})
    return result
