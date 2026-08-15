from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import latency_trend


UPTIME_TREND_PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "30_Uptime_Trend.py")


def _run_uptime_page() -> AppTest:
    app = AppTest.from_file(UPTIME_TREND_PAGE, default_timeout=60)
    app.run()
    assert not app.exception
    return app


def _page_text(app: AppTest) -> str:
    parts: list[str] = []
    for collection_name in ("markdown", "warning", "error", "caption"):
        for item in getattr(app, collection_name, []):
            parts.append(str(getattr(item, "value", getattr(item, "body", ""))))
    return "\n".join(parts)


def test_uptime_trend_results_persist_after_sidebar_rerun(monkeypatch):
    def fake_run_latency_trend(url: str, checks: int, interval_seconds: float):
        return {
            "ok": True,
            "url": url,
            "samples": [
                {"index": 1, "ok": True, "status_code": 200, "response_time_ms": 90.0, "error": None},
                {"index": 2, "ok": True, "status_code": 200, "response_time_ms": 110.0, "error": None},
                {"index": 3, "ok": True, "status_code": 200, "response_time_ms": 100.0, "error": None},
            ],
            "uptime_pct": 100.0,
            "avg_latency_ms": 100.0,
            "min_latency_ms": 90.0,
            "max_latency_ms": 110.0,
            "error": None,
        }

    monkeypatch.setattr(latency_trend, "run_latency_trend", fake_run_latency_trend)

    app = _run_uptime_page()
    next(t for t in app.text_input if t.label == "URL").set_value("https://example.com")
    next(b for b in app.button if b.label == "Run uptime probe").click()
    app.run(timeout=60)
    assert not app.exception
    assert len(app.metric) == 4
    assert "Probe completed" in _page_text(app)

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run(timeout=60)
    assert not app.exception
    assert len(app.metric) == 4
    assert "Probe completed" in _page_text(app)
    assert "Ready to run an uptime probe" not in _page_text(app)


def test_uptime_trend_blank_url_shows_failure_guidance():
    app = _run_uptime_page()
    next(b for b in app.button if b.label == "Run uptime probe").click()
    app.run(timeout=60)
    assert not app.exception

    text = _page_text(app)
    assert "Uptime probe needs attention" in text
    assert "Provide a valid public HTTP(S) URL and rerun the probe." in text
