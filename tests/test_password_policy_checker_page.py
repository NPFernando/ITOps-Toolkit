from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "115_Password_Policy_Checker.py")


def test_check_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("Abc123!@#xyz")
    app.button[0].click().run()
    assert not app.exception

    markdown = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in markdown
    assert "Compliant" in markdown


def test_non_compliant_password_shows_warning_status():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("abc")
    app.button[0].click().run()
    assert not app.exception

    markdown = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-warning" in markdown
    assert "Not compliant" in markdown


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md
    assert "tool-status-note-neutral" in md
    assert "Awaiting password input" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("Abc123!@#xyz")
    app.button[0].click().run()
    assert not app.exception
    before_markdown = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in before_markdown

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    after_markdown = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in after_markdown
