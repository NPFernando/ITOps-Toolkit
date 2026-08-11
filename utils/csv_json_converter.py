"""Convert between CSV/TSV and JSON.

Distinct from Config Format Converter (JSON/YAML/TOML/XML, no CSV) and CSV
to Markdown Table (CSV -> Markdown only, one-way).
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any

MAX_INPUT_LENGTH = 100_000


def csv_to_json(csv_text: str, delimiter: str = ",") -> dict[str, Any]:
    """Parse CSV/TSV text (first row = header) into a JSON array of objects."""
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
    if len(set(header)) != len(header):
        result["error"] = "Header row has duplicate column names."
        return result

    records = []
    for row in body:
        # Pad/truncate to the header's column count so a ragged row doesn't
        # silently shift values into the wrong keys.
        padded = (row + [""] * len(header))[: len(header)]
        records.append(dict(zip(header, padded, strict=True)))

    result.update({"ok": True, "output": json.dumps(records, indent=2, ensure_ascii=False)})
    return result


def json_to_csv(json_text: str, delimiter: str = ",") -> dict[str, Any]:
    """Parse a JSON array of flat objects into CSV/TSV text.

    Columns are the union of every object's keys, in first-seen order, so a
    field missing from some records still gets its own column (blank cells
    for the records that lack it) instead of being silently dropped.
    """
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    value = (json_text or "").strip()
    if not value:
        result["error"] = "Paste JSON to convert."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    try:
        data = json.loads(value)
    except json.JSONDecodeError as exc:
        result["error"] = f"Invalid JSON: {exc}"
        return result

    if not isinstance(data, list) or not data:
        result["error"] = "JSON must be a non-empty array of objects."
        return result
    if not all(isinstance(item, dict) for item in data):
        result["error"] = "Every array element must be an object."
        return result

    columns: list[str] = []
    for item in data:
        for key in item:
            if key not in columns:
                columns.append(key)

    def _cell(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=delimiter, lineterminator="\n")
    writer.writerow(columns)
    for item in data:
        writer.writerow([_cell(item.get(col)) for col in columns])

    result.update({"ok": True, "output": buffer.getvalue()})
    return result
