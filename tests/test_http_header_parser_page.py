from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "67_HTTP_Header_Parser.py")


def test_parse_shows_table_and_request_line():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("HTTP/1.1 200 OK\nContent-Type: application/json\n")
    app.button[0].click().run()
    assert not app.exception

    assert any("HTTP/1.1 200 OK" in c.value for c in app.caption)
    tables = app.table
    assert len(tables) == 1


def test_invalid_line_shows_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_area[0].set_value("not a valid header line")
    app.button[0].click().run()
    assert not app.exception
    assert any("Could not parse line" in e.value for e in app.error)


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_area[0].set_value("Content-Type: application/json\n")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.table)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.table) == before
