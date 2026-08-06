from utils import dns_propagation


def test_check_propagation_rejects_empty_domain():
    result = dns_propagation.check_propagation("", "A")

    assert result["ok"] is False
    assert "Enter a domain" in result["error"]


def test_check_propagation_rejects_unsupported_record_type():
    result = dns_propagation.check_propagation("example.com", "SOA")

    assert result["ok"] is False
    assert "Unsupported record type" in result["error"]


def test_check_propagation_rejects_oversized_domain():
    result = dns_propagation.check_propagation("x" * (dns_propagation.MAX_DOMAIN_LENGTH + 1), "A")

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_check_propagation_live_a_record_is_consistent():
    result = dns_propagation.check_propagation("example.com", "A")

    assert result["ok"] is True
    assert len(result["resolvers"]) == len(dns_propagation.PUBLIC_RESOLVERS)
    assert all(entry["ok"] for entry in result["resolvers"])
    assert result["consistent"] is True
    names = {entry["resolver_name"] for entry in result["resolvers"]}
    assert names == {name for name, _ in dns_propagation.PUBLIC_RESOLVERS}


def test_check_propagation_live_nxdomain():
    result = dns_propagation.check_propagation("this-domain-should-not-exist-itops-toolkit-test.invalid", "A")

    assert result["ok"] is True
    assert all(not entry["ok"] for entry in result["resolvers"])
    assert result["consistent"] is None
