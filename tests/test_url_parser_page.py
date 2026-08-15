from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "65_URL_Parser.py")


def test_parse_shows_components_and_query_table():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("https://example.com:8443/path?a=1&b=2#frag")
    app.button[0].click().run()
    assert not app.exception

    summary = app.dataframe[0].value.to_dict("records")
    summary_by_component = {row["Component"]: row["Value"] for row in summary}
    assert summary_by_component["Scheme"] == "https"
    assert summary_by_component["Host"] == "example.com"
    assert summary_by_component["Port"] == "8443"
    assert len(app.dataframe) == 2
    markdown = " ".join(block.value for block in app.markdown)
    assert "URL parsed" in markdown
    assert "tool-status-note-success" in markdown


def test_empty_input_shows_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_input[0].set_value("")
    app.button[0].click().run()
    assert not app.exception
    markdown = " ".join(block.value for block in app.markdown)
    assert "URL input needs attention" in markdown
    assert "tool-status-note-warning" in markdown


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("https://example.com:8443/path?a=1")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.dataframe)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.dataframe) == before


def test_parse_without_query_or_fragment_shows_explicit_state_cues():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("https://example.com/path")
    app.button[0].click().run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "No fragment" in markdown
    assert "No query parameters" in markdown
    assert markdown.count("tool-status-note-neutral") >= 2
