from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "127_Markdown_Link_Extractor.py")


def test_extract_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("Check out [Google](https://google.com).")
    app.button[0].click().run()
    assert not app.exception

    assert len(app.dataframe) > 0
    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in md
    assert "Extraction complete" in md


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md
    assert "tool-status-note-neutral" in md
    assert "Awaiting Markdown input" in md


def test_input_without_links_shows_warning_status():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("This line has no Markdown links.")
    app.button[0].click().run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-warning" in md
    assert "Link extraction needs attention" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_area[0].set_value("[Google](https://google.com)")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.dataframe)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.dataframe) == before
