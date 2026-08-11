from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "106_Cache_Control_Tool.py")


def test_build_tab_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.multiselect[0].set_value(["public"])
    app.button[0].click().run()
    assert not app.exception

    code = " ".join(c.value for c in app.code)
    assert "public" in code


def test_explain_tab_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("public, max-age=3600")
    app.button[1].click().run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "public" in md


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.multiselect[0].set_value(["public"])
    app.button[0].click().run()
    assert not app.exception
    before = len(app.code)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.code) == before
