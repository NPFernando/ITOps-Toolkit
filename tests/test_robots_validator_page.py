from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import robots_validator


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "62_Robots_Sitemap_Validator.py")

_FAKE_RESULT = {
    "ok": True,
    "error": None,
    "domain": "example.com",
    "issues": ["Line 3: unrecognized directive 'Foo'."],
    "sitemaps": [{"url": "https://example.com/sitemap.xml", "ok": True, "detail": "Valid <urlset>."}],
}


def test_validate_renders_issues_and_sitemaps(monkeypatch):
    monkeypatch.setattr(robots_validator, "validate_robots_txt", lambda domain: _FAKE_RESULT)

    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("example.com")
    app.button[0].click().run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Syntax issues found" in markdown
    assert "1 robots.txt directive issue(s) require review." in markdown
    assert len(app.dataframe) == 2
    sitemap_frame = app.dataframe[1].value
    assert sitemap_frame.iloc[0]["Sitemap URL"] == "https://example.com/sitemap.xml"
    assert sitemap_frame.iloc[0]["Status"] == "OK"


def test_empty_domain_shows_validation_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_input[0].set_value("")
    app.button[0].click().run()
    assert not app.exception
    markdown = " ".join(block.value for block in app.markdown)
    assert "robots.txt input needs attention" in markdown
    assert "Enter a valid domain name and run the validation again." in markdown


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction(monkeypatch):
    monkeypatch.setattr(robots_validator, "validate_robots_txt", lambda domain: _FAKE_RESULT)

    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("example.com")
    app.button[0].click().run()
    assert not app.exception
    before_markdown = " ".join(block.value for block in app.markdown)
    assert "Syntax issues found" in before_markdown

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    after_markdown = " ".join(block.value for block in app.markdown)
    assert "Syntax issues found" in after_markdown
