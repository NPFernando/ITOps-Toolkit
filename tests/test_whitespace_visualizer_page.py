from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "71_Whitespace_Visualizer.py")
NBSP = chr(0x00A0)


def test_flagged_characters_show_warning_and_table():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value(f"hello{NBSP}world")
    app.button[0].click().run()
    assert not app.exception

    assert any("character(s) flagged" in w.value for w in app.warning)
    assert len(app.table) == 1


def test_clean_text_shows_success():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_area[0].set_value("clean text")
    app.button[0].click().run()
    assert not app.exception
    assert any("No invisible" in s.value for s in app.success)


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_area[0].set_value("clean text")
    app.button[0].click().run()
    assert not app.exception
    assert any("No invisible" in s.value for s in app.success)

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert any("No invisible" in s.value for s in app.success)
