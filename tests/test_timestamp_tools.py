from utils import timestamp_tools


def test_epoch_to_datetime_seconds_in_utc():
    result = timestamp_tools.epoch_to_datetime("1735689600", "seconds", "UTC")

    assert result["ok"] is True
    assert result["iso"] == "2025-01-01T00:00:00+00:00"
    assert result["epoch_seconds"] == 1735689600
    assert result["epoch_milliseconds"] == 1735689600000


def test_epoch_to_datetime_milliseconds():
    result = timestamp_tools.epoch_to_datetime("1735689600000", "milliseconds", "UTC")

    assert result["ok"] is True
    assert result["epoch_seconds"] == 1735689600


def test_epoch_to_datetime_rejects_non_numeric_input():
    result = timestamp_tools.epoch_to_datetime("not-a-number", "seconds", "UTC")

    assert result["ok"] is False
    assert "must be a number" in result["error"]


def test_epoch_to_datetime_rejects_unknown_timezone():
    result = timestamp_tools.epoch_to_datetime("1735689600", "seconds", "Not/AZone")

    assert result["ok"] is False
    assert "Unknown timezone" in result["error"]


def test_epoch_to_datetime_rejects_unsupported_unit():
    result = timestamp_tools.epoch_to_datetime("1735689600", "microseconds", "UTC")

    assert result["ok"] is False
    assert "Unsupported unit" in result["error"]


def test_epoch_to_datetime_requires_a_value():
    result = timestamp_tools.epoch_to_datetime("", "seconds", "UTC")

    assert result["ok"] is False
    assert "Enter an epoch value" in result["error"]


def test_datetime_to_epoch_parses_iso_string():
    result = timestamp_tools.datetime_to_epoch("2025-01-01T00:00:00", "UTC")

    assert result["ok"] is True
    assert result["epoch_seconds"] == 1735689600


def test_datetime_to_epoch_rejects_unparsable_input():
    result = timestamp_tools.datetime_to_epoch("not a date", "UTC")

    assert result["ok"] is False
    assert "Could not parse" in result["error"]


def test_convert_timezone_reinterprets_across_zones():
    result = timestamp_tools.convert_timezone("2026-08-05T14:30:00", "Asia/Kolkata", "America/New_York")

    assert result["ok"] is True
    assert result["iso"].startswith("2026-08-05T05:00:00")


def test_now_timestamp_returns_current_time_fields():
    result = timestamp_tools.now_timestamp("UTC")

    assert result["ok"] is True
    assert result["epoch_seconds"] > 1_700_000_000


def test_all_common_timezones_are_valid():
    for tz_name in timestamp_tools.COMMON_TIMEZONES:
        result = timestamp_tools.now_timestamp(tz_name)
        assert result["ok"] is True, f"{tz_name} failed: {result.get('error')}"


def test_relative_description_past_and_future():
    from datetime import datetime, timezone

    reference = datetime(2026, 1, 1, tzinfo=timezone.utc)
    past = int(datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp()) - 3600
    future = int(datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp()) + 3600

    assert timestamp_tools.relative_description(past, reference) == "1h ago"
    assert timestamp_tools.relative_description(future, reference) == "in 1h"
