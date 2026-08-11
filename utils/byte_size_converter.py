"""Convert a byte count to/from human-readable units (KB/MB/GB/TB, decimal or binary).

Distinct from Integer Base Converter, which converts numeric bases, not
units.
"""

from __future__ import annotations

from typing import Any

MAX_INPUT_LENGTH = 32

_BINARY_UNITS = ("B", "KiB", "MiB", "GiB", "TiB", "PiB")
_DECIMAL_UNITS = ("B", "KB", "MB", "GB", "TB", "PB")
UNITS: dict[bool, tuple[str, ...]] = {True: _BINARY_UNITS, False: _DECIMAL_UNITS}


def bytes_to_human(count_str: str, binary: bool = True) -> dict[str, Any]:
    """Convert a byte count into the largest human-readable unit that keeps the value >= 1."""
    result: dict[str, Any] = {"ok": False, "error": None, "result": None}

    value = (count_str or "").strip()
    if not value:
        result["error"] = "Enter a byte count."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    try:
        count = float(value)
    except ValueError:
        result["error"] = "Enter a valid number."
        return result
    if count < 0:
        result["error"] = "Enter a non-negative byte count."
        return result

    base = 1024 if binary else 1000
    units = _BINARY_UNITS if binary else _DECIMAL_UNITS
    size = count
    for unit in units:
        if size < base or unit == units[-1]:
            display = f"{int(size)} {unit}" if unit == "B" else f"{size:.2f} {unit}"
            result.update({"ok": True, "result": display})
            return result
        size /= base

    return result


def human_to_bytes(value_str: str, unit: str, binary: bool = True) -> dict[str, Any]:
    """Convert a number + unit (e.g. "5", "GiB") into a raw byte count."""
    result: dict[str, Any] = {"ok": False, "error": None, "result": None}

    value = (value_str or "").strip()
    if not value:
        result["error"] = "Enter a value."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    try:
        number = float(value)
    except ValueError:
        result["error"] = "Enter a valid number."
        return result
    if number < 0:
        result["error"] = "Enter a non-negative value."
        return result

    units = _BINARY_UNITS if binary else _DECIMAL_UNITS
    if unit not in units:
        result["error"] = f"Unknown unit: {unit}."
        return result

    base = 1024 if binary else 1000
    power = units.index(unit)
    byte_count = number * (base**power)

    result.update({"ok": True, "result": int(byte_count) if byte_count.is_integer() else byte_count})
    return result
