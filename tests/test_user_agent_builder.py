from __future__ import annotations

from utils.user_agent_builder import build_user_agent


def test_build_chrome_windows():
    result = build_user_agent("Windows 11", "Chrome", "128.0.0.0")

    assert result["ok"] is True
    assert "Windows NT 10.0" in result["output"]
    assert "Chrome/128.0.0.0" in result["output"]
    assert "Safari/537.36" in result["output"]


def test_build_safari_macos():
    result = build_user_agent("macOS (Sonoma)", "Safari", "17.0")

    assert result["ok"] is True
    assert "Macintosh" in result["output"]
    assert "Version/17.0" in result["output"]


def test_build_safari_ios_uses_mobile_token():
    result = build_user_agent("iOS 17", "Safari", "17.0")

    assert result["ok"] is True
    assert "Mobile/15E148" in result["output"]


def test_build_firefox_linux():
    result = build_user_agent("Ubuntu Linux", "Firefox", "130.0")

    assert result["ok"] is True
    assert "X11; Linux x86_64" in result["output"]
    assert "Firefox/130.0" in result["output"]


def test_build_edge_includes_edg_token():
    result = build_user_agent("Windows 11", "Edge", "128.0.0.0")

    assert result["ok"] is True
    assert "Edg/128.0.0.0" in result["output"]


def test_rejects_impossible_combo_safari_on_windows():
    result = build_user_agent("Windows 11", "Safari", "17.0")

    assert result["ok"] is False
    assert "never released" in result["error"]


def test_rejects_impossible_combo_chrome_on_ios():
    result = build_user_agent("iOS 17", "Chrome", "128.0.0.0")

    assert result["ok"] is False


def test_rejects_empty_version():
    result = build_user_agent("Windows 11", "Chrome", "")

    assert result["ok"] is False
    assert result["error"] == "Enter a version number."


def test_rejects_malformed_version():
    result = build_user_agent("Windows 11", "Chrome", "not-a-version")

    assert result["ok"] is False
    assert "dotted number" in result["error"]


def test_rejects_unknown_os():
    result = build_user_agent("BogusOS", "Chrome", "128.0.0.0")

    assert result["ok"] is False
    assert "Unknown OS" in result["error"]


def test_rejects_unknown_browser():
    result = build_user_agent("Windows 11", "BogusBrowser", "128.0.0.0")

    assert result["ok"] is False
    assert "Unknown browser" in result["error"]
