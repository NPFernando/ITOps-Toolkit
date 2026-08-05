"""Text case conversion helpers (slug-case, camelCase, snake_case, kebab-case, Title Case)."""

from __future__ import annotations

import re
from typing import Any

MAX_INPUT_LENGTH = 5_000

_WORD_BOUNDARY = re.compile(r"[_\-\s]+")
_LOWER_TO_UPPER = re.compile(r"([a-z0-9])([A-Z])")
_ACRONYM_TO_WORD = re.compile(r"([A-Z]+)([A-Z][a-z])")
_NON_ALNUM = re.compile(r"[^a-zA-Z0-9]+")


def _split_words(value: str) -> list[str]:
    text = _WORD_BOUNDARY.sub(" ", value)
    text = _LOWER_TO_UPPER.sub(r"\1 \2", text)
    text = _ACRONYM_TO_WORD.sub(r"\1 \2", text)
    return [word for word in text.split(" ") if word]


def convert_case(value: str) -> dict[str, Any]:
    """Convert ``value`` into slug-case, snake_case, kebab-case, camelCase, PascalCase, and Title Case."""
    result: dict[str, Any] = {"ok": False, "error": None}
    text = (value or "").strip()
    if not text:
        result["error"] = "Enter some text."
        return result
    if len(text) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    words = [_NON_ALNUM.sub("", word) for word in _split_words(text)]
    words = [word for word in words if word]
    if not words:
        result["error"] = "No alphanumeric characters found to convert."
        return result

    lower_words = [word.lower() for word in words]
    camel = lower_words[0] + "".join(word.capitalize() for word in lower_words[1:])
    pascal = "".join(word.capitalize() for word in lower_words)

    result.update(
        {
            "ok": True,
            "slug_case": "-".join(lower_words),
            "kebab_case": "-".join(lower_words),
            "snake_case": "_".join(lower_words),
            "camel_case": camel,
            "pascal_case": pascal,
            "title_case": " ".join(word.capitalize() for word in lower_words),
            "upper_snake_case": "_".join(word.upper() for word in lower_words),
        }
    )
    return result
