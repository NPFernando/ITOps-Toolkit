"""Add line numbers to pasted text, for referencing a specific line in review or a bug report."""

from __future__ import annotations

from typing import Any

MAX_INPUT_LENGTH = 200_000


def add_line_numbers(text: str, start_at: int = 1, separator: str = ": ") -> dict[str, Any]:
    """Prefix every line of ``text`` with a right-aligned line number."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    value = text or ""
    if not value:
        result["error"] = "Paste some text."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    lines = value.splitlines()
    last_number = start_at + len(lines) - 1
    width = len(str(last_number))

    numbered = [f"{str(start_at + i).rjust(width)}{separator}{line}" for i, line in enumerate(lines)]
    result.update({"ok": True, "output": "\n".join(numbered)})
    return result
