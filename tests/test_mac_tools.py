from utils import mac_tools


class FakeResponse:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text
        self.ok = 200 <= status_code < 300


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


def test_lookup_vendor_full_mac_uses_oui_only(monkeypatch):
    captured = {}

    def fake_get(url, timeout=None):
        captured["url"] = url
        captured["timeout"] = timeout
        return FakeResponse(text="Google, Inc.")

    monkeypatch.setattr(mac_tools.requests, "get", fake_get)

    result = mac_tools.lookup_vendor("00:1A:11:22:33:44")

    assert result["ok"] is True
    assert result["vendor"] == "Google, Inc."
    assert captured["url"].endswith("001a11")
    assert captured["timeout"] == mac_tools.VENDOR_LOOKUP_TIMEOUT


def test_lookup_vendor_accepts_bare_oui(monkeypatch):
    monkeypatch.setattr(mac_tools.requests, "get", lambda url, timeout=None: FakeResponse(text="Raspberry Pi Foundation"))

    result = mac_tools.lookup_vendor("B8:27:EB")

    assert result["ok"] is True
    assert result["vendor"] == "Raspberry Pi Foundation"


def test_lookup_vendor_handles_not_found(monkeypatch):
    monkeypatch.setattr(mac_tools.requests, "get", lambda url, timeout=None: FakeResponse(status_code=404))

    result = mac_tools.lookup_vendor("00:00:00")

    assert result["ok"] is False
    assert "No registered vendor" in result["error"]


def test_lookup_vendor_handles_rate_limit(monkeypatch):
    monkeypatch.setattr(mac_tools.requests, "get", lambda url, timeout=None: FakeResponse(status_code=429))

    result = mac_tools.lookup_vendor("00:1A:11")

    assert result["ok"] is False
    assert "rate-limited" in result["error"]


def test_lookup_vendor_handles_network_error(monkeypatch):
    import requests

    def fake_get(url, timeout=None):
        raise requests.ConnectionError("boom")

    monkeypatch.setattr(mac_tools.requests, "get", fake_get)

    result = mac_tools.lookup_vendor("00:1A:11")

    assert result["ok"] is False
    assert "Vendor lookup failed" in result["error"]


def test_lookup_vendor_rejects_invalid_input():
    result = mac_tools.lookup_vendor("nope")

    assert result["ok"] is False
    assert "valid MAC address or OUI" in result["error"]
