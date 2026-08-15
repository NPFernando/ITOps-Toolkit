from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "19_Timestamp_Converter.py")


def test_convert_epoch_shows_datetime_fields():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("1735689600")
    app.button[0].click().run()
    assert not app.exception

    output_iso = [t for t in app.text_input if t.label == "ISO 8601"]
    assert output_iso
    assert output_iso[0].value.startswith("2025-01-01T00:00:00")


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("1735689600")
    app.button[0].click().run()
    assert not app.exception

    before = [t.value for t in app.text_input if t.label == "ISO 8601"]
    assert before

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception

    after = [t.value for t in app.text_input if t.label == "ISO 8601"]
    assert after == before
