from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "48_TOTP_Generator.py")


def test_totp_page_shows_empty_state_before_secret():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Ready for a secret" in markdown


def test_totp_page_shows_failure_note_for_invalid_secret():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    next(widget for widget in app.text_input if widget.label == "Base32 secret").set_value("%%%%").run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Secret input needs attention" in markdown
    assert "tool-status-note-warning" in markdown
