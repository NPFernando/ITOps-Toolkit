"""Reformat a pasted SQL query with consistent indentation and keyword casing.

sqlparse is a lenient tokenizer/formatter, not a SQL validator or parser
for a specific dialect -- it never rejects input as "invalid SQL" (even
non-SQL text passes through unchanged). This tool inherits that
behavior deliberately: it reformats whatever you give it rather than
pretending to validate correctness.
"""

from __future__ import annotations

from typing import Any

import sqlparse

MAX_INPUT_LENGTH = 50_000
KEYWORD_CASES: tuple[str, ...] = ("upper", "lower", "capitalize")


def format_sql(sql: str, keyword_case: str = "upper", indent_width: int = 2) -> dict[str, Any]:
    """Reformat ``sql`` with consistent indentation and keyword casing."""
    result: dict[str, Any] = {"ok": False, "formatted": "", "error": None}

    cleaned = sql or ""
    if not cleaned.strip():
        result["error"] = "Enter a SQL query to format."
        return result
    if len(cleaned) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH} characters."
        return result
    if keyword_case not in KEYWORD_CASES:
        result["error"] = f"Unknown keyword case. Choose one of: {', '.join(KEYWORD_CASES)}."
        return result
    if not 1 <= indent_width <= 8:
        result["error"] = "Indent width must be between 1 and 8."
        return result

    formatted = sqlparse.format(
        cleaned,
        reindent=True,
        keyword_case=keyword_case,
        indent_width=indent_width,
        strip_comments=False,
    )
    result.update({"ok": True, "formatted": formatted})
    return result
