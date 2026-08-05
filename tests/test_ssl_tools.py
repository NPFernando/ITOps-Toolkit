from utils import ssl_tools


def test_diagnose_chain_trusted_when_no_verify_code():
    status, explanation = ssl_tools.diagnose_chain(None, None)

    assert status == "Trusted"
    assert "verified successfully" in explanation


def test_diagnose_chain_missing_intermediate():
    status, explanation = ssl_tools.diagnose_chain(20, "unable to get local issuer certificate")

    assert status == "Missing intermediate"
    assert "intermediate" in explanation.lower()


def test_diagnose_chain_self_signed():
    status, explanation = ssl_tools.diagnose_chain(18, "self-signed certificate")

    assert status == "Self-signed"
    assert "self-signed" in explanation.lower()


def test_diagnose_chain_expired():
    status, explanation = ssl_tools.diagnose_chain(10, "certificate has expired")

    assert status == "Expired"
    assert "expired" in explanation.lower()


def test_diagnose_chain_hostname_mismatch():
    status, _ = ssl_tools.diagnose_chain(62, "hostname mismatch")

    assert status == "Hostname mismatch"


def test_diagnose_chain_unknown_code_falls_back_to_verify_message():
    status, explanation = ssl_tools.diagnose_chain(999, "some obscure openssl error")

    assert status == "Verification failed"
    assert explanation == "some obscure openssl error"
