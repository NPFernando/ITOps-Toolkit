from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "85_Text_Pattern_Extractor.py")


def test_extract_shows_matching_lines():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("^error:")
    app.text_area[0].set_value("error: connection failed\ninfo: retrying\nerror: timeout\n")
    app.button[0].click().run()
    assert not app.exception

    assert len(app.dataframe) == 1


def test_no_matches_shows_info():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_input[0].set_value("zzz")
    app.text_area[0].set_value("hello\nworld\n")
    app.button[0].click().run()
    assert not app.exception
    assert any("No matching lines" in i.value for i in app.info)


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("^error:")
    app.text_area[0].set_value("error: a\ninfo: b\n")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.dataframe)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.dataframe) == before
