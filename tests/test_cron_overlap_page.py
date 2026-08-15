from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "113_Cron_Overlap_Checker.py")


def test_check_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("*/5 * * * *")
    app.text_input[1].set_value("*/10 * * * *")
    app.button[0].click().run()
    assert not app.exception

    assert len(app.metric) == 3
    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-warning" in md
    assert "Overlaps detected" in md


def test_check_without_overlap_shows_success_status():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("0 0 * * *")
    app.text_input[1].set_value("1 0 * * *")
    app.button[0].click().run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in md
    assert "No overlaps detected" in md


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md
    assert "tool-status-note-neutral" in md
    assert "Awaiting cron input" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("*/5 * * * *")
    app.text_input[1].set_value("*/7 * * * *")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.metric)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.metric) == before
