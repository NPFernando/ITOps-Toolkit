"""Pretty-print, minify, or validate arbitrary XML.

Distinct from JSON Formatter and Config Format Converter's XML support
(which only converts a JSON-shaped object model to a simple XML convention,
not general XML with attributes/mixed content/namespaces) -- this formats
or validates arbitrary XML as-is.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any
from xml.dom import minidom
from xml.parsers.expat import ExpatError

MAX_INPUT_LENGTH = 100_000


def format_xml(text: str, minify: bool = False) -> dict[str, Any]:
    """Validate ``text`` as XML, and either pretty-print or minify it."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    value = (text or "").strip()
    if not value:
        result["error"] = "Paste XML to format."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    if minify:
        try:
            root = ET.fromstring(value)
        except ET.ParseError as exc:
            result["error"] = f"Invalid XML: {exc}"
            return result
        result.update({"ok": True, "output": ET.tostring(root, encoding="unicode")})
        return result

    try:
        parsed = minidom.parseString(value)
    except ExpatError as exc:
        result["error"] = f"Invalid XML: {exc}"
        return result

    pretty = parsed.toprettyxml(indent="  ")
    # toprettyxml() leaves blank lines from whitespace-only text nodes between
    # elements -- strip them for clean, consistent output.
    cleaned = "\n".join(line for line in pretty.splitlines() if line.strip())
    result.update({"ok": True, "output": cleaned})
    return result
