"""Show one point in time across a fixed set of major world timezones.

Distinct from Timestamp Converter's convert_timezone (a single from/to
conversion) -- this shows every zone in the list side by side at once, for
planning a meeting or a maintenance window across offices.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

MAX_INPUT_LENGTH = 32

# Curated set of widely-used IANA zones spanning every UTC offset region --
# not exhaustive, but enough to plan a meeting across most global teams.
WORLD_ZONES = (
    "UTC",
    "America/Los_Angeles",
    "America/Denver",
    "America/Chicago",
    "America/New_York",
    "America/Sao_Paulo",
    "Europe/London",
    "Europe/Berlin",
    "Europe/Moscow",
    "Africa/Johannesburg",
    "Asia/Dubai",
    "Asia/Kolkata",
    "Asia/Bangkok",
    "Asia/Singapore",
    "Asia/Tokyo",
    "Australia/Sydney",
)

_DISPLAY_FORMAT = "%Y-%m-%d %H:%M %Z"


def _resolve_timezone(tz_name: str) -> ZoneInfo | None:
    try:
        return ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, ValueError):
        return None


def world_clock(value: str, source_tz_name: str) -> dict[str, Any]:
    """Convert one local time into every zone in WORLD_ZONES."""
    result: dict[str, Any] = {"ok": False, "error": None, "zones": None}

    text = (value or "").strip()
    if not text:
        result["error"] = "Enter a date and time."
        return result
    if len(text) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    source_tz = _resolve_timezone(source_tz_name)
    if source_tz is None:
        result["error"] = f"Unknown timezone: {source_tz_name}."
        return result

    try:
        naive = datetime.fromisoformat(text)
    except ValueError:
        result["error"] = "Enter a date/time like 2026-03-05T14:30 or 2026-03-05 14:30."
        return result
    if naive.tzinfo is not None:
        result["error"] = "Enter a timezone-naive date/time; pick the source timezone separately."
        return result

    anchored = naive.replace(tzinfo=source_tz)

    zones = []
    for zone_name in WORLD_ZONES:
        tz = _resolve_timezone(zone_name)
        if tz is None:
            continue
        local = anchored.astimezone(tz)
        zones.append(
            {
                "zone": zone_name,
                "local_time": local.strftime(_DISPLAY_FORMAT),
                "day_offset": (local.date() - anchored.date()).days,
            }
        )

    result.update({"ok": True, "zones": zones})
    return result
