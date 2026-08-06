from utils.cron_builder import build_cron_expression


def _every(**overrides):
    defaults = {
        "minute_mode": "Every", "minute_step": 0, "minute_values": [],
        "hour_mode": "Every", "hour_step": 0, "hour_values": [],
        "day_mode": "Every", "day_step": 0, "day_values": [],
        "month_mode": "Every", "month_step": 0, "month_values": [],
        "weekday_mode": "Every", "weekday_step": 0, "weekday_values": [],
    }
    defaults.update(overrides)
    return build_cron_expression(
        defaults["minute_mode"], defaults["minute_step"], defaults["minute_values"],
        defaults["hour_mode"], defaults["hour_step"], defaults["hour_values"],
        defaults["day_mode"], defaults["day_step"], defaults["day_values"],
        defaults["month_mode"], defaults["month_step"], defaults["month_values"],
        defaults["weekday_mode"], defaults["weekday_step"], defaults["weekday_values"],
    )


def test_build_cron_all_every_fields():
    result = _every()

    assert result["ok"] is True
    assert result["expression"] == "* * * * *"


def test_build_cron_every_n_minutes():
    result = _every(minute_mode="Every N", minute_step=15)

    assert result["ok"] is True
    assert result["expression"] == "*/15 * * * *"


def test_build_cron_specific_values():
    result = _every(minute_mode="Specific", minute_values=[0], hour_mode="Specific", hour_values=[9], weekday_mode="Specific", weekday_values=[1, 2, 3, 4, 5])

    assert result["ok"] is True
    assert result["expression"] == "0 9 * * 1,2,3,4,5"
    assert result["description"]
    assert len(result["next_runs"]) == 5


def test_build_cron_specific_dedupes_and_sorts_values():
    result = _every(minute_mode="Specific", minute_values=[30, 0, 30, 15])

    assert result["expression"].startswith("0,15,30 ")


def test_build_cron_rejects_empty_specific_values():
    result = _every(minute_mode="Specific", minute_values=[])

    assert result["ok"] is False
    assert "Choose at least one minute value" in result["error"]


def test_build_cron_rejects_out_of_range_values():
    result = _every(hour_mode="Specific", hour_values=[25])

    assert result["ok"] is False
    assert "Hour values must be between 0 and 23" in result["error"]


def test_build_cron_rejects_zero_step():
    result = _every(minute_mode="Every N", minute_step=0)

    assert result["ok"] is False
    assert "step must be at least 1" in result["error"]
