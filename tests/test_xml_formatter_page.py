from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "73_XML_Formatter.py")


def test_format_action_pretty_prints():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("<root><a>1</a></root>")
    app.radio[0].set_value("Format XML")
    app.button[0].click().run()
    assert not app.exception

    codes = app.code
    assert len(codes) == 1
    assert "<a>1</a>" in codes[0].value


def test_validate_action_shows_success_no_code_block():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_area[0].set_value("<root><a>1</a></root>")
    app.radio[0].set_value("Validate XML")
    app.button[0].click().run()
    assert not app.exception
    assert any("Valid XML" in s.value for s in app.success)
    assert len(app.code) == 0


def test_malformed_xml_shows_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_area[0].set_value("<root><unclosed></root>")
    app.button[0].click().run()
    assert not app.exception
    assert any("Invalid XML" in e.value for e in app.error)


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_area[0].set_value("<root><a>1</a></root>")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.code)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.code) == before
