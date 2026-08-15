from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "103_JWT_Claims_Reference.py")


def test_search_claims_shows_filtered_results():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    next(t for t in app.text_input if t.label == "Search").set_value("exp")
    next(b for b in app.button if b.label == "Search claims").click().run()
    assert not app.exception

    text = " ".join(m.value for m in app.markdown)
    assert "matching claim(s)." in text
    assert "tool-status-note-success" in text
    assert "Matching claims found" in text
    assert 'role="status"' in text
    rows = app.table[0].value
    assert any(str(claim).lower() == "exp" for claim in rows["Claim"])


def test_search_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    next(t for t in app.text_input if t.label == "Search").set_value("oauth")
    next(b for b in app.button if b.label == "Search claims").click().run()
    assert not app.exception
    before = len(app.table)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.table) == before


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md
    assert "tool-status-note-neutral" in md
    assert "Awaiting claim search" in md


def test_unmatched_search_shows_warning_status():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    next(t for t in app.text_input if t.label == "Search").set_value("zzzz-unmatched")
    next(b for b in app.button if b.label == "Search claims").click().run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-warning" in md
    assert "No claims matched this search" in md
    assert 'role="alert"' in md
    assert len(app.table) == 0
