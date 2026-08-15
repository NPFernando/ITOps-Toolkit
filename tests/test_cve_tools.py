import requests

from utils import cve_tools


class _FakeResponse:
    def __init__(self, status_code=200, payload=None, raises_json=False):
        self.status_code = status_code
        self._payload = payload or {}
        self._raises_json = raises_json

    def json(self):
        if self._raises_json:
            raise ValueError("bad json")
        return self._payload


def test_lookup_cve_rejects_empty_query():
    result = cve_tools.lookup_cve("")

    assert result["ok"] is False
    assert "Enter a CVE ID" in result["error"]


def test_lookup_cve_rejects_oversized_query():
    result = cve_tools.lookup_cve("x" * (cve_tools.MAX_QUERY_LENGTH + 1))

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_cve_id_pattern_matches_valid_ids():
    assert cve_tools._CVE_ID_PATTERN.match("CVE-2021-44228")
    assert cve_tools._CVE_ID_PATTERN.match("cve-2021-44228")
    assert not cve_tools._CVE_ID_PATTERN.match("log4j")
    assert not cve_tools._CVE_ID_PATTERN.match("CVE-2021")


def test_best_cvss_prefers_v31_over_v2():
    metrics = {
        "cvssMetricV2": [{"cvssData": {"version": "2.0", "baseScore": 9.3}, "baseSeverity": "HIGH"}],
        "cvssMetricV31": [{"cvssData": {"version": "3.1", "baseScore": 10.0, "baseSeverity": "CRITICAL", "vectorString": "CVSS:3.1/AV:N"}}],
    }

    cvss = cve_tools._best_cvss(metrics)

    assert cvss["version"] == "3.1"
    assert cvss["base_score"] == 10.0
    assert cvss["base_severity"] == "CRITICAL"


def test_best_cvss_falls_back_to_v2_when_v3_absent():
    metrics = {"cvssMetricV2": [{"cvssData": {"version": "2.0", "baseScore": 9.3}, "baseSeverity": "HIGH"}]}

    cvss = cve_tools._best_cvss(metrics)

    assert cvss["version"] == "2.0"
    assert cvss["base_severity"] == "HIGH"


def test_best_cvss_returns_none_when_no_metrics():
    assert cve_tools._best_cvss({}) is None


def test_english_description_prefers_en_lang():
    descriptions = [{"lang": "es", "value": "hola"}, {"lang": "en", "value": "hello"}]

    assert cve_tools._english_description(descriptions) == "hello"


def test_english_description_falls_back_to_first_entry():
    descriptions = [{"lang": "es", "value": "hola"}]

    assert cve_tools._english_description(descriptions) == "hola"


def test_english_description_empty_list():
    assert cve_tools._english_description([]) == ""


def test_lookup_cve_uses_exact_id_params_and_uppercases(monkeypatch):
    captured = {}

    def fake_get(url, params, headers, timeout):
        captured["url"] = url
        captured["params"] = params
        captured["headers"] = headers
        captured["timeout"] = timeout
        return _FakeResponse(payload={"vulnerabilities": [{"cve": {"id": "CVE-2021-44228"}}]})

    monkeypatch.setattr(cve_tools.requests, "get", fake_get)

    result = cve_tools.lookup_cve("cve-2021-44228")

    assert result["ok"] is True
    assert captured["url"] == cve_tools.NVD_URL
    assert captured["params"] == {"cveId": "CVE-2021-44228"}
    assert captured["timeout"] == cve_tools.NVD_TIMEOUT
    assert "User-Agent" in captured["headers"]


def test_lookup_cve_uses_keyword_params_with_limit(monkeypatch):
    captured = {}

    def fake_get(url, params, headers, timeout):
        captured["params"] = params
        return _FakeResponse(payload={"vulnerabilities": [{"cve": {"id": "CVE-2021-0001"}}]})

    monkeypatch.setattr(cve_tools.requests, "get", fake_get)

    result = cve_tools.lookup_cve("log4j remote code execution")

    assert result["ok"] is True
    assert captured["params"] == {"keywordSearch": "log4j remote code execution", "resultsPerPage": cve_tools.MAX_KEYWORD_RESULTS}


