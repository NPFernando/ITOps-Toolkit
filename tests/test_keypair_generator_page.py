from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "49_RSA_SSH_Key_Pair_Generator.py")


def test_keypair_page_shows_empty_state_before_generate():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Ready to generate" in markdown


def test_keypair_page_shows_success_note_after_generate():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    next(button for button in app.button if button.label == "Generate key pair").click().run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Key pair generated" in markdown
    assert "tool-status-note-success" in markdown

