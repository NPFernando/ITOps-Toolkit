"""Convert a config snippet between JSON, YAML, TOML, and XML.

JSON/YAML/TOML all map onto the same Python dict/list/scalar model, so
those three convert losslessly between each other (modulo TOML's own
restrictions -- no top-level list, no null values). XML has no such
standard mapping onto that model, so this module uses one explicit,
simple convention (documented on the page): each dict key becomes a
child element named after the key; a list becomes repeated sibling
elements with the same tag; a scalar becomes element text. This is a
reasonable, commonly-used convention (the same shape python-xmltodict
uses), not a universal XML/JSON equivalence -- attributes, mixed
text+children content, comments, and namespaces are not represented.
"""

from __future__ import annotations

import json
from typing import Any
from xml.etree import ElementTree as ET

import toml
import yaml


FORMATS: tuple[str, ...] = ("JSON", "YAML", "TOML", "XML")
MAX_INPUT_LENGTH = 100_000


class _DuplicateKeyLoader(yaml.SafeLoader):
    """SafeLoader that raises on a duplicate mapping key instead of silently keeping the last value.

    Duplicate keys are invalid per the YAML spec, but PyYAML's default
    loader accepts them anyway and keeps the last value with no warning.
    """


def _no_duplicate_keys(loader: yaml.SafeLoader, node: Any, deep: bool = False) -> dict[Any, Any]:
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


def _dict_to_xml(data: Any, tag: str) -> ET.Element:
    element = ET.Element(tag)
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    element.append(_dict_to_xml(item, str(key)))
            else:
                element.append(_dict_to_xml(value, str(key)))
    elif isinstance(data, list):
        for item in data:
            element.append(_dict_to_xml(item, "item"))
    else:
        element.text = "" if data is None else str(data)
    return element


def _xml_to_dict(element: ET.Element) -> Any:
    children = list(element)
    if not children:
        return element.text.strip() if element.text and element.text.strip() else None

    result: dict[str, Any] = {}
    for child in children:
        value = _xml_to_dict(child)
        if child.tag in result:
            existing = result[child.tag]
            if isinstance(existing, list):
                existing.append(value)
            else:
                result[child.tag] = [existing, value]
        else:
            result[child.tag] = value
    return result


def _parse(text: str, fmt: str) -> Any:
    if fmt == "JSON":
        return json.loads(text)
    if fmt == "YAML":
        return yaml.load(text, Loader=_DuplicateKeyLoader)
    if fmt == "TOML":
        return toml.loads(text)
    if fmt == "XML":
        root = ET.fromstring(text)
        return {root.tag: _xml_to_dict(root)}
    raise ValueError(f"Unsupported source format: {fmt}")


def _serialize(data: Any, fmt: str) -> str:
    if fmt == "JSON":
        return json.dumps(data, indent=2, ensure_ascii=False)
    if fmt == "YAML":
        return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    if fmt == "TOML":
        if not isinstance(data, dict):
            raise ValueError("TOML requires a top-level object/mapping, not a list or scalar.")
        return toml.dumps(data)
    if fmt == "XML":
        if isinstance(data, dict) and len(data) == 1:
            (root_tag, root_value), = data.items()
        else:
            root_tag, root_value = "root", data
        element = _dict_to_xml(root_value, str(root_tag))
        ET.indent(element)
        return ET.tostring(element, encoding="unicode")
    raise ValueError(f"Unsupported target format: {fmt}")


def convert_config(text: str, from_format: str, to_format: str) -> dict[str, Any]:
    """Parse ``text`` as ``from_format`` and re-serialize it as ``to_format``."""
    result: dict[str, Any] = {"ok": False, "output": "", "error": None}

    if from_format not in FORMATS or to_format not in FORMATS:
        result["error"] = f"Formats must be one of: {', '.join(FORMATS)}."
        return result
    if not (text or "").strip():
        result["error"] = "Enter some config text to convert."
        return result
    if len(text) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH} characters."
        return result

    try:
        data = _parse(text, from_format)
    except Exception as exc:
        result["error"] = f"Could not parse input as {from_format}: {exc}"
        return result

    try:
        output = _serialize(data, to_format)
    except Exception as exc:
        result["error"] = f"Could not convert to {to_format}: {exc}"
        return result

    result.update({"ok": True, "output": output})
    return result
