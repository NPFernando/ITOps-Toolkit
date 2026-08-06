from utils import security_headers


def test_check_security_headers_rejects_empty_url():
    result = security_headers.check_security_headers("")

    assert result["ok"] is False
    assert "Enter a URL" in result["error"]


def test_check_security_headers_rejects_invalid_scheme():
    result = security_headers.check_security_headers("ftp://example.com")

    assert result["ok"] is False
    assert "valid HTTP" in result["error"]


def test_check_hsts_missing():
    check = security_headers._check_hsts(None)

    assert check["present"] is False
    assert check["status"] == "fail"


def test_check_hsts_short_max_age_warns():
    check = security_headers._check_hsts("max-age=100")

    assert check["present"] is True
    assert check["status"] == "warn"
    assert "below" in check["note"]


def test_check_hsts_strong_value_passes():
    check = security_headers._check_hsts("max-age=63072000; includeSubDomains")

    assert check["status"] == "pass"


def test_check_csp_missing():
    check = security_headers._check_csp(None)

    assert check["present"] is False
    assert check["status"] == "fail"


def test_check_csp_unsafe_inline_warns():
    check = security_headers._check_csp("default-src 'self'; script-src 'unsafe-inline'")

    assert check["present"] is True
    assert check["status"] == "warn"


def test_check_csp_strict_value_passes():
    check = security_headers._check_csp("default-src 'self'")

    assert check["status"] == "pass"


def test_grade_all_pass_is_a():
    checks = [{"status": "pass"} for _ in range(6)]

    assert security_headers._grade(checks) == "A"


def test_grade_all_missing_is_f():
    checks = [{"status": "fail"} for _ in range(6)]

    assert security_headers._grade(checks) == "F"


def test_grade_mixed_results():
    checks = [{"status": "pass"}] * 3 + [{"status": "fail"}] * 3

    assert security_headers._grade(checks) == "C"


def test_check_security_headers_live_example_com():
    result = security_headers.check_security_headers("https://example.com")

    assert result["ok"] is True
    assert result["grade"] in {"A", "B", "C", "D", "F"}
    assert len(result["checks"]) == 6
    assert result["status_code"] == 200
