from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import webhook_tools


WEBHOOK_PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "29_Webhook_Tester.py")


def _run_webhook_page() -> AppTest:
    app = AppTest.from_file(WEBHOOK_PAGE, default_timeout=30)
    app.run()
    assert not app.exception
    return app


def _page_text(app: AppTest) -> str:
    parts: list[str] = []
    for collection_name in ("markdown", "warning", "error", "caption"):
        for item in getattr(app, collection_name, []):
            parts.append(str(getattr(item, "value", getattr(item, "body", ""))))
    return "\n".join(parts)


def test_webhook_page_results_persist_after_sidebar_rerun(monkeypatch):
    def fake_send_request(url: str, method: str, headers_text: str = "", body: str = ""):
        return {
            "ok": True,
            "url": url,
            "method": method,
            "status_code": 202,
            "reason": "Accepted",
            "response_time_ms": 18.6,
            "response_headers": {"Content-Type": "application/json"},
            "response_body": '{"ok":true}',
            "response_body_truncated": False,
            "error": None,
        }

    monkeypatch.setattr(webhook_tools, "send_request", fake_send_request)

    app = _run_webhook_page()
    next(t for t in app.text_input if t.label == "URL").set_value("https://example.com/webhook")
    next(b for b in app.button if b.label == "Send test request").click()
    app.run()
    assert not app.exception
    assert len(app.metric) == 3

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.metric) == 3
    assert "Ready to send a test request" not in _page_text(app)


def test_webhook_page_blank_url_shows_failure_guidance():
    app = _run_webhook_page()
    next(b for b in app.button if b.label == "Send test request").click()
    app.run()
    assert not app.exception

    text = _page_text(app)
    assert "Webhook request needs attention" in text
    assert "Provide a valid public HTTP(S) URL" in text
