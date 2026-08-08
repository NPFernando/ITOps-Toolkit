from __future__ import annotations

import socket

from utils import tls_scanner


def test_scan_tls_rejects_empty_host():
    result = tls_scanner.scan_tls("")

    assert result["ok"] is False
    assert result["error"] == "Enter a host name."


def test_scan_tls_rejects_out_of_range_port():
    result = tls_scanner.scan_tls("example.com", port=99999)

    assert result["ok"] is False
    assert "Port must be between" in result["error"]


def test_scan_tls_rejects_overlong_host():
    result = tls_scanner.scan_tls("a" * 300)

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_legacy_protocols_report_not_testable_without_network():
    """This environment's OpenSSL build has SSLv3/TLSv1.0/TLSv1.1 compiled
    out entirely -- verified by direct execution. _is_locally_testable must
    catch this before any socket is opened, so this assertion holds with no
    network access and no mocking."""
    for name, version in tls_scanner._PROTOCOL_VERSIONS:
        if name in {"SSLv3", "TLSv1.0", "TLSv1.1"}:
            context = tls_scanner._build_context(version)
            assert tls_scanner._is_locally_testable(context, "example.com") is False


def test_modern_protocols_are_locally_testable():
    for name, version in tls_scanner._PROTOCOL_VERSIONS:
        if name in {"TLSv1.2", "TLSv1.3"}:
            context = tls_scanner._build_context(version)
            assert tls_scanner._is_locally_testable(context, "example.com") is True


def test_probe_version_reports_not_testable_for_ssl3():
    result = tls_scanner._probe_version("SSLv3", tls_scanner.ssl.TLSVersion.SSLv3, "example.com", 443, 5)

    assert result["status"] == "not_testable"
    assert "Not testable in this environment" in result["detail"]


def test_probe_version_reports_connection_error_on_unreachable_host(monkeypatch):
    def _raise_os_error(*args, **kwargs):
        raise OSError("no route to host")

    monkeypatch.setattr(tls_scanner.socket, "create_connection", _raise_os_error)

    result = tls_scanner._probe_version("TLSv1.2", tls_scanner.ssl.TLSVersion.TLSv1_2, "example.com", 443, 5)

    assert result["status"] == "connection_error"
    assert "Could not connect" in result["detail"]


def test_probe_version_reports_connection_error_on_timeout(monkeypatch):
    def _raise_timeout(*args, **kwargs):
        raise socket.timeout()

    monkeypatch.setattr(tls_scanner.socket, "create_connection", _raise_timeout)

    result = tls_scanner._probe_version("TLSv1.2", tls_scanner.ssl.TLSVersion.TLSv1_2, "example.com", 443, 5)

    assert result["status"] == "connection_error"
    assert "timed out" in result["detail"]


def test_scan_tls_returns_one_result_per_protocol_version(monkeypatch):
    def _raise_os_error(*args, **kwargs):
        raise OSError("simulated -- no real network in this test")

    monkeypatch.setattr(tls_scanner.socket, "create_connection", _raise_os_error)

    result = tls_scanner.scan_tls("example.com")

    assert result["ok"] is True
    assert len(result["results"]) == 5
    statuses = {row["status"] for row in result["results"]}
    assert statuses == {"not_testable", "connection_error"}
