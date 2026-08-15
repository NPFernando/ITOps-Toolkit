from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "117_JSON_Merge_Patch.py")


def test_merge_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value('{"a": "b"}')
    app.text_area[1].set_value('{"a": "c"}')
    app.button[0].click().run()
    assert not app.exception

    code = " ".join(c.value for c in app.code)
    assert '"a": "c"' in code
    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in md
    assert "JSON merge patch applied" in md


def test_invalid_json_shows_warning_status():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("{not valid")
    app.text_area[1].set_value("{}")
    app.button[0].click().run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-warning" in md
    assert "JSON merge patch needs attention" in md


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md
    assert "tool-status-note-neutral" in md
    assert "Ready for JSON input" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_area[0].set_value('{"a": 1}')
    app.text_area[1].set_value('{"b": 2}')
    app.button[0].click().run()
    assert not app.exception
    before = len(app.code)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.code) == before
