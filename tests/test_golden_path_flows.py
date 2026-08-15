from __future__ import annotations

from datetime import UTC, datetime
import os
from pathlib import Path

import streamlit as st
from streamlit.testing.v1 import AppTest

from utils import dns_tools, github_issues, http_tools, roadmap, ssl_tools


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOMAIN_PAGE = str(PROJECT_ROOT / "pages" / "1_Domain_Health_Checker.py")
DNS_PAGE = str(PROJECT_ROOT / "pages" / "2_DNS_Record_Checker.py")
SSL_PAGE = str(PROJECT_ROOT / "pages" / "3_SSL_Certificate_Checker.py")
HTTP_PAGE = str(PROJECT_ROOT / "pages" / "4_HTTP_Status_Checker.py")
ROADMAP_PAGE = str(PROJECT_ROOT / "pages" / "10_Roadmap_Feedback.py")


def _fake_dns_summary(domain: str, include_dmarc: bool = True):
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
        "dmarc_found": include_dmarc,
        "email_security_posture": {
            "status": "Healthy",
            "rows": [{"check": "DNSSEC", "value": "DS or DNSKEY found", "status": "Healthy", "recommendation": ""}],
            "recommendations": [],
        },
    }


def _fake_ssl_result(domain: str, port: int = 443):
    return {
        "ok": True,
        "domain": domain,
        "port": port,
        "tls_status": "Healthy",
        "verification_ok": True,
        "chain_status": "Trusted",
        "chain_explanation": "Verified.",
        "subject": {"commonName": domain},
        "issuer": {"commonName": "Example CA"},
        "san_names": [domain],
        "valid_from": datetime(2025, 1, 1, tzinfo=UTC),
        "valid_until": datetime(2030, 1, 1, tzinfo=UTC),
        "days_remaining": 365,
        "error": None,
    }


def _fake_http_result(domain_or_url: str):
    return {
        "ok": True,
        "input_url": domain_or_url,
        "url": f"https://{domain_or_url.replace('https://', '')}",
        "status_code": 200,
        "reason": "OK",
        "response_time_ms": 55.0,
        "final_url": f"https://{domain_or_url.replace('https://', '')}",
        "uses_https": True,
        "redirect_chain": [],
        "headers": {"strict-transport-security": "max-age=31536000"},
        "recommendations": [],
        "error": None,
    }


def test_domain_health_golden_path_flow(monkeypatch):
    monkeypatch.setattr(dns_tools, "get_dns_summary", _fake_dns_summary)
    monkeypatch.setattr(ssl_tools, "get_certificate_info", lambda domain: _fake_ssl_result(domain))
    monkeypatch.setattr(http_tools, "check_http_status", _fake_http_result)

    app = AppTest.from_file(DOMAIN_PAGE, default_timeout=60)
    app.run()
    app.text_input[0].set_value("example.com")
    app.button[0].click()
    app.run(timeout=60)

    assert not app.exception
    assert len(app.dataframe) > 0


def test_dns_ssl_http_chain_pages_submit_without_errors(monkeypatch):
    monkeypatch.setattr(dns_tools, "resolve_records", lambda domain, record_type: {"ok": True, "status": "Healthy", "records": [{"type": record_type, "value": "ok"}], "raw_values": ["ok"], "query_name": domain})
    monkeypatch.setattr(ssl_tools, "get_certificate_info", lambda domain, port=443: _fake_ssl_result(domain, port))
    monkeypatch.setattr(http_tools, "check_http_status", _fake_http_result)

    dns_app = AppTest.from_file(DNS_PAGE, default_timeout=60)
    dns_app.run()
    dns_app.text_input[0].set_value("example.com")
    dns_app.button[0].click()
    dns_app.run(timeout=60)
    assert not dns_app.exception

    ssl_app = AppTest.from_file(SSL_PAGE, default_timeout=60)
    ssl_app.run()
    ssl_app.text_input[0].set_value("example.com")
    ssl_app.button[0].click()
    ssl_app.run(timeout=60)
    assert not ssl_app.exception

    http_app = AppTest.from_file(HTTP_PAGE, default_timeout=60)
    http_app.run()
    http_app.text_input[0].set_value("example.com")
    http_app.button[0].click()
    http_app.run(timeout=60)
    assert not http_app.exception


def test_roadmap_fallback_golden_path(monkeypatch):
    st.cache_data.clear()
    monkeypatch.setenv("ITOPS_CACHE_SCOPE", os.getenv("PYTEST_CURRENT_TEST", "golden-path"))
    monkeypatch.setattr(
        github_issues,
        "fetch_public_issues",
        lambda *args, **kwargs: github_issues.GitHubIssuesResult(
            (), "GitHub API rate limit reached. Showing seed roadmap data."
        ),
    )
    monkeypatch.setattr(
        roadmap,
        "load_roadmap_board",
        lambda repo_url=None: roadmap.RoadmapBoard(roadmap.ROADMAP_ITEMS, "GitHub API rate limit reached. Showing seed roadmap data."),
    )

    app = AppTest.from_file(ROADMAP_PAGE, default_timeout=60)
    app.run()

    assert not app.exception
    parts: list[str] = []
    for collection_name in ("markdown", "warning", "info", "error", "caption"):
        for item in getattr(app, collection_name, []):
            parts.append(str(getattr(item, "body", getattr(item, "value", ""))))
    text = "\n".join(parts)
    assert "GitHub roadmap sync temporarily unavailable" in text
