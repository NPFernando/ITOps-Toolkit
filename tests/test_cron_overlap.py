from __future__ import annotations

from utils.cron_overlap import find_cron_overlaps


def test_finds_overlaps_between_every_5_and_every_7_minutes():
    result = find_cron_overlaps("*/5 * * * *", "*/7 * * * *", lookahead_days=1)

    assert result["ok"] is True
    # LCM(5, 7) = 35 minutes -- roughly 41 overlaps in a 1440-minute day.
    assert len(result["overlaps"]) > 0
    assert result["count_a"] > result["count_b"]


def test_no_overlap_for_disjoint_daily_times():
    result = find_cron_overlaps("0 0 * * *", "0 12 * * *", lookahead_days=2)

    assert result["ok"] is True
    assert result["overlaps"] == []
    assert result["count_a"] == 2
    assert result["count_b"] == 2


def test_rejects_invalid_expression():
    result = find_cron_overlaps("bogus", "* * * * *")

    assert result["ok"] is False
    assert "not a valid cron expression" in result["error"]


def test_rejects_empty_expression():
    result = find_cron_overlaps("", "* * * * *")

    assert result["ok"] is False
    assert "Enter both" in result["error"]


def test_rejects_out_of_range_lookahead():
    result = find_cron_overlaps("* * * * *", "* * * * *", lookahead_days=0)

    assert result["ok"] is False
    assert "Lookahead must be between" in result["error"]

    result2 = find_cron_overlaps("* * * * *", "* * * * *", lookahead_days=91)
    assert result2["ok"] is False
