from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "142_Text_to_Binary_Hex_Octal_Converter.py")


def test_text_radix_page_shows_neutral_state_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Outcome: conversion awaiting input" in markdown
    assert "tool-status-note-neutral" in markdown
    assert 'role="status"' in markdown
    assert 'aria-live="polite"' in markdown


def test_text_radix_page_converts_ascii_text_to_binary_hex_and_octal():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("Az")
    next(widget for widget in app.button if widget.label == "Convert text").click().run()
    assert not app.exception

    assert len(app.code) == 1
    output = app.code[0].value
    assert "Binary: 01000001 01111010" in output
    assert "Hex: 41 7A" in output
    assert "Octal: 101 172" in output

    markdown = " ".join(block.value for block in app.markdown)
    assert "tool-status-note-success" in markdown
    assert "Outcome: text conversion complete" in markdown


def test_text_radix_page_requires_non_empty_input():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    next(widget for widget in app.button if widget.label == "Convert text").click().run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "tool-status-note-warning" in markdown
    assert "Outcome: text conversion blocked" in markdown
    assert 'role="alert"' in markdown
