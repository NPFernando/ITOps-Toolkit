from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import dns_tools, http_tools, reporting, ssl_tools


# Newer streamlit resolves AppTest.from_file()'s relative paths against the
# file that calls it (this test file's directory), not the working
# directory -- an absolute path avoids that resolution entirely.
DOMAIN_PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "1_Domain_Health_Checker.py")


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


def test_domain_health_clicking_download_does_not_hide_results(monkeypatch):
    """Regression: st.download_button triggers a rerun just like any widget outside
    st.form. Results must be keyed off session_state, not the transient `submitted`
    flag, or the whole results section disappears right after the file downloads."""

    def fake_dns_summary(domain, include_dmarc=True):
        healthy = {"records": [{"type": "A", "value": "203.0.113.10"}], "raw_values": ["203.0.113.10"], "status": "Healthy"}
        return {
            "domain": domain,
            "lookups": {
                "A": healthy,
                "AAAA": {"records": [], "raw_values": [], "status": "No Answer"},
                "MX": {"records": [], "raw_values": [], "status": "No Answer"},
                "TXT": {"records": [], "raw_values": [], "status": "No Answer"},
                "SPF": {"records": [], "raw_values": [], "status": "No Answer"},
                "DMARC": {"records": [], "raw_values": [], "status": "No Answer"},
            },
            "status": "Healthy",
            "email_status": "Warning",
            "a_found": True,
            "aaaa_found": False,
            "mx_found": False,
            "spf_found": False,
            "dmarc_found": False,
            "email_security_posture": {"status": "Warning", "rows": [], "recommendations": []},
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

    monkeypatch.setattr(dns_tools, "get_dns_summary", fake_dns_summary)
    monkeypatch.setattr(ssl_tools, "get_certificate_info", fake_ssl_result)
    monkeypatch.setattr(http_tools, "check_http_status", fake_http_result)

    app = AppTest.from_file(DOMAIN_PAGE, default_timeout=60)
    app.run()
    app.text_input[0].set_value("example.com")
    app.button[0].click()
    app.run(timeout=60)
    assert not app.exception
    assert len(app.dataframe) > 0

    app.download_button[0].click()
    app.run(timeout=60)
    assert not app.exception
    assert len(app.dataframe) > 0


def test_domain_health_www_subdomain_check_not_refetched_on_rerun(monkeypatch):
    """Regression: the www-subdomain sub-check used to call get_dns_summary/
    check_http_status directly in the always-rendered results section, so it
    re-fired those live network calls on every rerun while results were
    showing (sidebar search, another expander, any download button). It must
    now be computed once at submit time and cached, like the rest of this
    page's results."""

    call_counts = {"dns": 0, "http": 0}

    def fake_dns_summary(domain, include_dmarc=True):
        call_counts["dns"] += 1
        healthy = {"records": [{"type": "A", "value": "203.0.113.10"}], "raw_values": ["203.0.113.10"], "status": "Healthy"}
        return {
            "domain": domain,
            "lookups": {
                "A": healthy,
                "AAAA": {"records": [], "raw_values": [], "status": "No Answer"},
                "MX": {"records": [], "raw_values": [], "status": "No Answer"},
                "TXT": {"records": [], "raw_values": [], "status": "No Answer"},
                "SPF": {"records": [], "raw_values": [], "status": "No Answer"},
                "DMARC": {"records": [], "raw_values": [], "status": "No Answer"},
            },
            "status": "Healthy",
            "email_status": "Warning",
            "a_found": True,
            "aaaa_found": False,
            "mx_found": False,
            "spf_found": False,
            "dmarc_found": False,
            "email_security_posture": {"status": "Warning", "rows": [], "recommendations": []},
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
        call_counts["http"] += 1
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

    monkeypatch.setattr(dns_tools, "get_dns_summary", fake_dns_summary)
    monkeypatch.setattr(ssl_tools, "get_certificate_info", fake_ssl_result)
    monkeypatch.setattr(http_tools, "check_http_status", fake_http_result)

    app = AppTest.from_file(DOMAIN_PAGE, default_timeout=60)
    app.run()
    app.text_input[0].set_value("example.com")
    app.button[0].click()
    app.run(timeout=60)
    assert not app.exception

    # check_www defaults to True and "example.com" doesn't already start with
    # "www.", so the submit above should have triggered exactly 2 calls each
    # (one for the main domain, one for the www subdomain).
    assert call_counts == {"dns": 2, "http": 2}

    # Touch a widget outside the form (the sidebar quick-search box) -- this
    # triggers a rerun with the transient submit flag back to False, the same
    # way clicking a download button or expanding a section does.
    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run(timeout=60)
    assert not app.exception

    # Call counts must be unchanged -- the www-subdomain check must be served
    # from cached state, not re-fetched on this rerun.
    assert call_counts == {"dns": 2, "http": 2}
