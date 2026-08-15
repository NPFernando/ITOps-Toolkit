from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "105_Robots_Meta_Tag_Builder.py")


def test_build_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.button[0].click().run()
    assert not app.exception

    code = " ".join(c.value for c in app.code)
    assert 'content="index, follow"' in code
    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-success" in md
    assert "Meta tag ready" in md
    assert 'role="status"' in md
    assert 'aria-live="polite"' in md


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md
    assert "tool-status-note-neutral" in md
    assert "Awaiting directives" in md
    assert 'role="status"' in md


def test_generation_error_shows_warning_status(monkeypatch):
    from utils import robots_meta_builder

    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    monkeypatch.setattr(
        robots_meta_builder,
        "build_robots_meta",
        lambda *_args, **_kwargs: {"ok": False, "error": "Invalid directives.", "output": None},
    )
    app.button[0].click().run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-warning" in md
    assert "Meta tag generation needs attention" in md
    assert 'role="alert"' in md
    assert 'aria-live="assertive"' in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.button[0].click().run()
    assert not app.exception
    before = len(app.code)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.code) == before
