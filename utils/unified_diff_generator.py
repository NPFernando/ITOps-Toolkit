"""Generate a real unified diff (patch) from two texts, applicable with `patch`/`git apply`.

Distinct from Text Diff Checker, which produces its own added/removed
line summary for on-screen review, not a standard .patch-format file.
Uses stdlib difflib.unified_diff directly.
"""

from __future__ import annotations

import difflib
from typing import Any

MAX_INPUT_LENGTH = 200_000


def generate_unified_diff(original: str, changed: str, original_name: str = "a", changed_name: str = "b", context_lines: int = 3) -> dict[str, Any]:
    """Generate a unified diff between two texts."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None, "identical": False}

    if len(original or "") > MAX_INPUT_LENGTH or len(changed or "") > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result
    if not (original or "").strip() and not (changed or "").strip():
        result["error"] = "Paste at least one non-empty text to compare."
        return result
    if context_lines < 0:
        result["error"] = "Context lines must be non-negative."
        return result

    original_lines = (original or "").splitlines(keepends=True)
    changed_lines = (changed or "").splitlines(keepends=True)

    if original_lines == changed_lines:
        result.update({"ok": True, "output": "", "identical": True})
        return result

    diff_lines = list(
        difflib.unified_diff(
            original_lines,
            changed_lines,
            fromfile=original_name or "a",
            tofile=changed_name or "b",
            n=context_lines,
        )
    )
    # Lines from splitlines(keepends=True) already carry their own newline
    # except possibly the last one -- ensure every diff line ends cleanly
    # so the joined output doesn't run two lines together.
    output = "".join(line if line.endswith("\n") else line + "\n" for line in diff_lines)

    result.update({"ok": True, "output": output, "identical": False})
    return result
