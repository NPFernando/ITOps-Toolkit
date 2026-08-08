from __future__ import annotations

from datetime import datetime

from utils.log_duration import calculate_log_duration, parse_log_timestamp


def test_parse_log_timestamp_iso8601():
    fmt, dt = parse_log_timestamp("2026-08-07T16:00:00Z")

    assert fmt == "ISO 8601"
    assert dt.year == 2026
    assert dt.hour == 16


def test_parse_log_timestamp_apache():
    fmt, dt = parse_log_timestamp("07/Aug/2026:16:00:00 +0000")

    assert fmt == "Apache/nginx access log"
    assert dt.day == 7
    assert dt.month == 8


def test_parse_log_timestamp_syslog_assumes_current_year():
    fmt, dt = parse_log_timestamp("Aug  7 16:00:00")

    assert fmt == "syslog (year assumed)"
    assert dt.year == datetime.now().year
    assert dt.month == 8
    assert dt.day == 7


def test_parse_log_timestamp_unrecognized_returns_none():
    fmt, dt = parse_log_timestamp("not a timestamp at all")

    assert fmt is None
    assert dt is None


def test_calculate_log_duration_same_format():
    result = calculate_log_duration("07/Aug/2026:16:00:00 +0000", "07/Aug/2026:18:30:00 +0000")

    assert result["ok"] is True
    assert result["duration_display"] == "2h 30m 0s"
    assert result["duration_seconds"] == 9000


def test_calculate_log_duration_mixed_formats():
    result = calculate_log_duration("2026-08-07T16:00:00Z", "07/Aug/2026:17:00:00 +0000")

    assert result["ok"] is True
    assert result["start_format"] == "ISO 8601"
    assert result["end_format"] == "Apache/nginx access log"
    assert result["duration_seconds"] == 3600


def test_calculate_log_duration_syslog_year_rollover():
    result = calculate_log_duration("Dec 31 23:50:00", "Jan  1 00:10:00")

    assert result["ok"] is True
    assert result["duration_seconds"] == 1200


def test_calculate_log_duration_rejects_unparseable_start():
    result = calculate_log_duration("garbage", "2026-08-07T17:00:00Z")

    assert result["ok"] is False
    assert "start timestamp" in result["error"]


def test_calculate_log_duration_rejects_unparseable_end():
    result = calculate_log_duration("2026-08-07T16:00:00Z", "garbage")

    assert result["ok"] is False
    assert "end timestamp" in result["error"]


def test_calculate_log_duration_rejects_oversized_input():
    result = calculate_log_duration("a" * 100, "2026-08-07T17:00:00Z")

    assert result["ok"] is False
    assert "64 characters" in result["error"]
