from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "20_Text_Diff_Checker.py")


def test_text_diff_page_shows_empty_state_before_compare():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Ready to compare" in markdown


def test_text_diff_page_compares_and_persists_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("line1\nline2")
    app.text_area[1].set_value("line1\nline2 changed")
    next(button for button in app.button if button.label == "Compare").click().run()
    assert not app.exception
    assert any(metric.label == "Similarity" for metric in app.metric)

    search = next(widget for widget in app.text_input if widget.key == "sidebar_quick_search")
    search.set_value("diff").run()
    assert not app.exception
    assert any(metric.label == "Similarity" for metric in app.metric)


def test_text_diff_page_shows_explicit_success_status_note():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("line1")
    app.text_area[1].set_value("line1 changed")
    next(button for button in app.button if button.label == "Compare").click().run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Comparison complete" in markdown
    assert "tool-status-note-success" in markdown
