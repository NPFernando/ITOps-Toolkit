from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "83_Regex_Find_Replace.py")


def test_replace_shows_output():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("foo")
    app.text_input[1].set_value("XXX")
    app.text_area[0].set_value("foo bar foo baz")
    app.button[0].click().run()
    assert not app.exception

    assert app.text_area[1].value == "XXX bar XXX baz"
    assert any("2 replacement" in c.value for c in app.caption)


def test_invalid_pattern_shows_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_input[0].set_value("(")
    app.text_input[1].set_value("x")
    app.text_area[0].set_value("text")
    app.button[0].click().run()
    assert not app.exception
    assert any("Invalid pattern" in e.value for e in app.error)


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("foo")
    app.text_input[1].set_value("XXX")
    app.text_area[0].set_value("foo bar")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.text_area)
    assert before > 1

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.text_area) == before
