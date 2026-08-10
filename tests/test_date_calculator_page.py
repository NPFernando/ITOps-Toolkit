from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "72_Date_Calculator.py")


def test_add_days_shows_result_date():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("2026-08-10")
    app.number_input[0].set_value(90)
    app.button[0].click().run()
    assert not app.exception

    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Date"] == "2026-11-08"


def test_invalid_date_shows_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_input[0].set_value("not-a-date")
    app.button[0].click().run()
    assert not app.exception
    assert any("valid date" in e.value for e in app.error)


def test_days_between_tab_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[1].set_value("2026-01-01")
    app.text_input[2].set_value("2026-08-10")
    app.button[1].click().run()
    assert not app.exception

    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Calendar days"] == "221"


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("2026-08-10")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.metric)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.metric) == before
