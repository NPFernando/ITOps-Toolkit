from __future__ import annotations

import json

from utils.jwk_pem_converter import jwk_to_pem, pem_to_jwk


# RFC 7517 Appendix A.1's own published example public key.
_RFC7517_JWK = {
    "kty": "RSA",
    "n": "0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx4cbbfAAtVT86zwu1RK7aPFFxuhDR1L6tSoc_BJECPebWKRXjBZCiFV4n3oknjhMstn64tZ_2W-5JsGY4Hc5n9yBXArwl93lqt7_RN5w6Cf0h4QyQ5v-65YGjQR0_FDW2QvzqY368QQMicAtaSqzs8KJZgnYb9c7d0zgdAZHzu6qMQvRL5hajrn1n91CbOpbISD08qNLyrdkt-bFTWhAI4vMQFh6WeZu0fM4lFd2NcRwr3XPksINHaQ-G_xBniIqbw0Ls1jF44-csFCur-kEgU8awapJzKnqDKgw",
    "e": "AQAB",
}


def test_jwk_to_pem_matches_official_rfc_example():
    result = jwk_to_pem(json.dumps(_RFC7517_JWK))

    assert result["ok"] is True
    assert "BEGIN PUBLIC KEY" in result["output"]


def test_round_trip_preserves_modulus_and_exponent():
    pem_result = jwk_to_pem(json.dumps(_RFC7517_JWK))
    back = pem_to_jwk(pem_result["output"])

    assert back["ok"] is True
    back_jwk = json.loads(back["output"])
    assert back_jwk["n"] == _RFC7517_JWK["n"]
    assert back_jwk["e"] == _RFC7517_JWK["e"]


def test_pem_to_jwk_includes_kid_when_given():
    pem_result = jwk_to_pem(json.dumps(_RFC7517_JWK))
    back = pem_to_jwk(pem_result["output"], key_id="my-key-1")

    back_jwk = json.loads(back["output"])
    assert back_jwk["kid"] == "my-key-1"


def test_rejects_non_rsa_kty():
    result = jwk_to_pem(json.dumps({"kty": "EC", "crv": "P-256"}))

    assert result["ok"] is False
    assert "Only kty" in result["error"]


def test_rejects_missing_n_or_e():
    result = jwk_to_pem(json.dumps({"kty": "RSA"}))

    assert result["ok"] is False
    assert "missing required RSA fields" in result["error"]


def test_rejects_invalid_json():
    result = jwk_to_pem("{not valid")

    assert result["ok"] is False
    assert "Invalid JSON" in result["error"]


def test_pem_to_jwk_rejects_invalid_pem():
    result = pem_to_jwk("not a pem key")

    assert result["ok"] is False
    assert "Could not parse PEM" in result["error"]


def test_rejects_empty_input():
    result = jwk_to_pem("")

    assert result["ok"] is False
