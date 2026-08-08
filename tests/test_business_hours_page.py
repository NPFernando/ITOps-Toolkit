from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "58_Business_Hours_Calculator.py")


def test_calculate_across_weekend_shows_metrics():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("2026-08-07T16:00:00")
    app.text_input[1].set_value("2026-08-10T10:00:00")
    app.button[0].click().run()
    assert not app.exception

    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Business hours"] == "2h 0m"
    assert metrics["Business days spanned"] == "2"


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_invalid_timestamp_shows_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_input[0].set_value("not-a-date")
    app.text_input[1].set_value("2026-08-10T10:00:00")
    app.button[0].click().run()
    assert not app.exception
    assert any("valid ISO 8601" in e.value for e in app.error)


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("2026-08-07T16:00:00")
    app.text_input[1].set_value("2026-08-10T10:00:00")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.metric)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.metric) == before
