"""Plain calendar-date arithmetic: add/subtract days/weeks/months, or count days between two dates.

Distinct from Timestamp Converter (single-value epoch/ISO conversion),
Business Hours Calculator (business-hours-only elapsed time), and Log
Timestamp Duration Calculator (log-format auto-detection) -- this is
everyday calendar-date math with no time-of-day component.
"""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from typing import Any

MAX_INPUT_LENGTH = 32
UNITS: tuple[str, ...] = ("days", "weeks", "months")


def _add_months(base: date, months: int) -> date:
    month_index = base.month - 1 + months
    year = base.year + month_index // 12
    month = month_index % 12 + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat((value or "").strip())
    except ValueError:
        return None


def add_to_date(date_str: str, amount: int, unit: str) -> dict[str, Any]:
    """Add (or subtract, if ``amount`` is negative) a number of days/weeks/months to a date."""
    result: dict[str, Any] = {"ok": False, "error": None, "result_date": None, "weekday": None}

    if unit not in UNITS:
        result["error"] = f"Unknown unit: {unit}."
        return result

    base = _parse_date(date_str)
    if base is None:
        result["error"] = "Enter a valid date (YYYY-MM-DD)."
        return result

    try:
        if unit == "days":
            new_date = base + timedelta(days=amount)
        elif unit == "weeks":
            new_date = base + timedelta(weeks=amount)
        else:
            new_date = _add_months(base, amount)
    except (OverflowError, ValueError):
        # timedelta arithmetic raises OverflowError for an out-of-range
        # result; _add_months's date(year, ...) construction raises
        # ValueError instead once the computed year exceeds datetime.MAXYEAR.
        result["error"] = "That amount pushes the result outside the range of representable dates."
        return result

    result.update({"ok": True, "result_date": new_date.isoformat(), "weekday": new_date.strftime("%A")})
    return result


def days_between(start_str: str, end_str: str) -> dict[str, Any]:
    """Compute the number of calendar days between two dates (order-independent)."""
    result: dict[str, Any] = {"ok": False, "error": None, "days": None}

    start = _parse_date(start_str)
    end = _parse_date(end_str)
    if start is None or end is None:
        result["error"] = "Enter two valid dates (YYYY-MM-DD)."
        return result

    result.update({"ok": True, "days": abs((end - start).days)})
    return result
