from __future__ import annotations

from utils.iso8601_duration import build_duration, parse_duration


def test_parse_full_duration():
    result = parse_duration("P3Y6M4DT12H30M5S")

    assert result["ok"] is True
    assert result["output"] == "3 years, 6 months, 4 days, 12 hours, 30 minutes, 5 seconds"


def test_parse_time_only():
    result = parse_duration("PT1H")

    assert result["ok"] is True
    assert result["output"] == "1 hour"


def test_parse_singular_vs_plural():
    result = parse_duration("P1D")

    assert result["output"] == "1 day"


def test_parse_fractional_value():
    result = parse_duration("P1.5D")

    assert result["ok"] is True
    assert result["output"] == "1.5 days"


def test_parse_rejects_bare_p():
    result = parse_duration("P")

    assert result["ok"] is False


def test_parse_rejects_bare_t():
    result = parse_duration("PT")

    assert result["ok"] is False


def test_parse_rejects_invalid_format():
    result = parse_duration("bogus")

    assert result["ok"] is False
    assert "not a valid ISO 8601 duration" in result["error"]


def test_parse_rejects_empty_input():
    result = parse_duration("")

    assert result["ok"] is False


def test_build_basic():
    result = build_duration(years=1, days=2)

    assert result["ok"] is True
    assert result["output"] == "P1Y2D"


def test_build_time_only():
    result = build_duration(hours=3, minutes=30)

    assert result["ok"] is True
    assert result["output"] == "PT3H30M"


def test_build_round_trips_through_parse():
    built = build_duration(years=3, months=6, days=4, hours=12, minutes=30, seconds=5)
    parsed = parse_duration(built["output"])

    assert parsed["ok"] is True
    assert parsed["units"] == {"years": 3.0, "months": 6.0, "days": 4.0, "hours": 12.0, "minutes": 30.0, "seconds": 5.0}


def test_build_rejects_all_zero():
    result = build_duration()

    assert result["ok"] is False
    assert "at least one non-zero" in result["error"]


def test_build_rejects_negative_value():
    # Regression: a negative value used to be misreported as "enter at
    # least one non-zero component" (technically true but misleading --
    # -1 IS non-zero) instead of the actual problem, because the all-zero
    # check ran before the negativity check.
    result = build_duration(years=-1)

    assert result["ok"] is False
    assert result["error"] == "Duration components must be non-negative."
