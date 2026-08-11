from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "81_Byte_Size_Converter.py")


def test_bytes_to_human_tab_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("1536")
    app.button[0].click().run()
    assert not app.exception

    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Size"] == "1.50 KiB"


def test_human_to_bytes_tab_shows_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[1].set_value("5")
    app.selectbox[0].set_value("GiB")
    app.button[1].click().run()
    assert not app.exception

    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Bytes"] == str(5 * 1024**3)


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("1536")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.metric)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.metric) == before
