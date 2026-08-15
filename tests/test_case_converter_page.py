from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "25_Case_Converter.py")


def test_case_converter_page_shows_empty_state_before_convert():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Ready to convert" in markdown


def test_case_converter_page_shows_converted_values():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("hello world")
    next(button for button in app.button if button.label == "Convert").click().run()
    assert not app.exception

    values = [widget.value for widget in app.text_input if widget.label != "Search tools"]
    assert "hello-world" in values
    assert "helloWorld" in values

    markdown = " ".join(block.value for block in app.markdown)
    assert "Conversion complete" in markdown
    assert "tool-status-note-success" in markdown
