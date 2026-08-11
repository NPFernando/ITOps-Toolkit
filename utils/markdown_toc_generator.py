"""Generate a linked table of contents from Markdown ATX headings.

Anchor slugs follow GitHub's algorithm (lowercase, strip characters that
aren't a word character/space/hyphen, spaces -> hyphens, duplicate slugs
get a -1/-2/... suffix) -- verified directly against GitHub's actual
rendered anchors for headings with punctuation and duplicates before
shipping. Only ATX-style (#, ##, ...) headings are recognized, not
Setext-style (underlined with ===/---).
"""

from __future__ import annotations

import re
from typing import Any

MAX_INPUT_LENGTH = 200_000

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
# A closing ATX sequence ("## Heading ##") must be preceded by whitespace
# per CommonMark -- a heading that genuinely ends in "#" (e.g. "## C#")
# must not have that trailing "#" stripped.
_CLOSING_HASHES_RE = re.compile(r"^(.*\S)\s+#+$")
_SLUG_STRIP_RE = re.compile(r"[^\w\s-]")
_SLUG_SPACE_RE = re.compile(r"\s+")


def _slugify(heading_text: str, used: dict[str, int]) -> str:
    slug = heading_text.lower()
    slug = _SLUG_STRIP_RE.sub("", slug)
    slug = _SLUG_SPACE_RE.sub("-", slug.strip())
    count = used.get(slug, 0)
    used[slug] = count + 1
    return slug if count == 0 else f"{slug}-{count}"


def generate_toc(markdown_text: str, min_level: int = 1, max_level: int = 6) -> dict[str, Any]:
    """Extract ATX headings and build a nested, linked table of contents."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None, "heading_count": 0}

    value = markdown_text or ""
    if not value.strip():
        result["error"] = "Paste Markdown text with headings."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    in_fenced_code = False
    used_slugs: dict[str, int] = {}
    lines_out = []
    heading_count = 0

    for raw_line in value.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            # Headings inside fenced code blocks are literal text, not
            # real headings -- a bare "# comment" in a bash snippet
            # shouldn't end up in the TOC.
            in_fenced_code = not in_fenced_code
            continue
        if in_fenced_code:
            continue

        match = _HEADING_RE.match(raw_line)
        if not match:
            continue
        level = len(match.group(1))
        if not (min_level <= level <= max_level):
            continue
        raw_text = match.group(2).rstrip()
        closing_match = _CLOSING_HASHES_RE.match(raw_text)
        text = closing_match.group(1) if closing_match else raw_text
        if not text:
            continue

        slug = _slugify(text, used_slugs)
        indent = "  " * (level - min_level)
        lines_out.append(f"{indent}- [{text}](#{slug})")
        heading_count += 1

    if heading_count == 0:
        result["error"] = f"No headings found at level {min_level}-{max_level}."
        return result

    result.update({"ok": True, "output": "\n".join(lines_out), "heading_count": heading_count})
    return result
