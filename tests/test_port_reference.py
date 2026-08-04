from utils import port_reference


def test_ports_data_has_unique_ports_and_valid_ranges():
    ports_seen = set()
    for entry in port_reference.PORTS:
        assert 1 <= entry.port <= 65535
        assert entry.protocol
        assert entry.name
        assert entry.description
        ports_seen.add(entry.port)
    assert len(ports_seen) == len(port_reference.PORTS)


def test_search_ports_empty_query_returns_everything():
    assert port_reference.search_ports("") == port_reference.PORTS
    assert port_reference.search_ports("   ") == port_reference.PORTS


def test_search_ports_matches_port_number():
    results = port_reference.search_ports("443")

    assert any(entry.port == 443 for entry in results)
    assert any(entry.port == 8443 for entry in results)


def test_search_ports_matches_name_case_insensitively():
    results = port_reference.search_ports("mysql")

    assert len(results) == 1
    assert results[0].name == "MySQL / MariaDB"


def test_search_ports_matches_description_substring():
    results = port_reference.search_ports("remote desktop")

    assert any(entry.name == "RDP" for entry in results)


def test_search_ports_no_match_returns_empty():
    assert port_reference.search_ports("not-a-real-service-xyz") == ()