def test_lookup_cve_handles_request_exception(monkeypatch):
    def fake_get(url, params, headers, timeout):
        raise requests.RequestException("timeout")

    monkeypatch.setattr(cve_tools.requests, "get", fake_get)

    result = cve_tools.lookup_cve("CVE-2021-44228")

    assert result["ok"] is False
    assert "failed" in result["error"].lower()


def test_lookup_cve_handles_404(monkeypatch):
    monkeypatch.setattr(
        cve_tools.requests,
        "get",
        lambda url, params, headers, timeout: _FakeResponse(status_code=404),
    )

    result = cve_tools.lookup_cve("CVE-2021-44228")

    assert result["ok"] is False
    assert result["error"] == "No matching CVE found."


def test_lookup_cve_handles_rate_limit(monkeypatch):
    monkeypatch.setattr(
        cve_tools.requests,
        "get",
        lambda url, params, headers, timeout: _FakeResponse(status_code=429),
    )

    result = cve_tools.lookup_cve("CVE-2021-44228")

    assert result["ok"] is False
    assert "rate limit" in result["error"].lower()


def test_lookup_cve_handles_non_200_status(monkeypatch):
    monkeypatch.setattr(
        cve_tools.requests,
        "get",
        lambda url, params, headers, timeout: _FakeResponse(status_code=503),
    )

    result = cve_tools.lookup_cve("CVE-2021-44228")

    assert result["ok"] is False
    assert "status 503" in result["error"]


def test_lookup_cve_handles_bad_json(monkeypatch):
    monkeypatch.setattr(
        cve_tools.requests,
        "get",
        lambda url, params, headers, timeout: _FakeResponse(status_code=200, raises_json=True),
    )

    result = cve_tools.lookup_cve("CVE-2021-44228")

    assert result["ok"] is False
    assert "unexpected response" in result["error"].lower()


def test_lookup_cve_handles_empty_vulnerabilities(monkeypatch):
    monkeypatch.setattr(
        cve_tools.requests,
        "get",
        lambda url, params, headers, timeout: _FakeResponse(status_code=200, payload={"vulnerabilities": []}),
    )

    result = cve_tools.lookup_cve("CVE-2021-44228")

    assert result["ok"] is False
    assert result["error"] == "No matching CVE found."


def test_lookup_cve_summarizes_success_payload(monkeypatch):
    payload = {
        "totalResults": 1,
        "vulnerabilities": [
            {
                "cve": {
                    "id": "CVE-2021-44228",
                    "vulnStatus": "Analyzed",
                    "published": "2021-12-10T00:00:00.000",
                    "lastModified": "2021-12-11T00:00:00.000",
                    "descriptions": [{"lang": "en", "value": "Example description"}],
                    "metrics": {
                        "cvssMetricV31": [
                            {
                                "cvssData": {"version": "3.1", "baseScore": 10.0, "baseSeverity": "CRITICAL"},
                                "baseSeverity": "CRITICAL",
                            }
                        ]
                    },
                    "references": [{"url": "https://example.com/a"}, {"url": "https://example.com/b"}],
                }
            }
        ],
    }
    monkeypatch.setattr(
        cve_tools.requests,
        "get",
        lambda url, params, headers, timeout: _FakeResponse(status_code=200, payload=payload),
    )

    result = cve_tools.lookup_cve("CVE-2021-44228")

    assert result["ok"] is True
    assert result["total_results"] == 1
    assert result["results"][0]["id"] == "CVE-2021-44228"
    assert result["results"][0]["cvss"]["base_severity"] == "CRITICAL"
    assert result["results"][0]["references"] == ["https://example.com/a", "https://example.com/b"]
