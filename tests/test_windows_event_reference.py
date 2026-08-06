from utils.windows_event_reference import EVENTS, search_events


def test_events_have_no_duplicate_ids():
    ids = [entry.event_id for entry in EVENTS]

    assert len(ids) == len(set(ids))


def test_search_events_empty_query_returns_all():
    assert search_events("") == EVENTS
    assert search_events("   ") == EVENTS


def test_search_events_matches_by_id():
    results = search_events("4625")

    assert len(results) == 1
    assert results[0].event_id == 4625


def test_search_events_matches_by_log_name():
    results = search_events("security")

    assert results
    assert all(entry.log.lower() == "security" for entry in results)


def test_search_events_matches_by_keyword_in_summary():
    results = search_events("account was locked out")

    assert len(results) == 1
    assert results[0].event_id == 4740


def test_search_events_no_match_returns_empty():
    assert search_events("not-a-real-event-keyword-zzz") == ()


def test_search_events_is_case_insensitive():
    assert search_events("KERBEROS") == search_events("kerberos")
