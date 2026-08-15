from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "108_CSV_Column_Selector.py")


def test_select_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("name,age,city\nAlice,30,NYC")
    app.text_input[0].set_value("city, name")
    app.button[0].click().run()
    assert not app.exception

    code = " ".join(c.value for c in app.code)
    assert "city,name" in code
    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in md
    assert "Column selection complete" in md
    assert 'role="status"' in md
    assert 'aria-live="polite"' in md


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md
    assert "tool-status-note-neutral" in md
    assert "Awaiting tabular input" in md
    assert 'role="status"' in md


def test_empty_submission_shows_warning_status():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.button[0].click().run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-warning" in md
    assert "Column selection needs attention" in md
    assert 'role="alert"' in md
    assert 'aria-live="assertive"' in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_area[0].set_value("a,b\n1,2")
    app.text_input[0].set_value("a")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.code)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.code) == before


def test_mobile_styles_present():
    source = Path(PAGE).read_text(encoding="utf-8")
    assert 'submitted = st.form_submit_button("Select columns", use_container_width=True)' in source
    assert 'st.download_button("Download as .csv"' in source
    assert 'mark_page_baseline(_baseline, "shell-ready")' in source
    assert 'mark_page_baseline(_baseline, "content-rendered")' in source
