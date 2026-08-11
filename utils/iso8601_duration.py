"""Parse an ISO 8601 duration (e.g. P3Y6M4DT12H30M5S) into human-readable units, or build one.

Distinct from Timestamp Converter/Log Timestamp Duration Calculator, which
work with actual timestamps, not the ISO 8601 duration format used in many
APIs and config files (e.g. AWS, Kubernetes, iCalendar).
"""

from __future__ import annotations

import re
from typing import Any

MAX_INPUT_LENGTH = 64

_DURATION_RE = re.compile(
    r"^P(?!$)(?:(?P<years>\d+(?:\.\d+)?)Y)?(?:(?P<months>\d+(?:\.\d+)?)M)?(?:(?P<weeks>\d+(?:\.\d+)?)W)?(?:(?P<days>\d+(?:\.\d+)?)D)?"
    r"(?:T(?!$)(?:(?P<hours>\d+(?:\.\d+)?)H)?(?:(?P<minutes>\d+(?:\.\d+)?)M)?(?:(?P<seconds>\d+(?:\.\d+)?)S)?)?$"
)

_UNIT_LABELS = (
    ("years", "year"),
    ("months", "month"),
    ("weeks", "week"),
    ("days", "day"),
    ("hours", "hour"),
    ("minutes", "minute"),
    ("seconds", "second"),
)


def _format_number(value: float) -> str:
    return str(int(value)) if value == int(value) else str(value)


def parse_duration(text: str) -> dict[str, Any]:
    """Parse an ISO 8601 duration string into a human-readable description."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None, "units": None}

    value = (text or "").strip()
    if not value:
        result["error"] = "Enter an ISO 8601 duration, e.g. P3Y6M4DT12H30M5S."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    match = _DURATION_RE.match(value.upper())
    if not match:
        result["error"] = f"'{value}' is not a valid ISO 8601 duration."
        return result

    parts = []
    units: dict[str, float] = {}
    for key, label in _UNIT_LABELS:
        raw = match.group(key)
        if raw is None:
            continue
        number = float(raw)
        units[key] = number
        plural = "" if number == 1 else "s"
        parts.append(f"{_format_number(number)} {label}{plural}")

    if not parts:
        result["error"] = f"'{value}' has no duration components."
        return result

    result.update({"ok": True, "output": ", ".join(parts), "units": units})
    return result


def build_duration(years: float = 0, months: float = 0, weeks: float = 0, days: float = 0, hours: float = 0, minutes: float = 0, seconds: float = 0) -> dict[str, Any]:
    """Build an ISO 8601 duration string from individual unit values."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    values = {"Y": years, "M": months, "W": weeks, "D": days}
    time_values = {"H": hours, "M": minutes, "S": seconds}

    if any(v < 0 for v in (*values.values(), *time_values.values())):
        result["error"] = "Duration components must be non-negative."
        return result
    if all(v <= 0 for v in (*values.values(), *time_values.values())):
        result["error"] = "Enter at least one non-zero duration component."
        return result

    date_part = "".join(f"{_format_number(v)}{unit}" for unit, v in values.items() if v > 0)
    time_part = "".join(f"{_format_number(v)}{unit}" for unit, v in time_values.items() if v > 0)

    output = "P" + date_part + (f"T{time_part}" if time_part else "")
    result.update({"ok": True, "output": output})
    return result
