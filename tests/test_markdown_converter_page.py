from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "60_Markdown_HTML_Converter.py")


def test_markdown_to_html_renders_code_block():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("# Hello")
    app.button[0].click().run()
    assert not app.exception

    codes = app.code
    assert len(codes) == 1
    assert "<h1>Hello</h1>" in codes[0].value


def test_direction_switch_to_html_to_markdown():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.selectbox[0].set_value("HTML to Markdown")
    app.text_area[0].set_value("<p><strong>bold</strong></p>")
    app.button[0].click().run()
    assert not app.exception

    codes = app.code
    assert "**bold**" in codes[0].value


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_area[0].set_value("# Hello")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.code)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.code) == before
