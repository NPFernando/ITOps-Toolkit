from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "37_Windows_Error_Reference.py")


def test_windows_error_reference_shows_empty_state_before_search():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Ready to search errors" in markdown


def test_search_renders_matching_result_dataframe():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("0xC0000005")
    app.button[0].click().run()
    assert not app.exception
    assert len(app.dataframe) == 1
    frame = app.dataframe[0].value
    assert "STATUS_ACCESS_VIOLATION" in frame["Name"].to_list()


def test_no_match_shows_status_message():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("not-a-real-error-keyword-zzz")
    app.button[0].click().run()
    assert not app.exception
    markdown = " ".join(block.value for block in app.markdown)
    assert "No matches found" in markdown


def test_empty_search_shows_validation_guardrail():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("   ")
    app.button[0].click().run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Windows error search input needs attention" in markdown
    assert "Enter a decimal code, hex code, category, or keyword" in markdown
