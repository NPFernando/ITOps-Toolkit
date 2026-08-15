from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "112_Env_File_Diff.py")


def test_compare_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("A=1\nB=2")
    app.text_area[1].set_value("A=1\nB=changed")
    app.button[0].click().run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "Changed" in md
    assert "tool-status-note-warning" in md
    assert "Differences detected" in md


def test_compare_identical_files_shows_success_status():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("A=1\nB=2")
    app.text_area[1].set_value("A=1\nB=2")
    app.button[0].click().run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in md
    assert "No differences detected" in md


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md
    assert "tool-status-note-neutral" in md
    assert "Awaiting env input" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_area[0].set_value("A=1")
    app.text_area[1].set_value("A=2")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.table)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.table) == before
