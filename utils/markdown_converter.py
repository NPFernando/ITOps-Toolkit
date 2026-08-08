"""Convert between Markdown and HTML."""

from __future__ import annotations

from typing import Any

import markdown as markdown_lib
from markdownify import markdownify

from utils.text_tools import validate_length

MAX_INPUT_LENGTH = 100_000
DIRECTIONS: tuple[str, ...] = ("Markdown to HTML", "HTML to Markdown")

_MARKDOWN_EXTENSIONS = ("extra", "sane_lists")


def convert_markdown(text: str, direction: str) -> dict[str, Any]:
    """Convert ``text`` between Markdown and HTML per ``direction``."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    ok, error = validate_length(text, MAX_INPUT_LENGTH, "Input")
    if not ok:
        result["error"] = error
        return result
    if not (text or "").strip():
        result["error"] = "Enter some text to convert."
        return result
    if direction not in DIRECTIONS:
        result["error"] = f"Unknown direction: {direction}."
        return result

    if direction == "Markdown to HTML":
        result["output"] = markdown_lib.markdown(text, extensions=list(_MARKDOWN_EXTENSIONS))
    else:
        result["output"] = markdownify(text).strip()

    result["ok"] = True
    return result
