from utils.http_status_reference import STATUSES, search_statuses


def test_statuses_have_no_duplicate_codes():
    codes = [entry.code for entry in STATUSES]

    assert len(codes) == len(set(codes))


def test_search_statuses_empty_query_returns_all():
    assert search_statuses("") == STATUSES
    assert search_statuses("   ") == STATUSES


def test_search_statuses_matches_by_code():
    results = search_statuses("404")

    assert len(results) == 1
    assert results[0].name == "Not Found"


def test_search_statuses_matches_by_category():
    results = search_statuses("5xx")

    assert results
    assert all(entry.category.startswith("5xx") for entry in results)


def test_search_statuses_matches_by_keyword():
    results = search_statuses("rate limiting")

    assert len(results) == 1
    assert results[0].code == 429


def test_search_statuses_no_match_returns_empty():
    assert search_statuses("not-a-real-status-zzz") == ()
