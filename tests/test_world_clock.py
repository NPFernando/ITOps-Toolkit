from __future__ import annotations

from utils.world_clock import world_clock


def test_world_clock_basic():
    result = world_clock("2026-03-05T14:30", "UTC")

    assert result["ok"] is True
    zones = {z["zone"]: z for z in result["zones"]}
    assert zones["UTC"]["local_time"] == "2026-03-05 14:30 UTC"
    assert "New_York" in zones["America/New_York"]["zone"]


def test_world_clock_day_offset_detected():
    result = world_clock("2026-03-05T23:30", "UTC")

    assert result["ok"] is True
    zones = {z["zone"]: z for z in result["zones"]}
    # Tokyo is far enough ahead of UTC that 23:30 UTC rolls into the next day.
    assert zones["Asia/Tokyo"]["day_offset"] == 1


def test_world_clock_accepts_space_separated_datetime():
    result = world_clock("2026-03-05 14:30", "UTC")

    assert result["ok"] is True


def test_world_clock_rejects_empty_input():
    result = world_clock("", "UTC")

    assert result["ok"] is False
    assert result["error"] == "Enter a date and time."


def test_world_clock_rejects_malformed_datetime():
    result = world_clock("not-a-datetime", "UTC")

    assert result["ok"] is False
    assert "Enter a date/time" in result["error"]


def test_world_clock_rejects_unknown_timezone():
    result = world_clock("2026-03-05T14:30", "Bogus/Zone")

    assert result["ok"] is False
    assert "Unknown timezone" in result["error"]


def test_world_clock_rejects_timezone_aware_input():
    result = world_clock("2026-03-05T14:30+05:00", "UTC")

    assert result["ok"] is False
    assert "timezone-naive" in result["error"]
