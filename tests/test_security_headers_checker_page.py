from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import security_headers


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "31_Security_Headers_Checker.py")


def _page_text(app: AppTest) -> str:
    parts: list[str] = []
    for collection_name in ("markdown", "warning", "error", "success"):
        for item in getattr(app, collection_name, []):
            parts.append(str(getattr(item, "value", getattr(item, "body", ""))))
    return "\n".join(parts)


def test_security_headers_checker_shows_metrics_and_rows(monkeypatch):
    monkeypatch.setattr(
        security_headers,
        "check_security_headers",
        lambda _: {
            "ok": True,
            "grade": "A",
            "status_code": 200,
            "response_time_ms": 120,
            "checks": [
                {
                    "header": "Strict-Transport-Security",
                    "status": "pass",
                    "value": "max-age=63072000; includeSubDomains",
                    "note": "Configured",
                }
            ],
        },
    )

    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("https://example.com")
    next(b for b in app.button if b.label == "Check headers").click()
    app.run()
    assert not app.exception

    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Grade"] == "A"
    assert metrics["Status code"] == "200"
    assert len(app.dataframe) == 1
    text = _page_text(app)
    assert "Headers check completed" in text
    assert 'role="status"' in text


def test_security_headers_checker_empty_state_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_security_headers_checker_blank_url_shows_accessible_failure_note():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    next(b for b in app.button if b.label == "Check headers").click()
    app.run()
    assert not app.exception

    text = _page_text(app)
    assert "Security headers check needs attention" in text
    assert "Retry the check or verify the target URL is reachable from this network." in text
    assert 'role="alert"' in text
