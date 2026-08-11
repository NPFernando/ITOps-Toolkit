"""Re-align a Markdown pipe table's columns to consistent, padded widths.

Distinct from CSV to Markdown Table (builds a table from CSV) -- this
reformats a table that's already Markdown but has ragged/misaligned column
widths. Preserves each column's alignment marker (:---, ---:, :---:, ---)
from the existing separator row.
"""

from __future__ import annotations

from typing import Any

MAX_INPUT_LENGTH = 100_000
_MIN_DASH_WIDTH = 3


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _parse_alignment(separator_cell: str) -> str:
    cell = separator_cell.strip()
    left, right = cell.startswith(":"), cell.endswith(":")
    if left and right:
        return "center"
    if right:
        return "right"
    if left:
        return "left"
    return "none"


def _format_separator(width: int, align: str) -> str:
    if align == "center":
        return ":" + "-" * max(width - 2, 1) + ":"
    if align == "right":
        return "-" * max(width - 1, 1) + ":"
    if align == "left":
        return ":" + "-" * max(width - 1, 1)
    return "-" * width


def _pad(cell: str, width: int, align: str) -> str:
    if align == "right":
        return cell.rjust(width)
    if align == "center":
        return cell.center(width)
    return cell.ljust(width)


def format_markdown_table(markdown_text: str) -> dict[str, Any]:
    """Re-align a Markdown pipe table so every column has a consistent, padded width."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    value = (markdown_text or "").strip()
    if not value:
        result["error"] = "Paste a Markdown table."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    lines = [line for line in value.splitlines() if line.strip()]
    if len(lines) < 2:
        result["error"] = "A table needs a header row and a separator row (e.g. |---|---|)."
        return result
    if "|" not in lines[0]:
        result["error"] = "Header row must contain at least one '|'."
        return result

    header = _split_row(lines[0])
    separator = _split_row(lines[1])
    if len(separator) != len(header) or not all(set(cell.strip(":")) <= {"-"} and cell.strip(":") for cell in separator):
        result["error"] = "Second row must be a valid separator row (e.g. |---|:---:|---:|), matching the header's column count."
        return result

    body = [_split_row(line) for line in lines[2:] if "|" in line]
    ragged = [row for row in body if len(row) != len(header)]
    if ragged:
        result["error"] = f"Every row must have {len(header)} columns to match the header -- found a row with {len(ragged[0])}."
        return result

    aligns = [_parse_alignment(cell) for cell in separator]
    widths = [max(_MIN_DASH_WIDTH, len(header[i]), *(len(row[i]) for row in body)) if body else max(_MIN_DASH_WIDTH, len(header[i])) for i in range(len(header))]

    out_lines = [
        "| " + " | ".join(_pad(header[i], widths[i], aligns[i]) for i in range(len(header))) + " |",
        "| " + " | ".join(_format_separator(widths[i], aligns[i]) for i in range(len(header))) + " |",
    ]
    for row in body:
        out_lines.append("| " + " | ".join(_pad(row[i], widths[i], aligns[i]) for i in range(len(header))) + " |")

    result.update({"ok": True, "output": "\n".join(out_lines)})
    return result
