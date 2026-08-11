from __future__ import annotations

from utils.jwt_claims_reference import JWT_CLAIMS, search_jwt_claims


def test_empty_query_returns_all():
    assert search_jwt_claims("") == JWT_CLAIMS


def test_search_by_claim_key():
    results = search_jwt_claims("exp")

    assert any(entry.claim == "exp" for entry in results)


def test_search_by_name_is_case_insensitive():
    results = search_jwt_claims("SUBJECT")

    assert any(entry.claim == "sub" for entry in results)


def test_search_no_match_returns_empty():
    assert search_jwt_claims("nonexistent-claim-xyz") == ()


def test_registered_claims_present():
    claims = {entry.claim for entry in JWT_CLAIMS}
    assert {"iss", "sub", "aud", "exp", "nbf", "iat", "jti"}.issubset(claims)


def test_claim_keys_are_unique():
    claims = [entry.claim for entry in JWT_CLAIMS]
    assert len(claims) == len(set(claims))
