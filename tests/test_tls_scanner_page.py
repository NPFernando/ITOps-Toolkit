from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import tls_scanner


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "57_TLS_Protocol_Scanner.py")

_FAKE_RESULT = {
    "ok": True,
    "error": None,
    "host": "example.com",
    "port": 443,
    "results": [
        {"version": "SSLv3", "status": "not_testable", "detail": "Not testable in this environment."},
        {"version": "TLSv1.2", "status": "accepted", "detail": "Negotiated cipher: ECDHE-RSA-AES128-GCM-SHA256."},
    ],
}


def test_scan_renders_results_table(monkeypatch):
    monkeypatch.setattr(tls_scanner, "scan_tls", lambda host, port=443: _FAKE_RESULT)

    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("example.com")
    app.button[0].click().run()
    assert not app.exception

    tables = app.table
    assert len(tables) == 1
    rendered = str(tables[0].value)
    assert "Not testable" in rendered
    assert "Accepted" in rendered


def test_empty_host_shows_validation_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_input[0].set_value("")
    app.button[0].click().run()
    assert not app.exception
    assert any("Enter a host name" in e.value for e in app.error)


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction(monkeypatch):
    monkeypatch.setattr(tls_scanner, "scan_tls", lambda host, port=443: _FAKE_RESULT)

    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("example.com")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.table)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.table) == before
