"""Compute elapsed duration between two log timestamps, auto-detecting format.

Distinct from Timestamp Converter (single epoch/ISO conversion) and Business
Hours Calculator (business-hours-only elapsed time) -- this parses raw log
line timestamps directly, trying ISO 8601, Apache/nginx access log, and
syslog formats in that order.

Syslog timestamps have no year field, so the current year is substituted
(an explicit, stated assumption -- surfaced to the caller, not hidden). If
the computed end-minus-start comes out negative after that substitution, the
end timestamp is rolled forward one year to handle a Dec->Jan boundary
crossing. Naive (timezone-less) timestamps -- always the syslog case here --
are treated as UTC when compared against a timezone-aware one; also an
explicit, stated assumption.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

MAX_INPUT_LENGTH = 64

_FORMAT_ISO8601 = "ISO 8601"
_FORMAT_APACHE = "Apache/nginx access log"
_FORMAT_SYSLOG = "syslog (year assumed)"


def parse_log_timestamp(value: str) -> tuple[str | None, datetime | None]:
    """Try ISO 8601, then Apache/nginx access log, then syslog. Return (format_name, datetime) or (None, None)."""
    value = (value or "").strip()
    if not value:
        return None, None

    try:
        return _FORMAT_ISO8601, datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        pass

    try:
        return _FORMAT_APACHE, datetime.strptime(value, "%d/%b/%Y:%H:%M:%S %z")
    except ValueError:
        pass

    try:
        parsed = datetime.strptime(value, "%b %d %H:%M:%S")
        return _FORMAT_SYSLOG, parsed.replace(year=datetime.now().year)
    except ValueError:
        pass

    return None, None


def calculate_log_duration(start_str: str, end_str: str) -> dict[str, Any]:
    """Parse two log timestamps (any supported format, mixed formats allowed) and compute elapsed duration."""
    result: dict[str, Any] = {"ok": False, "error": None, "start_format": None, "end_format": None, "duration_display": None, "duration_seconds": None}

    if len(start_str or "") > MAX_INPUT_LENGTH or len(end_str or "") > MAX_INPUT_LENGTH:
        result["error"] = f"Timestamps must be {MAX_INPUT_LENGTH} characters or fewer."
        return result

    start_format, start_dt = parse_log_timestamp(start_str)
    if start_dt is None:
        result["error"] = "Could not detect the format of the start timestamp (tried ISO 8601, Apache/nginx access log, syslog)."
        return result

    end_format, end_dt = parse_log_timestamp(end_str)
    if end_dt is None:
        result["error"] = "Could not detect the format of the end timestamp (tried ISO 8601, Apache/nginx access log, syslog)."
        return result

    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=timezone.utc)

    if end_dt < start_dt:
        end_dt = end_dt.replace(year=end_dt.year + 1)

    delta = end_dt - start_dt
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    result.update(
        {
            "ok": True,
            "start_format": start_format,
            "end_format": end_format,
            "duration_display": f"{hours}h {minutes}m {seconds}s",
            "duration_seconds": total_seconds,
        }
    )
    return result
