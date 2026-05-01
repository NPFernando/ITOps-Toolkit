from __future__ import annotations

from datetime import UTC, datetime

from streamlit.testing.v1 import AppTest

from utils import dns_tools, http_tools, reporting, ssl_tools


DOMAIN_PAGE = "pages/1_Domain_Health_Checker.py"


def test_domain_health_submitted_page_shows_html_download(monkeypatch):
    def fake_dns_summary(domain, include_dmarc=True):
        healthy = {"records": [{"type": "A", "value": "203.0.113.10"}], "raw_values": ["203.0.113.10"], "status": "Healthy"}
        return {
            "domain": domain,
            "lookups": {
                "A": healthy,
                "AAAA": {"records": [], "raw_values": [], "status": "No Answer"},
                "MX": {"records": [{"value": "10 mail.example.com"}], "raw_values": ["10 mail.example.com"], "status": "Healthy"},
                "TXT": {"records": [{"value": "v=spf1 include:_spf.example.com"}], "raw_values": ["v=spf1 include:_spf.example.com"], "status": "Healthy"},
                "SPF": {"records": [{"value": "v=spf1 include:_spf.example.com"}], "raw_values": ["v=spf1 include:_spf.example.com"], "status": "Healthy"},
                "DMARC": {"records": [{"value": "v=DMARC1; p=none"}], "raw_values": ["v=DMARC1; p=none"], "status": "Healthy"},
            },
            "status": "Healthy",
            "email_status": "Healthy",
            "a_found": True,
            "aaaa_found": False,
            "mx_found": True,
            "spf_found": True,
            "dmarc_found": True,
            "email_security_posture": {
                "status": "Healthy",
                "rows": [
                    {"check": "DNSSEC", "value": "DS or DNSKEY found", "status": "Healthy", "recommendation": ""},
                    {"check": "MTA-STS TXT", "value": "v=STSv1 found", "status": "Healthy", "recommendation": ""},
                ],
                "recommendations": [],
            },
        }

    def fake_ssl_result(domain):
        return {
            "ok": True,
            "tls_status": "Healthy",
            "subject": {"commonName": domain},
            "issuer": {"commonName": "Example CA"},
            "valid_from": datetime(2025, 4, 30, tzinfo=UTC),
            "valid_until": datetime(2030, 4, 30, tzinfo=UTC),
            "days_remaining": 365,
            "error": None,
        }

    def fake_http_result(domain):
        return {
            "ok": True,
            "status_code": 200,
            "reason": "OK",
            "response_time_ms": 123.4,
            "final_url": f"https://{domain}",
            "uses_https": True,
            "redirect_chain": [],
            "recommendations": [],
            "error": None,
        }

    captured_report = {}

    def fake_html_report(domain, dns_summary, ssl_result, http_result, risk, summary_rows):
        captured_report.update(
            {
                "domain": domain,
                "dns_status": dns_summary["status"],
                "http_status": http_result["status_code"],
                "risk_score": risk["score"],
                "summary_rows": summary_rows,
            }
        )
        return "<!doctype html><html><body>report</body></html>"

    monkeypatch.setattr(dns_tools, "get_dns_summary", fake_dns_summary)
    monkeypatch.setattr(ssl_tools, "get_certificate_info", fake_ssl_result)
    monkeypatch.setattr(http_tools, "check_http_status", fake_http_result)
    monkeypatch.setattr(reporting, "build_domain_health_html_report", fake_html_report)

    app = AppTest.from_file(DOMAIN_PAGE, default_timeout=60)
    app.run()
    app.text_input[0].set_value("example.com")
    app.button[0].click()
    app.run(timeout=60)

    assert not app.exception
    assert captured_report["domain"] == "example.com"
    assert captured_report["dns_status"] == "Healthy"
    assert captured_report["http_status"] == 200
    assert captured_report["risk_score"] == 100
    assert any(row["check"] == "Risk score" for row in captured_report["summary_rows"])
    assert any(row["check"] == "DNSSEC" for row in captured_report["summary_rows"])
