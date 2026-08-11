from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "82_Line_Ending_Converter.py")


def test_convert_to_lf_button_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("a\r\nb\r\nc")
    app.button[1].click().run()
    assert not app.exception

    assert app.text_area[1].value == "a\nb\nc"
    assert any("CRLF" in c.value for c in app.caption)


def test_convert_to_crlf_button_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_area[0].set_value("a\nb")
    app.button[0].click().run()
    assert not app.exception

    assert app.text_area[1].value == "a\r\nb"


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_area[0].set_value("a\nb")
    app.button[1].click().run()
    assert not app.exception
    before = len(app.text_area)
    assert before > 1

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.text_area) == before
