from utils.windows_error_reference import ERRORS, search_errors


def test_errors_have_no_duplicate_codes():
    codes = [entry.code for entry in ERRORS]

    assert len(codes) == len(set(codes))


def test_search_errors_empty_query_returns_all():
    assert search_errors("") == ERRORS
    assert search_errors("   ") == ERRORS


def test_search_errors_matches_by_decimal_code():
    results = search_errors("1326")

    assert len(results) == 1
    assert results[0].name == "ERROR_LOGON_FAILURE"


def test_search_errors_matches_by_hex_code():
    results = search_errors("0xC0000005")

    assert len(results) == 1
    assert results[0].name == "STATUS_ACCESS_VIOLATION"


def test_search_errors_matches_hex_case_insensitively():
    assert search_errors("0xc0000005") == search_errors("0xC0000005")


def test_search_errors_matches_by_category():
    results = search_errors("hresult")

    assert results
    assert all(entry.category == "HRESULT" for entry in results)


def test_search_errors_matches_by_keyword():
    results = search_errors("trust relationship")

    assert results
    assert any("trust" in entry.description.lower() for entry in results)


def test_search_errors_no_match_returns_empty():
    assert search_errors("not-a-real-error-keyword-zzz") == ()
