from utils import whois_tools


class FakeResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self.ok = 200 <= status_code < 300
        self._json_data = json_data

    def json(self):
        if self._json_data is None:
            raise ValueError("no json")
        return self._json_data


GOOGLE_RDAP = {
    "ldhName": "GOOGLE.COM",
    "status": ["client transfer prohibited"],
    "entities": [
        {
            "roles": ["registrar"],
            "vcardArray": ["vcard", [["version", {}, "text", "4.0"], ["fn", {}, "text", "MarkMonitor Inc."]]],
        }
    ],
    "events": [
        {"eventAction": "registration", "eventDate": "1997-09-15T04:00:00Z"},
        {"eventAction": "expiration", "eventDate": "2028-09-14T04:00:00Z"},
    ],
    "nameservers": [{"ldhName": "NS2.GOOGLE.COM"}, {"ldhName": "NS1.GOOGLE.COM"}],
}


def test_lookup_whois_parses_registrar_events_and_nameservers(monkeypatch):
    monkeypatch.setattr(whois_tools.requests, "get", lambda url, headers=None, timeout=None: FakeResponse(json_data=GOOGLE_RDAP))

    result = whois_tools.lookup_whois("google.com")

    assert result["ok"] is True
    assert result["registrar"] == "MarkMonitor Inc."
    assert result["status"] == ["client transfer prohibited"]
    assert result["nameservers"] == ["NS1.GOOGLE.COM", "NS2.GOOGLE.COM"]
    assert result["events"][0] == {"label": "Registered", "date": "1997-09-15T04:00:00Z"}
    assert result["events"][1] == {"label": "Expires", "date": "2028-09-14T04:00:00Z"}


def test_lookup_whois_handles_not_found(monkeypatch):
    monkeypatch.setattr(whois_tools.requests, "get", lambda url, headers=None, timeout=None: FakeResponse(status_code=404))

    result = whois_tools.lookup_whois("thisdomaindoesnotexist12345.com")

    assert result["ok"] is False
    assert "No registration record" in result["error"]


def test_lookup_whois_handles_server_error(monkeypatch):
    monkeypatch.setattr(whois_tools.requests, "get", lambda url, headers=None, timeout=None: FakeResponse(status_code=503))

    result = whois_tools.lookup_whois("example.com")

    assert result["ok"] is False
    assert "status 503" in result["error"]


def test_lookup_whois_handles_network_error(monkeypatch):
    import requests

    def fake_get(url, headers=None, timeout=None):
        raise requests.ConnectionError("boom")

    monkeypatch.setattr(whois_tools.requests, "get", fake_get)

    result = whois_tools.lookup_whois("example.com")

    assert result["ok"] is False
    assert "lookup failed" in result["error"]


def test_lookup_whois_rejects_invalid_input():
    assert "Enter a domain" in whois_tools.lookup_whois("")["error"]


def test_lookup_whois_rejects_missing_dot():
    result = whois_tools.lookup_whois("localhost")

    assert result["ok"] is False
    assert "valid domain" in result["error"]


def test_lookup_whois_rejects_overlong_domain():
    result = whois_tools.lookup_whois("a" * 300 + ".com")

    assert result["ok"] is False
    assert "longer than" in result["error"]
