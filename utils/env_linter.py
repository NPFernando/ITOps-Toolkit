"""Lint .env file content for common mistakes.

Checks for issues that are easy to introduce by hand and easy to miss on
review: duplicate keys (the last one silently wins in most loaders),
whitespace around the '=' or trailing on the line, unquoted values that
contain spaces, unterminated quotes, keys that aren't valid identifiers, and
lines with no '=' at all. This is a linter, not a validator -- it always
returns a (possibly empty) list of issues rather than failing outright.
"""

from __future__ import annotations

import re
from typing import Any

MAX_INPUT_LENGTH = 20_000

_VALID_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def lint_env(text: str) -> dict[str, Any]:
    """Lint .env-formatted text and return a list of line-numbered issues."""
    result: dict[str, Any] = {"ok": False, "error": None, "issues": []}
    if not (text or "").strip():
        result["error"] = "Paste .env content to lint."
        return result

    result["ok"] = True
    seen: dict[str, int] = {}
    issues: list[dict[str, Any]] = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        working = stripped
        if working.startswith("export "):
            working = working[len("export ") :].lstrip()

        if "=" not in working:
            issues.append({"line": line_number, "message": "Missing '=' -- not a valid KEY=VALUE line."})
            continue

        key, _, value = working.partition("=")
        key_stripped = key.strip()

        if key != key_stripped:
            issues.append({"line": line_number, "message": f"Key '{key_stripped}' has whitespace before '='."})

        if not _VALID_KEY.match(key_stripped):
            issues.append(
                {
                    "line": line_number,
                    "message": f"Key '{key_stripped}' is not a valid identifier (letters, digits, underscore; can't start with a digit).",
                }
            )

        if key_stripped in seen:
            issues.append({"line": line_number, "message": f"Duplicate key '{key_stripped}' (first set on line {seen[key_stripped]})."})
        else:
            seen[key_stripped] = line_number

        if raw_line.rstrip("\n") != raw_line.rstrip("\n").rstrip(" \t"):
            issues.append({"line": line_number, "message": "Trailing whitespace."})

        if value and value[0] in "\"'":
            quote = value[0]
            if not (len(value) >= 2 and value[-1] == quote):
                issues.append({"line": line_number, "message": f"Unterminated {quote} quote."})
        elif " " in value.strip():
            issues.append({"line": line_number, "message": "Unquoted value contains spaces -- wrap it in quotes."})

    result["issues"] = issues
    return result
