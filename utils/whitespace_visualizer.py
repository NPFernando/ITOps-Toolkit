"""Flag invisible/lookalike characters that commonly cause silent copy-paste bugs.

Non-breaking spaces, zero-width characters, BOMs, and other invisible or
lookalike characters pasted in from a rich-text source (e.g. a web page, a
Word doc, a Slack message) into a config file or script are a common,
hard-to-self-diagnose class of bug -- the value "looks" right but doesn't
match byte-for-byte.
"""

from __future__ import annotations

import unicodedata
from typing import Any

MAX_INPUT_LENGTH = 50_000

# Plain space, tab, and newline are the only whitespace characters that are
# never flagged -- everything else that's whitespace-or-invisible is a
# potential silent bug.
_ALLOWED_WHITESPACE = {" ", "\t", "\n", "\r"}


def _is_flaggable(char: str) -> bool:
    if char in _ALLOWED_WHITESPACE:
        return False
    category = unicodedata.category(char)
    # Zs/Zl/Zp: space/line/paragraph separators other than the plain ones
    # above (e.g. non-breaking space). Cf: format characters, invisible by
    # definition (e.g. zero-width space, BOM). Cc: other control characters.
    return category in {"Zs", "Zl", "Zp", "Cf", "Cc"}


def visualize_whitespace(text: str) -> dict[str, Any]:
    """Flag invisible/lookalike characters in ``text`` with their line/column position."""
    result: dict[str, Any] = {"ok": False, "error": None, "findings": [], "annotated_text": None}

    if not (text or ""):
        result["error"] = "Paste text to check."
        return result
    if len(text) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    findings: list[dict[str, Any]] = []
    annotated_lines: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        annotated_chars: list[str] = []
        for column, char in enumerate(line, start=1):
            if _is_flaggable(char):
                name = unicodedata.name(char, "UNKNOWN")
                findings.append({"line": line_number, "column": column, "codepoint": f"U+{ord(char):04X}", "name": name})
                annotated_chars.append(f"[{name}]")
            else:
                annotated_chars.append(char)
        annotated_lines.append("".join(annotated_chars))

    result.update({"ok": True, "findings": findings, "annotated_text": "\n".join(annotated_lines)})
    return result
