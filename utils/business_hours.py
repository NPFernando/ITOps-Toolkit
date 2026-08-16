"""Compute elapsed business hours between two timestamps.

Excludes weekends and a configurable set of holiday dates, restricted to a
configurable daily business-hours window (default 9:00-17:00). Distinct from
Timestamp Converter (single-timestamp conversion) and Uptime Trend (uptime
percentage over a window) -- this is duration math for SLA/ticket-response
calculations.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from utils.timestamp_tools import COMMON_TIMEZONES

MAX_INPUT_LENGTH = 64
DEFAULT_BUSINESS_START = time(9, 0)
DEFAULT_BUSINESS_END = time(17, 0)
_WEEKEND_DAYS = (5, 6)  # Saturday, Sunday


def _resolve_timezone(tz_name: str) -> ZoneInfo | None:
    try:
        return ZoneInfo(tz_name or "UTC")
    except ZoneInfoNotFoundError:
        return None


def _parse_timestamp(value: str, tz: ZoneInfo) -> datetime | None:
    try:
        dt = datetime.fromisoformat(value.strip())
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    return dt


def _parse_holidays(holidays_str: str) -> tuple[set[date], list[str]]:
    holidays: set[date] = set()
    invalid: list[str] = []
    for token in (holidays_str or "").split(","):
        token = token.strip()
        if not token:
            continue
        try:
            holidays.add(date.fromisoformat(token))
        except ValueError:
            invalid.append(token)
    return holidays, invalid


def _format_duration(total: timedelta) -> str:
    total_minutes = int(total.total_seconds() // 60)
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}h {minutes}m"


def calculate_business_hours(
    start_str: str,
    end_str: str,
    tz_name: str = "UTC",
    business_start: time = DEFAULT_BUSINESS_START,
    business_end: time = DEFAULT_BUSINESS_END,
    holidays_str: str = "",
) -> dict[str, Any]:
    """Compute elapsed business hours between two ISO 8601 timestamps."""
    result: dict[str, Any] = {"ok": False, "error": None, "business_hours": None, "business_hours_display": None, "business_days_spanned": None}

    tz = _resolve_timezone(tz_name)
    if tz is None:
        result["error"] = f"Unknown timezone: {tz_name}."
        return result

    start_str = (start_str or "").strip()
    end_str = (end_str or "").strip()
    if not start_str or not end_str:
        result["error"] = "Enter both a start and end timestamp."
        return result
    if len(start_str) > MAX_INPUT_LENGTH or len(end_str) > MAX_INPUT_LENGTH:
        result["error"] = f"Timestamps must be {MAX_INPUT_LENGTH} characters or fewer."
        return result

    start = _parse_timestamp(start_str, tz)
    end = _parse_timestamp(end_str, tz)
    if start is None or end is None:
        result["error"] = "Enter valid ISO 8601 timestamps (e.g. 2026-08-07T16:00:00)."
        return result

    if business_start >= business_end:
        result["error"] = "Business hours start must be before business hours end."
        return result

    holidays, invalid_holidays = _parse_holidays(holidays_str)
    if invalid_holidays:
        result["error"] = f"Invalid holiday date(s): {', '.join(invalid_holidays)}. Use YYYY-MM-DD, comma-separated."
        return result

    if end < start:
        start, end = end, start

    total = timedelta()
    business_days_spanned = 0
    day = start.date()
    while day <= end.date():
        if day.weekday() not in _WEEKEND_DAYS and day not in holidays:
            window_start = datetime.combine(day, business_start, tzinfo=start.tzinfo)
            window_end = datetime.combine(day, business_end, tzinfo=start.tzinfo)
            overlap_start = max(window_start, start)
            overlap_end = min(window_end, end)
            if overlap_end > overlap_start:
                total += overlap_end - overlap_start
                business_days_spanned += 1
        day += timedelta(days=1)

    result.update(
        {
            "ok": True,
            "business_hours": round(total.total_seconds() / 3600, 2),
            "business_hours_display": _format_duration(total),
            "business_days_spanned": business_days_spanned,
        }
    )
    return result


__all__ = ["COMMON_TIMEZONES", "MAX_INPUT_LENGTH", "DEFAULT_BUSINESS_START", "DEFAULT_BUSINESS_END", "calculate_business_hours"]
