"""Encode/decode HTML entities (&lt;, &amp;, &quot;, numeric character references, etc.)."""

from __future__ import annotations

import html
from typing import Any

MAX_INPUT_LENGTH = 20_000


def encode_html_entities(value: str) -> str:
    return html.escape(value or "", quote=True)


def decode_html_entities(value: str) -> dict[str, Any]:
    result: dict[str, Any] = {"ok": False, "error": None, "result": None}
    if len(value or "") > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result
    if not (value or ""):
        result["error"] = "Enter HTML-entity-encoded text to decode."
        return result

    # html.unescape never raises -- unrecognized entities are left as-is,
    # unlike Base64/Base32 decode which can fail on malformed input.
    result.update({"ok": True, "result": html.unescape(value)})
    return result
