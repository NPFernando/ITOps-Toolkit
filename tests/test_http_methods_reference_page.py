from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "109_HTTP_Methods_Reference.py")


def test_search_shows_matching_results():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("GET")
    app.button[0].click().run()
    assert not app.exception

    table_text = " ".join(str(t.value) for t in app.table)
    assert "GET" in table_text
    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in md
    assert "Search complete" in md
    assert 'role="status"' in md
    assert 'aria-live="polite"' in md


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md
    assert "tool-status-note-neutral" in md
    assert "Awaiting search" in md
    assert 'role="status"' in md


def test_no_matches_shows_warning_status():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("not-a-real-method")
    app.button[0].click().run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-warning" in md
    assert "No matches found" in md
    assert 'role="alert"' in md
    assert 'aria-live="assertive"' in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("GET")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.table)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.table) == before
