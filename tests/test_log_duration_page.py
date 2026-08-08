from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "64_Log_Timestamp_Duration_Calculator.py")


def test_calculate_shows_duration_metric():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("07/Aug/2026:16:00:00 +0000")
    app.text_input[1].set_value("07/Aug/2026:18:30:00 +0000")
    app.button[0].click().run()
    assert not app.exception

    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Duration"] == "2h 30m 0s"


def test_unparseable_timestamp_shows_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_input[0].set_value("garbage")
    app.text_input[1].set_value("2026-08-07T17:00:00Z")
    app.button[0].click().run()
    assert not app.exception
    assert any("start timestamp" in e.value for e in app.error)


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("07/Aug/2026:16:00:00 +0000")
    app.text_input[1].set_value("07/Aug/2026:18:30:00 +0000")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.metric)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.metric) == before
