from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "119_SSH_Config_Validator.py")


def test_lint_shows_clean_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("Host prod\n    User admin")
    app.button[0].click().run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in md
    assert "Lint complete" in md


def test_lint_shows_issues():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("User root\nHost prod\n    HostName 1.2.3.4")
    app.button[0].click().run()
    assert not app.exception

    assert len(app.table) > 0
    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-warning" in md
    assert "Lint issues detected" in md


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md
    assert "tool-status-note-neutral" in md
    assert "Awaiting SSH config" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_area[0].set_value("Host prod\n    User admin")
    app.button[0].click().run()
    assert not app.exception
    before_markdown = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in before_markdown

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    after_markdown = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in after_markdown
