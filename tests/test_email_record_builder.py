from utils import email_record_builder as erb


def test_build_spf_record_basic():
    result = erb.build_spf_record(["_spf.google.com"], ["203.0.113.10"], [], "-all")

    assert result["ok"] is True
    assert result["record"] == "v=spf1 ip4:203.0.113.10 include:_spf.google.com -all"
    assert result["warnings"] == []


def test_build_spf_record_rejects_unknown_all_mechanism():
    result = erb.build_spf_record([], [], [], "*all")

    assert result["ok"] is False
    assert "Unknown 'all' mechanism" in result["error"]


def test_build_spf_record_warns_on_empty_senders():
    result = erb.build_spf_record([], [], [], "-all")

    assert result["ok"] is True
    assert any("authorizes nothing" in w for w in result["warnings"])


def test_build_spf_record_warns_over_lookup_limit():
    includes = [f"sender{i}.example.com" for i in range(erb.MAX_SPF_LOOKUPS + 1)]
    result = erb.build_spf_record(includes, [], [], "-all")

    assert result["ok"] is True
    assert any("exceed the" in w for w in result["warnings"])


def test_build_dmarc_record_basic():
    result = erb.build_dmarc_record("quarantine", ["reports@example.com"])

    assert result["ok"] is True
    assert result["record"] == "v=DMARC1; p=quarantine; rua=mailto:reports@example.com"
    assert result["warnings"] == []


def test_build_dmarc_record_rejects_unknown_policy():
    result = erb.build_dmarc_record("banish", [])

    assert result["ok"] is False
    assert "Unknown policy" in result["error"]


def test_build_dmarc_record_rejects_pct_out_of_range():
    result = erb.build_dmarc_record("none", [], pct=150)

    assert result["ok"] is False
    assert "pct must be between" in result["error"]


def test_build_dmarc_record_warns_without_rua():
    result = erb.build_dmarc_record("none", [])

    assert result["ok"] is True
    assert any("rua" in w for w in result["warnings"])


def test_build_dmarc_record_warns_on_full_reject():
    result = erb.build_dmarc_record("reject", ["r@example.com"], pct=100)

    assert any("immediately rejects" in w for w in result["warnings"])


def test_build_dmarc_record_includes_optional_fields():
    result = erb.build_dmarc_record(
        "quarantine",
        ["r@example.com"],
        ruf=["f@example.com"],
        subdomain_policy="reject",
        pct=50,
        adkim="strict",
        aspf="strict",
    )

    assert result["record"] == (
        "v=DMARC1; p=quarantine; sp=reject; rua=mailto:r@example.com; "
        "ruf=mailto:f@example.com; pct=50; adkim=s; aspf=s"
    )


def test_build_dkim_record_basic():
    result = erb.build_dkim_record("default", "example.com", "ABC123")

    assert result["ok"] is True
    assert result["record"] == "v=DKIM1; k=rsa; p=ABC123"
    assert result["query_name"] == "default._domainkey.example.com"


def test_build_dkim_record_strips_pem_whitespace():
    key = "ABC\n123\n  DEF  "
    result = erb.build_dkim_record("s1", "example.com", key)

    assert result["record"] == "v=DKIM1; k=rsa; p=ABC123DEF"


def test_build_dkim_record_requires_all_fields():
    assert erb.build_dkim_record("", "example.com", "key")["ok"] is False
    assert erb.build_dkim_record("s1", "", "key")["ok"] is False
    assert erb.build_dkim_record("s1", "example.com", "")["ok"] is False
