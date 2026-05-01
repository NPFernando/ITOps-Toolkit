from __future__ import annotations

from datetime import UTC, datetime

from utils.reporting import build_domain_health_html_report


def _sample_report_inputs():
    dns_summary = {
        "status": "Healthy",
        "email_status": "Warning",
        "spf_found": True,
        "dmarc_found": False,
        "email_security_posture": {
            "status": "Warning",
            "rows": [
                {
                    "check": "DNSSEC",
                    "value": "No DS or DNSKEY found",
                    "status": "Warning",
                    "recommendation": "Publish DNSSEC DS records at the registrar and DNSKEY records in the zone.",
                },
                {
                    "check": "MTA-STS TXT",
                    "value": "Missing",
                    "status": "Warning",
                    "recommendation": "Publish _mta-sts TXT with v=STSv1 and host the HTTPS policy file.",
                },
            ],
            "recommendations": [
                "Publish DNSSEC DS records at the registrar and DNSKEY records in the zone.",
                "Publish _mta-sts TXT with v=STSv1 and host the HTTPS policy file.",
            ],
        },
        "lookups": {
            "A": {"raw_values": ["203.0.113.10"], "status": "Healthy"},
            "AAAA": {"raw_values": [], "status": "No Answer"},
            "MX": {"raw_values": ["10 mail.example.com"], "status": "Healthy"},
        },
    }
    ssl_result = {
        "tls_status": "Healthy",
        "subject": {"commonName": "example.com"},
        "issuer": {"commonName": "Example CA"},
        "valid_from": datetime(2025, 4, 30, tzinfo=UTC),
        "valid_until": datetime(2030, 4, 30, tzinfo=UTC),
        "days_remaining": 365,
        "error": None,
    }
    http_result = {
        "ok": True,
        "status_code": 200,
        "reason": "OK",
        "response_time_ms": 120.5,
        "final_url": "https://example.com",
        "uses_https": True,
        "recommendations": ["Add a Content-Security-Policy header."],
        "error": None,
    }
    risk = {
        "score": 85,
        "status": "Healthy",
        "deductions": [{"points": 15, "reason": "Missing DMARC record."}],
        "recommendations": ["Missing DMARC record."],
    }
    rows = [
        {"section": "Summary", "check": "Risk score", "value": 85, "status": "Healthy"},
        {"section": "DNS", "check": "DMARC", "value": "Missing", "status": "Warning"},
    ]
    return dns_summary, ssl_result, http_result, risk, rows


def test_domain_health_html_report_contains_expected_sections():
    dns_summary, ssl_result, http_result, risk, rows = _sample_report_inputs()

    html = build_domain_health_html_report(
        "example.com",
        dns_summary,
        ssl_result,
        http_result,
        risk,
        rows,
        generated_at=datetime(2026, 4, 30, 12, 0, tzinfo=UTC),
    )

    assert "Domain Health Report" in html
    assert "example.com" in html
    assert "Generated 2026-04-30 12:00:00 UTC" in html
    assert "Risk score" in html
    assert "85" in html
    assert "DNS And Email Security" in html
    assert "Email Security Posture" in html
    assert "Publish DNSSEC DS records" in html
    assert "SSL Certificate" in html
    assert "HTTP Reachability" in html
    assert "Missing DMARC record." in html
    assert "Add a Content-Security-Policy header." in html


def test_domain_health_html_report_escapes_user_controlled_values():
    dns_summary, ssl_result, http_result, risk, rows = _sample_report_inputs()
    dns_summary["lookups"]["A"]["raw_values"] = ['<b>bad</b> & "quoted"']

    html = build_domain_health_html_report(
        'bad.example"><script>alert(1)</script>',
        dns_summary,
        ssl_result,
        http_result,
        risk,
        rows,
    )

    assert "bad.example&quot;&gt;&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "&lt;b&gt;bad&lt;/b&gt; &amp; &quot;quoted&quot;" in html
    assert '<script>alert(1)</script>' not in html
    assert "<b>bad</b>" not in html


def test_domain_health_html_report_handles_missing_values():
    html = build_domain_health_html_report(
        "example.com",
        {"lookups": {}, "status": None, "email_status": None, "spf_found": False, "dmarc_found": None},
        {"tls_status": None, "subject": {}, "issuer": {}, "error": None},
        {"ok": False, "recommendations": []},
        {"score": None, "status": None, "deductions": [], "recommendations": []},
        [],
    )

    assert "Unknown" in html
    assert "No score deductions." in html
    assert "No major recommendations from the current checks." in html
    assert "No summary rows available." in html


def test_domain_health_html_report_has_no_active_scripts_or_external_assets():
    dns_summary, ssl_result, http_result, risk, rows = _sample_report_inputs()

    html = build_domain_health_html_report("example.com", dns_summary, ssl_result, http_result, risk, rows)
    lowered = html.lower()

    assert "<script" not in lowered
    assert " src=" not in lowered
    assert " href=" not in lowered
    assert "@import" not in lowered
    assert "url(" not in lowered
