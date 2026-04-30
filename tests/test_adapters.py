from datetime import UTC, datetime
import socket
import ssl

import dns.exception
import requests

from utils import dns_tools, http_tools, ssl_tools


class FakeARecord:
    address = "203.0.113.10"


class FakeTxtRecord:
    def __init__(self, value: str):
        self.strings = [value.encode("utf-8")]


class FakeResolver:
    def __init__(self, answers=None, error=None):
        self.answers = answers or []
        self.error = error

    def resolve(self, query_name, query_type):
        if self.error:
            raise self.error
        return self.answers


def test_normalize_domain_handles_urls_ports_paths_and_idna():
    assert dns_tools.normalize_domain(" HTTPS://WWW.Example.COM:443/path?x=1 ") == "www.example.com"
    assert dns_tools.normalize_domain("bücher.example.") == "xn--bcher-kva.example"
    assert dns_tools.normalize_domain("user@example.com") == "example.com"


def test_resolve_records_uses_fake_resolver_for_a_records(monkeypatch):
    monkeypatch.setattr(dns_tools, "_get_resolver", lambda: FakeResolver([FakeARecord()]))

    result = dns_tools.resolve_records("Example.com", "A")

    assert result["ok"] is True
    assert result["domain"] == "example.com"
    assert result["status"] == "Healthy"
    assert result["records"] == [{"type": "A", "value": "203.0.113.10"}]
    assert result["raw_values"] == ["203.0.113.10"]


def test_resolve_records_filters_spf_and_handles_timeouts(monkeypatch):
    monkeypatch.setattr(
        dns_tools,
        "_get_resolver",
        lambda: FakeResolver([FakeTxtRecord("not-spf"), FakeTxtRecord("v=spf1 include:_spf.example.com")]),
    )
    spf = dns_tools.resolve_records("example.com", "SPF")

    monkeypatch.setattr(dns_tools, "_get_resolver", lambda: FakeResolver(error=dns.exception.Timeout()))
    timeout = dns_tools.resolve_records("example.com", "A")

    assert spf["ok"] is True
    assert spf["query_name"] == "example.com"
    assert spf["raw_values"] == ["v=spf1 include:_spf.example.com"]
    assert timeout["ok"] is False
    assert timeout["status"] == "Timeout"
    assert timeout["error"] == "DNS lookup timed out."


def test_get_dns_summary_uses_mocked_results(monkeypatch):
    def fake_resolve(domain, record_type):
        records = [{"value": "present"}] if record_type in {"A", "MX", "SPF", "DMARC"} else []
        return {"domain": domain, "records": records, "status": "Healthy" if records else "No Answer"}

    monkeypatch.setattr(dns_tools, "resolve_records", fake_resolve)

    summary = dns_tools.get_dns_summary("example.com")

    assert summary["status"] == "Healthy"
    assert summary["email_status"] == "Healthy"
    assert summary["a_found"] is True
    assert summary["dmarc_found"] is True


class FakeHistoryResponse:
    status_code = 301
    url = "http://example.com"
    headers = {"location": "https://example.com"}


class FakeResponse:
    status_code = 200
    reason = "OK"
    url = "https://example.com"
    headers = {
        "strict-transport-security": "max-age=31536000",
        "x-frame-options": "DENY",
        "content-security-policy": "default-src 'self'",
    }
    history = [FakeHistoryResponse()]

    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_check_http_status_success_uses_fake_response(monkeypatch):
    captured = {}

    def fake_get(url, headers, timeout, allow_redirects, stream):
        captured.update(
            {
                "url": url,
                "headers": headers,
                "timeout": timeout,
                "allow_redirects": allow_redirects,
                "stream": stream,
            }
        )
        return FakeResponse()

    monkeypatch.setattr(http_tools.requests, "get", fake_get)

    result = http_tools.check_http_status("example.com", timeout=7)

    assert captured["url"] == "https://example.com"
    assert captured["headers"]["User-Agent"] == "ITOpsToolkit/1.0 public-safe-checker"
    assert captured["timeout"] == 7
    assert captured["allow_redirects"] is True
    assert captured["stream"] is True
    assert result["ok"] is True
    assert result["uses_https"] is True
    assert result["redirect_chain"] == [
        {"status_code": 301, "url": "http://example.com", "location": "https://example.com"}
    ]
    assert result["recommendations"] == []


def test_check_http_status_validation_and_timeout(monkeypatch):
    assert http_tools.check_http_status("")["error"] == "Enter a URL or domain."
    assert http_tools.check_http_status("ftp://example.com")["error"] == "Enter a valid HTTP or HTTPS URL."

    def fake_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout()

    monkeypatch.setattr(http_tools.requests, "get", fake_timeout)

    result = http_tools.check_http_status("https://example.com")

    assert result["ok"] is False
    assert result["error"] == "HTTP request timed out."
    assert result["recommendations"] == ["Check network reachability and application response time."]


class FakeSocket:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeTlsSocket:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def getpeercert(self):
        return {
            "subject": ((("commonName", "example.com"),),),
            "issuer": ((("commonName", "Example CA"),),),
            "subjectAltName": (("DNS", "example.com"), ("DNS", "www.example.com")),
            "notBefore": "Apr 30 00:00:00 2025 GMT",
            "notAfter": "Apr 30 00:00:00 2030 GMT",
        }


class FakeContext:
    def wrap_socket(self, sock, server_hostname):
        assert server_hostname == "example.com"
        return FakeTlsSocket()


def test_get_certificate_info_success_with_fake_socket(monkeypatch):
    monkeypatch.setattr(ssl_tools.ssl, "create_default_context", lambda: FakeContext())
    monkeypatch.setattr(ssl_tools.socket, "create_connection", lambda address, timeout: FakeSocket())

    result = ssl_tools.get_certificate_info("example.com")

    assert result["ok"] is True
    assert result["tls_status"] == "Healthy"
    assert result["verification_ok"] is True
    assert result["subject"]["commonName"] == "example.com"
    assert result["issuer"]["commonName"] == "Example CA"
    assert result["san_names"] == ["example.com", "www.example.com"]
    assert result["valid_until"] == datetime(2030, 4, 30, tzinfo=UTC)


def test_get_certificate_info_validation_and_timeout(monkeypatch):
    assert ssl_tools.get_certificate_info("", 443)["error"] == "Enter a domain name."
    assert ssl_tools.get_certificate_info("example.com", 70000)["error"] == "Port must be between 1 and 65535."

    def fake_timeout(*args, **kwargs):
        raise socket.timeout()

    monkeypatch.setattr(ssl_tools.socket, "create_connection", fake_timeout)

    result = ssl_tools.get_certificate_info("example.com")

    assert result["ok"] is False
    assert result["tls_status"] == "Unknown"
    assert result["error"] == "TLS connection timed out."


def test_get_certificate_info_ssl_error(monkeypatch):
    class BadContext:
        def wrap_socket(self, sock, server_hostname):
            raise ssl.SSLError("handshake failed")

    monkeypatch.setattr(ssl_tools.ssl, "create_default_context", lambda: BadContext())
    monkeypatch.setattr(ssl_tools.socket, "create_connection", lambda address, timeout: FakeSocket())

    result = ssl_tools.get_certificate_info("example.com")

    assert result["ok"] is False
    assert result["tls_status"] == "Critical"
    assert result["error"] == "TLS connection failed: ('handshake failed',)"
