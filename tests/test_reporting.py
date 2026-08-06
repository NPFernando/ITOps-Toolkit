from __future__ import annotations

from datetime import UTC, datetime

from utils.reporting import (
    build_domain_health_html_report,
    build_domain_health_incident_message,
    build_domain_health_psa_note,
    build_log_analysis_psa_note,
    build_uptime_incident_message,
)


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


def test_domain_health_psa_note_has_no_markdown_syntax():
    dns_summary, ssl_result, http_result, risk, _rows = _sample_report_inputs()

    note = build_domain_health_psa_note(
        "example.com",
        dns_summary,
        ssl_result,
        http_result,
        risk,
        generated_at=datetime(2026, 4, 30, 12, 0, tzinfo=UTC),
    )

    assert "example.com" in note
    assert "Risk score: 85 (Healthy)" in note
    assert "SSL status: Healthy (365 days remaining)" in note
    assert "HTTP status: 200 (120.5 ms)" in note
    assert "Missing DMARC record." in note
    assert "#" not in note
    assert "**" not in note


def test_domain_health_psa_note_handles_no_recommendations():
    note = build_domain_health_psa_note(
        "example.com",
        {"status": "Healthy", "email_status": "Healthy", "email_security_posture": {}},
        {"tls_status": "Healthy", "days_remaining": 90},
        {"status_code": 200, "response_time_ms": 100, "ok": True, "recommendations": []},
        {"score": 100, "status": "Healthy", "recommendations": []},
    )

    assert "No major recommendations from the current checks." in note


def test_log_analysis_psa_note_lists_findings_plainly():
    findings = [
        {
            "severity": "Critical",
            "likely_issue": "SSL certificate error",
            "possible_cause": "The certificate may be expired.",
            "commands_to_check": ["openssl s_client -connect example.com:443"],
            "safe_next_steps": ["Check certificate validity dates."],
        }
    ]

    note = build_log_analysis_psa_note(findings, generated_at=datetime(2026, 4, 30, 12, 0, tzinfo=UTC))

    assert "[Critical] SSL certificate error" in note
    assert "Cause: The certificate may be expired." in note
    assert "openssl s_client -connect example.com:443" in note
    assert "Check certificate validity dates." in note
    assert "#" not in note
    assert "**" not in note


def test_log_analysis_psa_note_handles_empty_findings():
    note = build_log_analysis_psa_note([])

    assert "Log Troubleshooting Summary" in note
    assert "Generated by ITOps Toolkit" in note


def test_domain_health_incident_message_rejects_unknown_target():
    dns_summary, ssl_result, http_result, risk, _rows = _sample_report_inputs()

    result = build_domain_health_incident_message("example.com", dns_summary, ssl_result, http_result, risk, target="discord")

    assert result["ok"] is False
    assert "Unknown target" in result["error"]


def test_domain_health_incident_message_slack_uses_single_asterisk_bold():
    dns_summary, ssl_result, http_result, risk, _rows = _sample_report_inputs()

    result = build_domain_health_incident_message("example.com", dns_summary, ssl_result, http_result, risk, target="slack")

    assert result["ok"] is True
    assert "*Domain Health: example.com*" in result["message"]
    assert "**" not in result["message"]
    assert "example.com" in result["message"]


def test_domain_health_incident_message_teams_uses_double_asterisk_bold():
    dns_summary, ssl_result, http_result, risk, _rows = _sample_report_inputs()

    result = build_domain_health_incident_message("example.com", dns_summary, ssl_result, http_result, risk, target="teams")

    assert result["ok"] is True
    assert "**Domain Health: example.com**" in result["message"]


def test_domain_health_incident_message_includes_recommendations():
    dns_summary, ssl_result, http_result, risk, _rows = _sample_report_inputs()

    result = build_domain_health_incident_message("example.com", dns_summary, ssl_result, http_result, risk, target="slack")

    assert "Missing DMARC record." in result["message"]


def test_uptime_incident_message_rejects_unknown_target():
    result = build_uptime_incident_message("https://example.com", {"samples": []}, target="discord")

    assert result["ok"] is False
    assert "Unknown target" in result["error"]


def test_uptime_incident_message_all_successful_no_failures_section():
    trend = {
        "uptime_pct": 100,
        "avg_latency_ms": 120.0,
        "min_latency_ms": 100.0,
        "max_latency_ms": 140.0,
        "samples": [{"index": 1, "ok": True, "response_time_ms": 120.0, "error": None}],
    }

    result = build_uptime_incident_message("https://example.com", trend, target="slack")

    assert result["ok"] is True
    assert "Uptime: 100% over 1 check(s)" in result["message"]
    assert "failed check" not in result["message"]


def test_uptime_incident_message_lists_failures():
    trend = {
        "uptime_pct": 50,
        "avg_latency_ms": 200.0,
        "min_latency_ms": 200.0,
        "max_latency_ms": 200.0,
        "samples": [
            {"index": 1, "ok": True, "response_time_ms": 200.0, "error": None},
            {"index": 2, "ok": False, "response_time_ms": None, "error": "Connection failed"},
        ],
    }

    result = build_uptime_incident_message("https://example.com", trend, target="teams")

    assert "1 failed check(s):" in result["message"]
    assert "Check 2: Connection failed" in result["message"]
