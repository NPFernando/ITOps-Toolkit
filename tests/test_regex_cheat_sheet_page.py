from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils.regex_reference import REGEX_PATTERNS


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "55_Regex_Cheat_Sheet.py")


def test_regex_cheat_sheet_shows_all_patterns_by_default():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    assert len(app.table) == 1
    assert len(app.table[0].value) == len(REGEX_PATTERNS)


def test_regex_cheat_sheet_search_narrows_results():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    next(t for t in app.text_input if t.label == "Search").set_value("email").run()
    assert not app.exception

    rows = app.table[0].value
    assert len(rows) >= 1
    assert all("email" in str(name).lower() for name in rows["Name"])


def test_regex_cheat_sheet_no_match_shows_info():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    next(t for t in app.text_input if t.label == "Search").set_value("not-a-real-pattern-keyword").run()
    assert not app.exception
    assert any("No patterns matched" in i.value for i in app.info)
