"""Convert CSV/TSV to a Markdown table.

Uses csv.reader (not DictReader) so row order and duplicate column names in
the header are preserved exactly -- DictReader would silently collapse
duplicate header names to a single key, losing columns.
"""

from __future__ import annotations

import csv
import io
from typing import Any

MAX_INPUT_LENGTH = 100_000


def _escape_cell(value: str) -> str:
    # An unescaped '|' breaks the Markdown table's column alignment;
    # embedded newlines break the one-row-per-line format.
    return value.replace("|", "\\|").replace("\n", " ").replace("\r", "")


def convert_csv_to_markdown(csv_text: str, delimiter: str = ",") -> dict[str, Any]:
    """Parse CSV/TSV text and return an equivalent Markdown table."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    value = (csv_text or "").strip()
    if not value:
        result["error"] = "Paste CSV or TSV text to convert."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    try:
        rows = list(csv.reader(io.StringIO(value), delimiter=delimiter))
    except csv.Error as exc:
        result["error"] = f"Could not parse input: {exc}"
        return result

    rows = [row for row in rows if row]
    if not rows:
        result["error"] = "No rows found."
        return result

    header, *body = rows
    lines = ["| " + " | ".join(_escape_cell(cell) for cell in header) + " |", "| " + " | ".join(["---"] * len(header)) + " |"]
    for row in body:
        # Pad/truncate to the header's column count so a ragged row doesn't
        # break the table's column alignment.
        padded = (row + [""] * len(header))[: len(header)]
        lines.append("| " + " | ".join(_escape_cell(cell) for cell in padded) + " |")

    result.update({"ok": True, "output": "\n".join(lines)})
    return result
