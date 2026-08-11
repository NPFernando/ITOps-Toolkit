"""Align whitespace-separated columns of plain text -- like the Unix `column -t` command.

Distinct from Markdown Table Formatter (pipe-delimited Markdown tables)
and CSV Column Selector (comma-delimited, selects/reorders rather than
aligns). Meant for things like `ps aux`, `df -h`, or `kubectl get pods`
output pasted with ragged spacing.
"""

from __future__ import annotations

import re
from typing import Any

MAX_INPUT_LENGTH = 200_000
_WHITESPACE_RUN_RE = re.compile(r"\s+")


def align_columns(text: str, delimiter: str = "") -> dict[str, Any]:
    """Split each line into columns and pad every column to its widest cell."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    value = text or ""
    if not value.strip():
        result["error"] = "Paste some columnar text."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    lines = value.splitlines()
    if delimiter:
        rows = [line.split(delimiter) for line in lines]
    else:
        rows = [_WHITESPACE_RUN_RE.split(line.strip()) for line in lines]

    max_columns = max((len(row) for row in rows), default=0)
    if max_columns == 0:
        result["error"] = "No columns found."
        return result

    widths = [0] * max_columns
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    out_lines = []
    for row in rows:
        # Don't pad the last real cell in a row -- avoids trailing spaces
        # on every line, which is both pointless and a common source of
        # "why does git diff show every line as changed" surprises.
        padded = [cell.ljust(widths[i]) for i, cell in enumerate(row[:-1])]
        if row:
            padded.append(row[-1])
        out_lines.append("  ".join(padded))

    result.update({"ok": True, "output": "\n".join(out_lines)})
    return result
