"""Structurally compare two CSVs by a key column, complementing JSON Diff Viewer."""

from __future__ import annotations

import csv
import io
from typing import Any

from utils.text_tools import validate_length

MAX_INPUT_LENGTH = 100_000


def _parse_csv(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text)))


def diff_csv(text_a: str, text_b: str, key_column: str) -> dict[str, Any]:
    """Compare two CSVs row-by-row, matched on ``key_column``."""
    result: dict[str, Any] = {"ok": False, "error": None, "differences": [], "identical": False}

    ok_a, error_a = validate_length(text_a, MAX_INPUT_LENGTH, "First CSV")
    if not ok_a:
        result["error"] = error_a
        return result
    ok_b, error_b = validate_length(text_b, MAX_INPUT_LENGTH, "Second CSV")
    if not ok_b:
        result["error"] = error_b
        return result

    key_column = (key_column or "").strip()
    if not key_column:
        result["error"] = "Enter the key column name to match rows on."
        return result

    try:
        rows_a = _parse_csv(text_a)
        rows_b = _parse_csv(text_b)
    except csv.Error as exc:
        result["error"] = f"Could not parse CSV: {exc}"
        return result

    if not rows_a or not rows_b:
        result["error"] = "Both CSVs must have a header row and at least one data row."
        return result

    if key_column not in rows_a[0] or key_column not in rows_b[0]:
        result["error"] = f"Key column '{key_column}' was not found in both CSVs' headers."
        return result

    by_key_a = {row[key_column]: row for row in rows_a}
    by_key_b = {row[key_column]: row for row in rows_b}

    differences: list[dict[str, Any]] = []
    for key, row_a in by_key_a.items():
        if key not in by_key_b:
            differences.append({"key": key, "type": "removed"})
            continue
        row_b = by_key_b[key]
        changed_fields = {field: {"old": value, "new": row_b.get(field)} for field, value in row_a.items() if row_b.get(field) != value}
        if changed_fields:
            differences.append({"key": key, "type": "changed", "fields": changed_fields})
    for key in by_key_b:
        if key not in by_key_a:
            differences.append({"key": key, "type": "added"})

    result.update({"ok": True, "differences": differences, "identical": not differences})
    return result
