"""Select and reorder specific columns from CSV/TSV by header name.

Distinct from CSV/TSV Cleaner (trims/dedupes rows and cells, doesn't
select/reorder columns) and CSV to Markdown Table (converts everything,
no column selection).
"""

from __future__ import annotations

import csv
import io
from typing import Any

MAX_INPUT_LENGTH = 200_000


def select_columns(csv_text: str, columns_text: str, delimiter: str = ",") -> dict[str, Any]:
    """Extract and reorder the named columns from CSV/TSV text."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    value = (csv_text or "").strip()
    if not value:
        result["error"] = "Paste CSV or TSV text."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    wanted = [c.strip() for c in (columns_text or "").split(",") if c.strip()]
    if not wanted:
        result["error"] = "Enter at least one column name, comma-separated."
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
    if len(set(header)) != len(header):
        result["error"] = "Header row has duplicate column names."
        return result

    missing = [col for col in wanted if col not in header]
    if missing:
        result["error"] = f"Column(s) not found in header: {', '.join(missing)}."
        return result

    indices = [header.index(col) for col in wanted]
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=delimiter, lineterminator="\n")
    writer.writerow(wanted)
    for row in body:
        padded = (row + [""] * len(header))[: len(header)]
        writer.writerow([padded[i] for i in indices])

    result.update({"ok": True, "output": buffer.getvalue()})
    return result
