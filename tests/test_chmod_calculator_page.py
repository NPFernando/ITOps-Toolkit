from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "44_Chmod_Calculator.py")


def test_chmod_page_shows_empty_state_before_input():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_chmod_page_converts_octal_to_symbolic():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    octal_input = next(t for t in app.text_input if t.key == "chmod_octal_input")
    octal_input.set_value("755").run()
    assert not app.exception

    octal_values = [m.value for m in app.metric if m.label == "Octal"]
    symbolic_values = [m.value for m in app.metric if m.label == "Symbolic"]
    assert "755" in octal_values
    assert "rwxr-xr-x" in symbolic_values


def test_chmod_page_invalid_input_shows_warning_status_note():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    octal_input = next(t for t in app.text_input if t.key == "chmod_octal_input")
    octal_input.set_value("99").run()
    assert not app.exception

    markdown = " ".join(m.value for m in app.markdown)
    assert "Invalid permission input" in markdown
    assert "tool-status-note-warning" in markdown
