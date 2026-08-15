from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "18_Regex_Tester.py")


def test_test_pattern_shows_matches_table():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value(r"\d+")
    app.text_area[0].set_value("Error 404, then 503.")
    app.button[0].click().run()
    assert not app.exception

    assert len(app.dataframe) == 1


def test_invalid_pattern_shows_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_input[0].set_value("(")
    app.text_area[0].set_value("text")
    app.button[0].click().run()
    assert not app.exception
    assert any("Invalid pattern" in e.value for e in app.error)


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md
