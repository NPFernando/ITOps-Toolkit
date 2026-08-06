from utils import cve_tools


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


def test_lookup_cve_live_exact_id():
    result = cve_tools.lookup_cve("CVE-2021-44228")

    assert result["ok"] is True
    assert len(result["results"]) == 1
    entry = result["results"][0]
    assert entry["id"] == "CVE-2021-44228"
    assert entry["cvss"]["base_severity"] == "CRITICAL"
    assert "log4j" in entry["description"].lower() or "jndi" in entry["description"].lower()


def test_lookup_cve_live_keyword_search():
    result = cve_tools.lookup_cve("log4j remote code execution")

    assert result["ok"] is True
    assert len(result["results"]) > 0
    assert result["total_results"] > 0
