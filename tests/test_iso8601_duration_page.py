from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "116_ISO8601_Duration_Tool.py")


def test_parse_tab_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("PT1H")
    app.button[0].click().run()
    assert not app.exception

    assert any("1 hour" in s.value for s in app.success)
    markdown = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in markdown
    assert "Parsed successfully" in markdown


def test_build_tab_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.number_input[4].set_value(3)
    app.button[1].click().run()
    assert not app.exception

    code = " ".join(c.value for c in app.code)
    assert "PT3H" in code
    markdown = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in markdown
    assert "Built successfully" in markdown


def test_parse_invalid_duration_shows_warning_status():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("bogus")
    app.button[0].click().run()
    assert not app.exception

    markdown = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-warning" in markdown
    assert "ISO 8601 parse needs attention" in markdown


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md
    assert md.count("tool-status-note-neutral") >= 2


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("PT1H")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.success)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.success) == before
