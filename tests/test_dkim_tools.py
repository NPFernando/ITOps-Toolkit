from utils import dkim_tools


def test_lookup_dkim_rejects_empty_domain():
    result = dkim_tools.lookup_dkim("", "selector1")

    assert result["ok"] is False
    assert "Enter a domain" in result["error"]


def test_lookup_dkim_rejects_empty_selector():
    result = dkim_tools.lookup_dkim("example.com", "")

    assert result["ok"] is False
    assert "Enter a DKIM selector" in result["error"]


def test_lookup_dkim_rejects_oversized_domain():
    result = dkim_tools.lookup_dkim("x" * (dkim_tools.MAX_DOMAIN_LENGTH + 1), "s1")

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_lookup_dkim_rejects_oversized_selector():
    result = dkim_tools.lookup_dkim("example.com", "x" * (dkim_tools.MAX_SELECTOR_LENGTH + 1))

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_parse_dkim_record_extracts_fields():
    fields = dkim_tools._parse_dkim_record("v=DKIM1; k=rsa; p=ABC123")

    assert fields == {"v": "DKIM1", "k": "rsa", "p": "ABC123"}


def test_parse_dkim_record_handles_missing_equals_gracefully():
    fields = dkim_tools._parse_dkim_record("not-a-real-field; p=ABC")

    assert fields == {"p": "ABC"}


def test_lookup_dkim_live_paypal_com_healthy():
    result = dkim_tools.lookup_dkim("paypal.com", "pp-dkim1")

    assert result["ok"] is True
    assert result["status"] == "Healthy"
    assert result["fields"].get("v", "").upper() == "DKIM1"
    assert result["fields"].get("p")


def test_lookup_dkim_live_nxdomain_selector():
    result = dkim_tools.lookup_dkim("this-domain-should-not-exist-itops-toolkit-test.invalid", "selector1")

    assert result["ok"] is False
    assert result["status"] == "NXDOMAIN"


def test_lookup_dkim_live_revoked_key_still_ok_but_warns():
    result = dkim_tools.lookup_dkim("example.com", "default")

    assert result["ok"] is True
    assert result["status"] == "Warning"
    assert "public key" in result["error"]
