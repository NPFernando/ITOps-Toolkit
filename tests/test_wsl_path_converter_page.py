from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "126_WSL_Path_Converter.py")


def test_convert_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value(r"C:\Users\naveen\file.txt")
    app.button[0].click().run()
    assert not app.exception

    code = " ".join(c.value for c in app.code)
    assert "/mnt/c/Users/naveen/file.txt" in code
    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in md
    assert "Path conversion complete" in md
    assert "WSL (/mnt/c/...)" in md
    assert 'role="status"' in md


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md
    assert "tool-status-note-neutral" in md
    assert "Ready for path input" in md
    assert 'role="status"' in md


def test_empty_submission_shows_warning_status():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.button[0].click().run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-warning" in md
    assert "Path conversion needs input fixes" in md
    assert 'role="alert"' in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value(r"C:\foo")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.code)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.code) == before


def test_wsl_path_converter_page_has_no_page_scoped_mobile_css():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "@media (max-width: 768px)" not in md
    assert 'data-testid="stCodeBlock"' not in md
