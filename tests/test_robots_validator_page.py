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

    assert any("1 issue" in w.value for w in app.warning)
    assert any("sitemap.xml" in s.value for s in app.success)


def test_empty_domain_shows_validation_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_input[0].set_value("")
    app.button[0].click().run()
    assert not app.exception
    assert any("Enter a domain name" in e.value for e in app.error)


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
    before = len(app.warning)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.warning) == before
