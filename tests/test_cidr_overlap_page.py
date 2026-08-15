from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "68_CIDR_Overlap_Checker.py")


def test_overlap_found_shows_warning_and_table():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("10.0.0.0/24\n10.0.0.128/25")
    app.button[0].click().run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Overlaps detected" in markdown
    assert "overlapping pair(s) were found" in markdown
    assert len(app.dataframe) == 1


def test_no_overlap_shows_success():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_area[0].set_value("10.0.0.0/24\n192.168.0.0/24")
    app.button[0].click().run()
    assert not app.exception
    markdown = " ".join(block.value for block in app.markdown)
    assert "No overlaps found" in markdown


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_area[0].set_value("10.0.0.0/24\n192.168.0.0/24")
    app.button[0].click().run()
    assert not app.exception
    before_markdown = " ".join(block.value for block in app.markdown)
    assert "No overlaps found" in before_markdown

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    after_markdown = " ".join(block.value for block in app.markdown)
    assert "No overlaps found" in after_markdown
