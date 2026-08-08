from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "61_Text_Encoding_Detector.py")


def test_upload_detects_encoding():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.get("file_uploader")[0].upload("sample.txt", b"hello world", "text/plain")
    app.button[0].click().run()
    assert not app.exception

    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Encoding"] == "ascii"
    assert metrics["Confidence"] == "100.0%"


def test_no_upload_shows_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.button[0].click().run()
    assert not app.exception
    assert any("Upload a file" in e.value for e in app.error)


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.get("file_uploader")[0].upload("sample.txt", b"hello world", "text/plain")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.metric)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.metric) == before
