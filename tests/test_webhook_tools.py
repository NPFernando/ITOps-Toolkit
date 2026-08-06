from utils import webhook_tools


class FakeResponse:
    def __init__(self, status_code=200, reason="OK", headers=None, text=""):
        self.status_code = status_code
        self.reason = reason
        self.headers = headers or {}
        self.text = text


def test_parse_headers_valid_lines():
    headers, error = webhook_tools.parse_headers("Content-Type: application/json\nX-Test: 1")

    assert error is None
    assert headers == {"Content-Type": "application/json", "X-Test": "1"}


def test_parse_headers_ignores_blank_lines():
    headers, error = webhook_tools.parse_headers("\nContent-Type: application/json\n\n")

    assert error is None
    assert headers == {"Content-Type": "application/json"}


def test_parse_headers_rejects_missing_colon():
    headers, error = webhook_tools.parse_headers("not-a-header-line")

    assert headers == {}
    assert "Line 1" in error


def test_send_request_success(monkeypatch):
    captured = {}

    def fake_request(method, url, headers=None, data=None, timeout=None, allow_redirects=None):
        captured.update(method=method, url=url, headers=headers, data=data)
        return FakeResponse(status_code=201, reason="Created", headers={"Content-Type": "application/json"}, text='{"ok": true}')

    monkeypatch.setattr(webhook_tools.requests, "request", fake_request)

    result = webhook_tools.send_request("example.com/api", "POST", "Content-Type: application/json", '{"a": 1}')

    assert result["ok"] is True
    assert result["status_code"] == 201
    assert result["response_body"] == '{"ok": true}'
    assert captured["method"] == "POST"
    assert captured["url"] == "https://example.com/api"
    assert captured["data"] == '{"a": 1}'
    assert captured["headers"]["Content-Type"] == "application/json"


def test_send_request_get_ignores_body(monkeypatch):
    captured = {}

    def fake_request(method, url, headers=None, data=None, timeout=None, allow_redirects=None):
        captured["data"] = data
        return FakeResponse()

    monkeypatch.setattr(webhook_tools.requests, "request", fake_request)

    webhook_tools.send_request("example.com", "GET", "", "should be ignored")

    assert captured["data"] is None


def test_send_request_rejects_invalid_method():
    result = webhook_tools.send_request("example.com", "TRACE")

    assert result["ok"] is False
    assert "Method must be one of" in result["error"]


def test_send_request_rejects_empty_url():
    result = webhook_tools.send_request("", "GET")

    assert result["ok"] is False
    assert "Enter a URL" in result["error"]


def test_send_request_rejects_bad_header_syntax():
    result = webhook_tools.send_request("example.com", "GET", "not-valid")

    assert result["ok"] is False
    assert "Line 1" in result["error"]


def test_send_request_handles_connection_error(monkeypatch):
    import requests

    def fake_request(method, url, headers=None, data=None, timeout=None, allow_redirects=None):
        raise requests.exceptions.ConnectionError("boom")

    monkeypatch.setattr(webhook_tools.requests, "request", fake_request)

    result = webhook_tools.send_request("example.com", "GET")

    assert result["ok"] is False
    assert "Connection failed" in result["error"]


def test_send_request_truncates_large_response_body(monkeypatch):
    big_body = "x" * (webhook_tools.MAX_RESPONSE_BODY_PREVIEW + 500)

    def fake_request(method, url, headers=None, data=None, timeout=None, allow_redirects=None):
        return FakeResponse(text=big_body)

    monkeypatch.setattr(webhook_tools.requests, "request", fake_request)

    result = webhook_tools.send_request("example.com", "GET")

    assert result["response_body_truncated"] is True
    assert len(result["response_body"]) == webhook_tools.MAX_RESPONSE_BODY_PREVIEW
