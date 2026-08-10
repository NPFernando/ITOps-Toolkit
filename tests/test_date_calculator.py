from __future__ import annotations

from utils.date_calculator import add_to_date, days_between


def test_add_to_date_days():
    result = add_to_date("2026-08-10", 90, "days")

    assert result["ok"] is True
    assert result["result_date"] == "2026-11-08"
    assert result["weekday"] == "Sunday"


def test_add_to_date_weeks():
    result = add_to_date("2026-08-10", 2, "weeks")

    assert result["ok"] is True
    assert result["result_date"] == "2026-08-24"


def test_add_to_date_months_clamps_to_month_end():
    # Jan 31 + 1 month -> Feb 28 (2026 is not a leap year), not an invalid Feb 31.
    result = add_to_date("2026-01-31", 1, "months")

    assert result["ok"] is True
    assert result["result_date"] == "2026-02-28"


def test_add_to_date_months_clamps_to_leap_year_end():
    result = add_to_date("2024-01-31", 1, "months")

    assert result["result_date"] == "2024-02-29"


def test_add_to_date_negative_amount_subtracts():
    result = add_to_date("2026-08-10", -2, "weeks")

    assert result["result_date"] == "2026-07-27"


def test_add_to_date_rejects_invalid_date():
    result = add_to_date("not-a-date", 1, "days")

    assert result["ok"] is False
    assert result["error"] == "Enter a valid date (YYYY-MM-DD)."


def test_add_to_date_rejects_unknown_unit():
    result = add_to_date("2026-08-10", 1, "centuries")

    assert result["ok"] is False
    assert "Unknown unit" in result["error"]


def test_add_to_date_rejects_out_of_range_days_instead_of_crashing():
    # Regression: timedelta arithmetic raises OverflowError uncaught for a
    # result outside datetime's representable range -- an ordinary typo
    # (an extra 9 or two) must not crash the page with a raw traceback.
    result = add_to_date("2026-01-01", 999_999_999, "days")

    assert result["ok"] is False
    assert "outside the range" in result["error"]


def test_add_to_date_rejects_out_of_range_months_instead_of_crashing():
    # Regression: _add_months's date(year, ...) construction raises
    # ValueError (not OverflowError) once the computed year exceeds
    # datetime.MAXYEAR -- both exception types must be caught.
    result = add_to_date("9999-12-01", 2, "months")

    assert result["ok"] is False
    assert "outside the range" in result["error"]


def test_days_between_basic():
    result = days_between("2026-01-01", "2026-08-10")

    assert result["ok"] is True
    assert result["days"] == 221


def test_days_between_is_order_independent():
    forward = days_between("2026-01-01", "2026-08-10")
    backward = days_between("2026-08-10", "2026-01-01")

    assert forward["days"] == backward["days"]


def test_days_between_same_date_is_zero():
    result = days_between("2026-08-10", "2026-08-10")

    assert result["days"] == 0


def test_days_between_rejects_invalid_date():
    result = days_between("bad", "2026-08-10")

    assert result["ok"] is False
    assert result["error"] == "Enter two valid dates (YYYY-MM-DD)."
