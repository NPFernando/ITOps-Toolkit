"""Clean up messy CSV/TSV: trim cell whitespace, drop empty rows, dedupe rows.

Distinct from Sort & Dedupe Lines (works on arbitrary text lines, not
structured rows/cells) and CSV Diff Viewer (compares two CSVs, doesn't
clean one).
"""

from __future__ import annotations

import csv
import io
from typing import Any

MAX_INPUT_LENGTH = 200_000


def clean_csv(
    csv_text: str,
    delimiter: str = ",",
    trim_cells: bool = True,
    drop_empty_rows: bool = True,
    dedupe_rows: bool = False,
) -> dict[str, Any]:
    """Clean pasted CSV/TSV text and report what changed."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None, "row_count": 0, "removed_count": 0}

    value = (csv_text or "").strip()
    if not value:
        result["error"] = "Paste CSV or TSV text to clean."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    try:
        rows = list(csv.reader(io.StringIO(value), delimiter=delimiter))
    except csv.Error as exc:
        result["error"] = f"Could not parse input: {exc}"
        return result

    if not rows:
        result["error"] = "No rows found."
        return result

    original_count = len(rows)

    if trim_cells:
        rows = [[cell.strip() for cell in row] for row in rows]

    if drop_empty_rows:
        rows = [row for row in rows if any(cell.strip() for cell in row)]

    if dedupe_rows:
        seen: set[tuple[str, ...]] = set()
        deduped = []
        for row in rows:
            key = tuple(row)
            if key not in seen:
                seen.add(key)
                deduped.append(row)
        rows = deduped

    if not rows:
        result["error"] = "Nothing left after cleaning -- every row was empty."
        return result

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=delimiter, lineterminator="\n")
    writer.writerows(rows)

    result.update(
        {
            "ok": True,
            "output": buffer.getvalue(),
            "row_count": len(rows),
            "removed_count": original_count - len(rows),
        }
    )
    return result
