from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "50_QR_Code_Generator.py")


def test_qr_page_shows_empty_state_before_input():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Ready for input" in markdown


def test_qr_page_shows_success_note_for_text_qr():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    next(widget for widget in app.text_input if widget.label == "Text or URL").set_value("https://example.com").run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "QR code generated" in markdown
    assert "tool-status-note-success" in markdown

