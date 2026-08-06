from utils.m365_sku_reference import SKUS, lookup_sku, search_skus


def test_skus_have_no_duplicate_sku_strings_or_guids():
    sku_strings = [entry.sku_string for entry in SKUS]
    guids = [entry.guid for entry in SKUS]

    assert len(sku_strings) == len(set(sku_strings))
    assert len(guids) == len(set(guids))


def test_search_skus_empty_query_returns_all():
    assert search_skus("") == SKUS
    assert search_skus("   ") == SKUS


def test_search_skus_matches_by_sku_string():
    results = search_skus("SPE_E3")

    assert len(results) == 1
    assert results[0].product_name == "Microsoft 365 E3"


def test_search_skus_matches_by_guid_substring():
    results = search_skus("05e9a617")

    assert len(results) == 1
    assert results[0].sku_string == "SPE_E3"


def test_search_skus_matches_by_product_name():
    results = search_skus("business premium")

    assert results
    assert any(entry.sku_string == "SPB" for entry in results)


def test_search_skus_no_match_returns_empty():
    assert search_skus("not-a-real-sku-zzz") == ()


def test_lookup_sku_by_exact_sku_string_case_insensitive():
    entry = lookup_sku("spe_e3")

    assert entry is not None
    assert entry.product_name == "Microsoft 365 E3"


def test_lookup_sku_by_exact_guid():
    entry = lookup_sku("05e9a617-0261-4cee-bb44-138d3ef5d965")

    assert entry is not None
    assert entry.sku_string == "SPE_E3"


def test_lookup_sku_returns_none_for_unknown():
    assert lookup_sku("not-a-real-sku") is None
    assert lookup_sku("") is None
