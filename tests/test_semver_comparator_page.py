from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "89_SemVer_Comparator.py")


def test_compare_tab_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("1.2.3")
    app.text_input[1].set_value("1.10.0")
    app.button[0].click().run()
    assert not app.exception

    assert any("older" in s.value for s in app.success)


def test_sort_tab_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("2.0.0\n1.0.0")
    app.button[1].click().run()
    assert not app.exception

    code = " ".join(c.value for c in app.code)
    assert code == "1.0.0\n2.0.0"


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("1.2.3")
    app.text_input[1].set_value("1.2.4")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.success)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.success) == before
