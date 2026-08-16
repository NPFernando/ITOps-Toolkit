from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "54_Curl_Command_Builder.py")


def test_curl_builder_produces_a_shell_quoted_command():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    next(t for t in app.text_input if t.label == "URL").set_value("https://example.com/webhook")
    next(s for s in app.selectbox if s.label == "Method").set_value("POST")
    next(t for t in app.text_area if t.label == "Headers (one per line, Key: Value)").set_value("Content-Type: application/json")
    next(t for t in app.text_area if t.label == "Body (POST/PUT/PATCH/DELETE only)").set_value('{"a": 1}')
    next(b for b in app.button if b.label == "Build command").click().run()
    assert not app.exception

    assert len(app.code) == 1
    command = app.code[0].value
    assert command.startswith("curl -X POST")
    assert "-H 'Content-Type: application/json'" in command
    assert "https://example.com/webhook" in command


def test_curl_builder_shows_validation_error_for_blank_url():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    next(b for b in app.button if b.label == "Build command").click().run()
    assert not app.exception
    assert any("Enter a URL" in e.value for e in app.error)


def test_curl_builder_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    next(t for t in app.text_input if t.label == "URL").set_value("https://example.com")
    next(b for b in app.button if b.label == "Build command").click().run()
    assert not app.exception
    assert len(app.code) == 1

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.code) == 1
