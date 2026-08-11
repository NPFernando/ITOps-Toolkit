from __future__ import annotations

from utils.http_methods_reference import HTTP_METHODS, search_http_methods


def test_empty_query_returns_all():
    assert search_http_methods("") == HTTP_METHODS


def test_search_by_method_name():
    # "GET" also substring-matches HEAD's description ("Like GET, but..."),
    # so this checks membership rather than an exact single-result count.
    results = search_http_methods("GET")

    assert any(entry.method == "GET" for entry in results)


def test_search_by_keyword_is_case_insensitive():
    results = search_http_methods("PREFLIGHT")

    assert any(entry.method == "OPTIONS" for entry in results)


def test_search_no_match_returns_empty():
    assert search_http_methods("nonexistent-method-xyz") == ()


def test_get_and_head_are_safe_idempotent_and_cacheable():
    by_method = {entry.method: entry for entry in HTTP_METHODS}
    for method in ("GET", "HEAD"):
        assert by_method[method].safe is True
        assert by_method[method].idempotent is True
        assert by_method[method].cacheable is True


def test_post_and_patch_are_not_idempotent():
    by_method = {entry.method: entry for entry in HTTP_METHODS}
    assert by_method["POST"].idempotent is False
    assert by_method["PATCH"].idempotent is False


def test_put_and_delete_are_idempotent_but_not_safe():
    by_method = {entry.method: entry for entry in HTTP_METHODS}
    for method in ("PUT", "DELETE"):
        assert by_method[method].safe is False
        assert by_method[method].idempotent is True


def test_methods_are_unique():
    methods = [entry.method for entry in HTTP_METHODS]
    assert len(methods) == len(set(methods))
