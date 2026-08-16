from utils import mac_tools


def test_analyze_mac_accepts_colon_format():
    result = mac_tools.analyze_mac("00:1A:2B:3C:4D:5E")

    assert result["ok"] is True
    assert result["colon"] == "00:1a:2b:3c:4d:5e"
    assert result["hyphen"] == "00-1a-2b-3c-4d-5e"
    assert result["dot"] == "001a.2b3c.4d5e"
    assert result["bare"] == "001a2b3c4d5e"
    assert result["oui"] == "00:1a:2b"
    assert result["nic"] == "3c:4d:5e"


def test_analyze_mac_accepts_hyphen_dot_and_bare_formats():
    colon_result = mac_tools.analyze_mac("00:1A:2B:3C:4D:5E")
    for variant in ["00-1A-2B-3C-4D-5E", "001A.2B3C.4D5E", "001A2B3C4D5E", "  00:1a:2b:3c:4d:5e  "]:
        assert mac_tools.analyze_mac(variant)["bare"] == colon_result["bare"]


def test_analyze_mac_unicast_and_universal_bits():
    result = mac_tools.analyze_mac("00:1A:2B:3C:4D:5E")

    assert result["is_unicast"] is True
    assert result["is_multicast"] is False
    assert result["is_universal"] is True
    assert result["is_local"] is False


def test_analyze_mac_multicast_and_locally_administered_bits():
    # 0x01 has the multicast bit set; 0x02 has the locally-administered bit set.
    multicast = mac_tools.analyze_mac("01:00:5E:00:00:01")
    local = mac_tools.analyze_mac("02:00:00:00:00:01")

    assert multicast["is_multicast"] is True
    assert multicast["is_unicast"] is False
    assert local["is_local"] is True
    assert local["is_universal"] is False


def test_analyze_mac_validation_errors():
    assert mac_tools.analyze_mac("")["error"] == "Enter a MAC address."
    assert "valid 48-bit" in mac_tools.analyze_mac("not-a-mac")["error"]
    assert "valid 48-bit" in mac_tools.analyze_mac("00:1A:2B:3C:4D")["error"]
    assert "longer than" in mac_tools.analyze_mac("a" * 100)["error"]
