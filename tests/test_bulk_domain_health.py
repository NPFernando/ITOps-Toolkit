from utils import bulk_domain_health


def test_parse_domain_list_splits_lines_dedupes_and_skips_header():
    raw = "Domain\nexample.com\nexample.org, extra, columns\nexample.com\n\n  example.net  "

    result = bulk_domain_health.parse_domain_list(raw)

    assert result == ["example.com", "example.org", "example.net"]


def test_parse_domain_list_handles_empty_input():
    assert bulk_domain_health.parse_domain_list("") == []
    assert bulk_domain_health.parse_domain_list(None) == []


def _fake_dns_summary(domain, include_dmarc=True):
    return {"status": "Healthy", "mx_found": True, "spf_found": True, "dmarc_found": include_dmarc}


def _fake_ssl_result(domain, port=443):
    return {"ok": True, "days_remaining": 60, "error": None}


def _fake_http_result(domain):
    return {"ok": True, "status_code": 200, "error": None}


def test_run_bulk_health_check_aggregates_rows(monkeypatch):
    monkeypatch.setattr(bulk_domain_health, "get_dns_summary", _fake_dns_summary)
    monkeypatch.setattr(bulk_domain_health, "get_certificate_info", _fake_ssl_result)
    monkeypatch.setattr(bulk_domain_health, "check_http_status", _fake_http_result)

    results = bulk_domain_health.run_bulk_health_check(["example.com", "example.org"])

    assert len(results) == 2
    assert results[0]["domain"] == "example.com"
    assert results[0]["risk_status"] in {"Healthy", "Warning", "Critical"}
    assert results[0]["http_status"] == 200
    assert results[0]["ssl_days_remaining"] == 60
    assert results[0]["error"] is None


def test_run_bulk_health_check_caps_batch_size(monkeypatch):
    monkeypatch.setattr(bulk_domain_health, "get_dns_summary", _fake_dns_summary)
    monkeypatch.setattr(bulk_domain_health, "get_certificate_info", _fake_ssl_result)
    monkeypatch.setattr(bulk_domain_health, "check_http_status", _fake_http_result)

    domains = [f"example{i}.com" for i in range(bulk_domain_health.MAX_DOMAINS_PER_BATCH + 10)]
    results = bulk_domain_health.run_bulk_health_check(domains)

    assert len(results) == bulk_domain_health.MAX_DOMAINS_PER_BATCH


def test_run_bulk_health_check_reports_per_domain_errors_without_stopping(monkeypatch):
    monkeypatch.setattr(bulk_domain_health, "get_dns_summary", _fake_dns_summary)
    monkeypatch.setattr(bulk_domain_health, "get_certificate_info", _fake_ssl_result)
    monkeypatch.setattr(bulk_domain_health, "check_http_status", _fake_http_result)

    results = bulk_domain_health.run_bulk_health_check(["a" * 300, "example.com"])

    assert results[0]["error"] is not None
    assert results[0]["risk_status"] == "Unknown"
    assert results[1]["domain"] == "example.com"
    assert results[1]["error"] is None
