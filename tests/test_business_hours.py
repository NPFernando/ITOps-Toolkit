from __future__ import annotations

from datetime import time

from utils.business_hours import calculate_business_hours


def test_calculate_business_hours_across_a_weekend():
    # Friday 4pm -> Monday 10am: 1 hour Friday (4-5pm) + 1 hour Monday (9-10am).
    result = calculate_business_hours("2026-08-07T16:00:00", "2026-08-10T10:00:00", "UTC")

    assert result["ok"] is True
    assert result["business_hours"] == 2.0
    assert result["business_hours_display"] == "2h 0m"
    assert result["business_days_spanned"] == 2


def test_calculate_business_hours_same_day_full_window():
    result = calculate_business_hours("2026-08-10T09:00:00", "2026-08-10T17:00:00", "UTC")

    assert result["ok"] is True
    assert result["business_hours"] == 8.0


def test_calculate_business_hours_excludes_holiday():
    result = calculate_business_hours("2026-08-07T16:00:00", "2026-08-10T10:00:00", "UTC", holidays_str="2026-08-10")

    assert result["ok"] is True
    assert result["business_hours"] == 1.0
    assert result["business_days_spanned"] == 1


def test_calculate_business_hours_swaps_reversed_order():
    forward = calculate_business_hours("2026-08-10T09:00:00", "2026-08-10T17:00:00", "UTC")
    reversed_result = calculate_business_hours("2026-08-10T17:00:00", "2026-08-10T09:00:00", "UTC")

    assert reversed_result["business_hours"] == forward["business_hours"]


def test_calculate_business_hours_rejects_empty_input():
    result = calculate_business_hours("", "2026-08-10T10:00:00", "UTC")

    assert result["ok"] is False
    assert result["error"] == "Enter both a start and end timestamp."


def test_calculate_business_hours_rejects_invalid_timestamp():
    result = calculate_business_hours("not-a-date", "2026-08-10T10:00:00", "UTC")

    assert result["ok"] is False
    assert "valid ISO 8601" in result["error"]


def test_calculate_business_hours_rejects_unknown_timezone():
    result = calculate_business_hours("2026-08-10T09:00:00", "2026-08-10T17:00:00", "Not/AZone")

    assert result["ok"] is False
    assert "Unknown timezone" in result["error"]


def test_calculate_business_hours_rejects_invalid_holiday_format():
    result = calculate_business_hours("2026-08-07T16:00:00", "2026-08-10T10:00:00", "UTC", holidays_str="not-a-date")

    assert result["ok"] is False
    assert "Invalid holiday date" in result["error"]


def test_calculate_business_hours_ignores_weekend_entirely():
    # Saturday 9am -> Sunday 5pm: entirely weekend, zero business hours.
    result = calculate_business_hours("2026-08-08T09:00:00", "2026-08-09T17:00:00", "UTC")

    assert result["ok"] is True
    assert result["business_hours"] == 0.0
    assert result["business_days_spanned"] == 0


def test_calculate_business_hours_rejects_inverted_business_window():
    result = calculate_business_hours("2026-08-10T09:00:00", "2026-08-10T17:00:00", "UTC", business_start=time(18, 0), business_end=time(9, 0))

    assert result["ok"] is False
    assert "start must be before" in result["error"]
