from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "141_Lorem_Ipsum_Generator.py")


def test_lorem_ipsum_page_shows_neutral_state_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Outcome: lorem generation awaiting input" in markdown
    assert "tool-status-note-neutral" in markdown
    assert 'role="status"' in markdown
    assert 'aria-live="polite"' in markdown


def test_lorem_ipsum_page_generates_deterministic_words_with_seed():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    seed = next(widget for widget in app.text_input if widget.key == "lorem_seed")
    seed.set_value("wave25")
    count = next(widget for widget in app.number_input if widget.key == "lorem_count")
    count.set_value(6)
    next(widget for widget in app.button if widget.label == "Generate lorem ipsum").click().run()
    assert not app.exception

    assert len(app.code) == 1
    assert app.code[0].value == "enim ullamco sit pariatur occaecat mollit"
    markdown = " ".join(block.value for block in app.markdown)
    assert "tool-status-note-success" in markdown
    assert "Outcome: lorem text generated" in markdown
