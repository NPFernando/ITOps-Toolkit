"""Timestamp / epoch conversion helpers."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

MAX_INPUT_LENGTH = 64

COMMON_TIMEZONES = (
    "UTC",
    "America/New_York",
    "America/Chicago",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Berlin",
    "Asia/Kolkata",
    "Asia/Tokyo",
    "Asia/Singapore",
    "Australia/Sydney",
)

EPOCH_UNITS = ("seconds", "milliseconds")

_DISPLAY_FORMAT = "%Y-%m-%d %H:%M:%S %Z"


def _resolve_timezone(tz_name: str) -> ZoneInfo | None:
    try:
        return ZoneInfo(tz_name or "UTC")
    except ZoneInfoNotFoundError:
        return None


def _describe(dt: datetime) -> dict[str, Any]:
    return {
        "iso": dt.isoformat(),
        "display": dt.strftime(_DISPLAY_FORMAT),
        "epoch_seconds": int(dt.timestamp()),
        "epoch_milliseconds": int(dt.timestamp() * 1000),
    }


def now_timestamp(tz_name: str = "UTC") -> dict[str, Any]:
    """Return the current time in the given timezone plus its epoch value."""
    tz = _resolve_timezone(tz_name)
    if tz is None:
        return {"ok": False, "error": f"Unknown timezone: {tz_name}."}
    return {"ok": True, "error": None, **_describe(datetime.now(tz))}


def epoch_to_datetime(value: str, unit: str, tz_name: str) -> dict[str, Any]:
    """Convert a Unix epoch value to a human-readable datetime in ``tz_name``."""
    result: dict[str, Any] = {"ok": False, "error": None}
    value = (value or "").strip()
    if not value:
        result["error"] = "Enter an epoch value."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH} characters."
        return result
    if unit not in EPOCH_UNITS:
        result["error"] = f"Unsupported unit: {unit}."
        return result

    try:
        numeric = float(value)
    except ValueError:
        result["error"] = "Epoch value must be a number."
        return result

    tz = _resolve_timezone(tz_name)
    if tz is None:
        result["error"] = f"Unknown timezone: {tz_name}."
        return result

    seconds = numeric / 1000 if unit == "milliseconds" else numeric
    try:
        dt = datetime.fromtimestamp(seconds, tz=tz)
    except (OverflowError, OSError, ValueError) as exc:
        result["error"] = f"Epoch value out of range: {exc}"
        return result

    result.update({"ok": True, **_describe(dt)})
    return result


def datetime_to_epoch(value: str, tz_name: str) -> dict[str, Any]:
    """Parse an ISO 8601-ish datetime string in ``tz_name`` and return its epoch value."""
    result: dict[str, Any] = {"ok": False, "error": None}
    value = (value or "").strip()
    if not value:
        result["error"] = "Enter a date/time value."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH} characters."
        return result

    tz = _resolve_timezone(tz_name)
    if tz is None:
        result["error"] = f"Unknown timezone: {tz_name}."
        return result

    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        result["error"] = "Could not parse that date/time. Try an ISO 8601 format, e.g. 2026-08-05T14:30:00."
        return result

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    result.update({"ok": True, **_describe(dt)})
    return result


def convert_timezone(value: str, from_tz_name: str, to_tz_name: str) -> dict[str, Any]:
    """Reinterpret an ISO 8601-ish datetime from one timezone into another."""
    result: dict[str, Any] = {"ok": False, "error": None}
    parsed = datetime_to_epoch(value, from_tz_name)
    if not parsed["ok"]:
        return {"ok": False, "error": parsed["error"]}

    to_tz = _resolve_timezone(to_tz_name)
    if to_tz is None:
        result["error"] = f"Unknown timezone: {to_tz_name}."
        return result

    source_dt = datetime.fromisoformat(parsed["iso"])
    converted = source_dt.astimezone(to_tz)
    result.update({"ok": True, **_describe(converted)})
    return result


def relative_description(epoch_seconds: int, reference: datetime | None = None) -> str:
    """Return a short human-readable "N minutes ago" / "in N hours" style description."""
    reference = reference or datetime.now(tz=_resolve_timezone("UTC"))
    target = datetime.fromtimestamp(epoch_seconds, tz=_resolve_timezone("UTC"))
    delta: timedelta = target - reference
    seconds = int(delta.total_seconds())
    future = seconds >= 0
    seconds = abs(seconds)

    if seconds < 60:
        phrase = f"{seconds}s"
    elif seconds < 3600:
        phrase = f"{seconds // 60}m"
    elif seconds < 86400:
        phrase = f"{seconds // 3600}h"
    else:
        phrase = f"{seconds // 86400}d"

    return f"in {phrase}" if future else f"{phrase} ago"
