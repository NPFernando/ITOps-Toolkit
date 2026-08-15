from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "47_HTTP_Status_Reference.py")


def test_http_status_reference_page_renders_results_table():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception
    assert len(app.dataframe) == 1


def test_http_status_reference_page_filters_by_search():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    next(widget for widget in app.text_input if widget.label == "Search").set_value("404")
    next(button for button in app.button if button.label == "Search").click().run()
    assert not app.exception

    frame = app.dataframe[0].value
    assert len(frame) == 1
    assert frame.iloc[0]["Code"] == 404


def test_http_status_reference_page_shows_no_match_message():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    next(widget for widget in app.text_input if widget.label == "Search").set_value("not-a-real-status-zzz")
    next(button for button in app.button if button.label == "Search").click().run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "No matching status codes" in markdown
    assert "No status codes matched that search." in markdown
    assert "tool-status-note-neutral" in markdown
