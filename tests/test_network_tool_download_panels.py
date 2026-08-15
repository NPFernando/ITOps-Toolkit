from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import dns_tools, http_tools, ssl_tools


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DNS_PAGE = str(PROJECT_ROOT / "pages" / "2_DNS_Record_Checker.py")
SSL_PAGE = str(PROJECT_ROOT / "pages" / "3_SSL_Certificate_Checker.py")
HTTP_PAGE = str(PROJECT_ROOT / "pages" / "4_HTTP_Status_Checker.py")


def test_dns_page_clicking_download_does_not_hide_results(monkeypatch):
    monkeypatch.setattr(
        dns_tools,
        "resolve_records",
        lambda domain, record_type: {
            "ok": True,
            "status": "Healthy",
            "records": [{"name": domain, "type": record_type, "value": "203.0.113.10"}],
            "raw_values": ["203.0.113.10"],
            "query_name": domain,
            "error": None,
        },
    )

    app = AppTest.from_file(DNS_PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("example.com")
    app.button[0].click().run()
    assert not app.exception
    assert len(app.dataframe) > 0
    assert app.download_button

    app.download_button[0].click().run()
    assert not app.exception
    assert len(app.dataframe) > 0


def test_ssl_page_clicking_download_does_not_hide_results(monkeypatch):
    monkeypatch.setattr(
        ssl_tools,
        "get_certificate_info",
        lambda domain, port=443: {
            "ok": True,
            "tls_status": "Healthy",
            "error": None,
            "verification_ok": True,
            "days_remaining": 120,
            "port": port,
            "chain_status": "Trusted",
            "chain_explanation": "Certificate chain verified successfully.",
            "subject": {"commonName": domain},
            "issuer": {"commonName": "Example CA"},
            "valid_from": datetime(2025, 1, 1, tzinfo=UTC),
            "valid_until": datetime(2026, 12, 31, tzinfo=UTC),
            "san_names": [domain, f"www.{domain}"],
        },
    )

    app = AppTest.from_file(SSL_PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("example.com")
    app.button[0].click().run()
    assert not app.exception
    assert len(app.dataframe) > 0
    assert app.download_button

    app.download_button[0].click().run()
    assert not app.exception
    assert len(app.dataframe) > 0


def test_http_page_clicking_download_does_not_hide_results(monkeypatch):
    monkeypatch.setattr(
        http_tools,
        "check_http_status",
        lambda url: {
            "ok": True,
            "error": None,
            "status_code": 200,
            "reason": "OK",
            "response_time_ms": 42.0,
            "uses_https": True,
            "final_url": "https://example.com",
            "url": url,
            "headers": {"strict-transport-security": "max-age=31536000"},
            "redirect_chain": [{"status_code": 301, "location": "https://example.com"}],
            "recommendations": [],
        },
    )

    app = AppTest.from_file(HTTP_PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("https://example.com")
    app.button[0].click().run()
    assert not app.exception
    assert len(app.dataframe) > 0
    assert app.download_button

    app.download_button[0].click().run()
    assert not app.exception
    assert len(app.dataframe) > 0
