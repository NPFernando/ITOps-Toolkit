from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "35_DKIM_Selector_Lookup.py")


def test_dkim_selector_lookup_shows_empty_state_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Ready to look up a DKIM selector" in markdown


def test_dkim_selector_lookup_submit_renders_result(monkeypatch):
    monkeypatch.setattr(
        "utils.dkim_tools.lookup_dkim",
        lambda domain, selector: {
            "ok": True,
            "status": "Healthy",
            "error": "",
            "query_name": f"{selector}._domainkey.{domain}",
            "fields": {"v": "DKIM1", "k": "rsa", "p": "ABC123"},
            "raw_value": "v=DKIM1; k=rsa; p=ABC123",
        },
    )

    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("example.com")
    app.text_input[1].set_value("default")
    app.button[0].click().run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Status: Healthy" in markdown
    assert len(app.dataframe) == 1


def test_dkim_selector_lookup_requires_selector():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("example.com")
    app.text_input[1].set_value("   ")
    app.button[0].click().run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "DKIM input needs attention" in markdown
    assert "Provide a valid public domain and DKIM selector" in markdown


def test_dkim_selector_lookup_unknown_status_uses_neutral_note(monkeypatch):
    monkeypatch.setattr(
        "utils.dkim_tools.lookup_dkim",
        lambda domain, selector: {
            "ok": True,
            "status": "Unknown",
            "error": "",
            "query_name": f"{selector}._domainkey.{domain}",
            "fields": {"v": "DKIM1", "k": "rsa", "p": ""},
            "raw_value": "v=DKIM1; k=rsa; p=",
        },
    )

    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("example.com")
    app.text_input[1].set_value("default")
    app.button[0].click().run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Status: Unknown" in markdown
    assert 'role="status"' in markdown
