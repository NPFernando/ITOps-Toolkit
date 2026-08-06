from utils import latency_trend


def _fake_check_ok(url):
    return {"ok": True, "status_code": 200, "response_time_ms": 42.0, "error": None}


def _fake_check_failing(url):
    return {"ok": False, "status_code": None, "response_time_ms": None, "error": "Connection failed"}


def test_run_latency_trend_collects_samples_and_summary(monkeypatch):
    monkeypatch.setattr(latency_trend, "check_http_status", _fake_check_ok)
    monkeypatch.setattr(latency_trend.time, "sleep", lambda seconds: None)

    result = latency_trend.run_latency_trend("example.com", checks=5, interval_seconds=1.0)

    assert result["ok"] is True
    assert len(result["samples"]) == 5
    assert [s["index"] for s in result["samples"]] == [1, 2, 3, 4, 5]
    assert result["uptime_pct"] == 100.0
    assert result["avg_latency_ms"] == 42.0
    assert result["min_latency_ms"] == 42.0
    assert result["max_latency_ms"] == 42.0


def test_run_latency_trend_skips_sleep_after_last_check(monkeypatch):
    monkeypatch.setattr(latency_trend, "check_http_status", _fake_check_ok)
    sleep_calls = []
    monkeypatch.setattr(latency_trend.time, "sleep", lambda seconds: sleep_calls.append(seconds))

    latency_trend.run_latency_trend("example.com", checks=4, interval_seconds=2.0)

    assert len(sleep_calls) == 3


def test_run_latency_trend_zero_interval_never_sleeps(monkeypatch):
    monkeypatch.setattr(latency_trend, "check_http_status", _fake_check_ok)
    sleep_calls = []
    monkeypatch.setattr(latency_trend.time, "sleep", lambda seconds: sleep_calls.append(seconds))

    latency_trend.run_latency_trend("example.com", checks=5, interval_seconds=0)

    assert sleep_calls == []


def test_run_latency_trend_computes_partial_uptime_with_failures(monkeypatch):
    calls = {"n": 0}

    def alternating_check(url):
        calls["n"] += 1
        return _fake_check_ok(url) if calls["n"] % 2 == 1 else _fake_check_failing(url)

    monkeypatch.setattr(latency_trend, "check_http_status", alternating_check)
    monkeypatch.setattr(latency_trend.time, "sleep", lambda seconds: None)

    result = latency_trend.run_latency_trend("example.com", checks=4, interval_seconds=0)

    assert result["uptime_pct"] == 50.0
    assert result["avg_latency_ms"] == 42.0
    assert sum(1 for s in result["samples"] if not s["ok"]) == 2


def test_run_latency_trend_all_failures_has_no_latency_stats(monkeypatch):
    monkeypatch.setattr(latency_trend, "check_http_status", _fake_check_failing)
    monkeypatch.setattr(latency_trend.time, "sleep", lambda seconds: None)

    result = latency_trend.run_latency_trend("example.com", checks=3, interval_seconds=0)

    assert result["uptime_pct"] == 0.0
    assert result["avg_latency_ms"] is None
    assert result["min_latency_ms"] is None
    assert result["max_latency_ms"] is None


def test_run_latency_trend_rejects_empty_url():
    result = latency_trend.run_latency_trend("", checks=5, interval_seconds=1.0)

    assert result["ok"] is False
    assert "Enter a URL" in result["error"]


def test_run_latency_trend_rejects_out_of_range_checks():
    assert "between" in latency_trend.run_latency_trend("example.com", checks=1, interval_seconds=1.0)["error"]
    assert "between" in latency_trend.run_latency_trend("example.com", checks=100, interval_seconds=1.0)["error"]


def test_run_latency_trend_rejects_out_of_range_interval():
    result = latency_trend.run_latency_trend("example.com", checks=5, interval_seconds=999)

    assert result["ok"] is False
    assert "Interval must be between" in result["error"]
