"""Sort and/or deduplicate the lines of pasted text.

Distinct from Text Diff Checker (compares two texts) and CSV/TSV Cleaner
(structured rows/cells, not arbitrary lines).
"""

from __future__ import annotations

from typing import Any

MAX_INPUT_LENGTH = 200_000

SORT_MODES = ("None", "Alphabetical (A-Z)", "Alphabetical (Z-A)", "Numeric (ascending)", "Numeric (descending)")


def sort_and_dedupe_lines(
    text: str,
    sort_mode: str = "None",
    dedupe: bool = False,
    case_insensitive: bool = False,
    remove_blank: bool = False,
) -> dict[str, Any]:
    """Sort and/or deduplicate the lines of ``text``, returning the cleaned result."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None, "line_count": 0, "removed_count": 0}

    value = text or ""
    if not value.strip():
        result["error"] = "Paste some text to process."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result
    if sort_mode not in SORT_MODES:
        result["error"] = f"Unknown sort mode: {sort_mode}."
        return result

    lines = value.splitlines()
    original_count = len(lines)

    if remove_blank:
        lines = [line for line in lines if line.strip()]

    if dedupe:
        seen: set[str] = set()
        deduped = []
        for line in lines:
            key = line.lower() if case_insensitive else line
            if key not in seen:
                seen.add(key)
                deduped.append(line)
        lines = deduped

    if sort_mode == "Alphabetical (A-Z)":
        lines.sort(key=str.lower if case_insensitive else None)
    elif sort_mode == "Alphabetical (Z-A)":
        lines.sort(key=str.lower if case_insensitive else None, reverse=True)
    elif sort_mode in ("Numeric (ascending)", "Numeric (descending)"):
        try:
            numeric_lines = [(float(line.strip()), line) for line in lines]
        except ValueError:
            # Blank lines fail float() too, so a truthful message must not
            # say "non-blank" unless blank lines are actually being removed.
            if remove_blank:
                result["error"] = "Numeric sort requires every non-blank line to be a plain number."
            else:
                result["error"] = 'Numeric sort requires every line to be a plain number. Enable "Remove blank lines" if your input has any.'
            return result
        numeric_lines.sort(key=lambda pair: pair[0], reverse=sort_mode.endswith("descending)"))
        lines = [line for _, line in numeric_lines]

    result.update(
        {
            "ok": True,
            "output": "\n".join(lines),
            "line_count": len(lines),
            "removed_count": original_count - len(lines),
        }
    )
    return result
