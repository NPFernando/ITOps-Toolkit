from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import dns_propagation


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "33_DNS_Propagation_Checker.py")


def _page_text(app: AppTest) -> str:
    parts: list[str] = []
    for collection_name in ("markdown", "warning", "error", "success"):
        for item in getattr(app, collection_name, []):
            parts.append(str(getattr(item, "value", getattr(item, "body", ""))))
    return "\n".join(parts)


def test_dns_propagation_checker_shows_consistency_and_table(monkeypatch):
    monkeypatch.setattr(
        dns_propagation,
        "check_propagation",
        lambda *_: {
            "ok": True,
            "consistent": True,
            "resolvers": [
                {
                    "resolver_name": "Google",
                    "resolver_ip": "8.8.8.8",
                    "status": "ok",
                    "ok": True,
                    "records": [{"record": "93.184.216.34", "ttl": 300}],
                    "error": "",
                }
            ],
        },
    )

    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("example.com")
    app.button[0].click().run()
    assert not app.exception

    text = _page_text(app)
    assert "Resolvers agree" in text
    assert 'role="status"' in text
    assert len(app.dataframe) == 1


def test_dns_propagation_checker_empty_state_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_dns_propagation_checker_blank_domain_shows_accessible_failure_note():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.button[0].click().run()
    assert not app.exception

    text = _page_text(app)
    assert "DNS propagation input needs attention" in text
    assert "Enter a valid public domain and rerun the lookup." in text
    assert 'role="alert"' in text
