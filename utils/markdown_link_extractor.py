"""Extract every link from Markdown text: [text](url) inline links, reference-style
links ([text][ref] plus its [ref]: url definition), and bare autolinks (<https://...>).

Distinct from Text Pattern Extractor (a generic user-supplied regex, no
Markdown-specific link syntax awareness) and Markdown TOC Generator
(headings, not links).
"""

from __future__ import annotations

import re
from typing import Any

MAX_INPUT_LENGTH = 200_000

_INLINE_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_REFERENCE_USE_RE = re.compile(r"(?<!!)\[([^\]]*)\]\[([^\]]*)\]")
_REFERENCE_DEF_RE = re.compile(r"^\s*\[([^\]]+)\]:\s*(\S+)", re.MULTILINE)
_AUTOLINK_RE = re.compile(r"<((?:https?|ftp)://[^\s<>]+)>")


def extract_links(markdown_text: str) -> dict[str, Any]:
    """Extract all Markdown links (inline, reference-style, and autolinks) with their text and URL."""
    result: dict[str, Any] = {"ok": False, "error": None, "links": None}

    value = markdown_text or ""
    if not value.strip():
        result["error"] = "Paste some Markdown text."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    links: list[dict[str, str]] = []

    for match in _INLINE_LINK_RE.finditer(value):
        links.append({"text": match.group(1), "url": match.group(2), "type": "inline"})

    references = {ref.lower(): url for ref, url in _REFERENCE_DEF_RE.findall(value)}
    for match in _REFERENCE_USE_RE.finditer(value):
        text, ref = match.group(1), match.group(2)
        ref_key = (ref or text).lower()
        url = references.get(ref_key)
        if url is not None:
            links.append({"text": text, "url": url, "type": "reference"})

    for match in _AUTOLINK_RE.finditer(value):
        links.append({"text": match.group(1), "url": match.group(1), "type": "autolink"})

    if not links:
        result["error"] = "No links found."
        return result

    result.update({"ok": True, "links": links})
    return result
