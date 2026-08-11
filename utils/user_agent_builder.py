"""Build a realistic browser User-Agent string from OS/browser/version choices.

Reverse of User Agent Parser (which decomposes an existing UA string, not
builds one) -- useful for testing how a site responds to a specific browser
without switching devices.
"""

from __future__ import annotations

from typing import Any

OS_OPTIONS = ("Windows 11", "macOS (Sonoma)", "Ubuntu Linux", "Android 14", "iOS 17")
BROWSER_OPTIONS = ("Chrome", "Firefox", "Safari", "Edge")

_OS_TOKENS = {
    "Windows 11": "Windows NT 10.0; Win64; x64",
    "macOS (Sonoma)": "Macintosh; Intel Mac OS X 10_15_7",
    "Ubuntu Linux": "X11; Linux x86_64",
    "Android 14": "Linux; Android 14; Pixel 8",
    "iOS 17": "iPhone; CPU iPhone OS 17_0 like Mac OS X",
}

# (os, browser) combinations that don't exist in the real world -- Safari is
# WebKit-only and never shipped for Windows/Linux/Android; Edge and Chrome
# are desktop/Android builds, not iOS (Apple requires WebKit there).
_UNSUPPORTED_COMBOS = {
    ("Windows 11", "Safari"),
    ("Ubuntu Linux", "Safari"),
    ("Android 14", "Safari"),
    ("iOS 17", "Chrome"),
    ("iOS 17", "Firefox"),
    ("iOS 17", "Edge"),
}


def build_user_agent(os_name: str, browser: str, version: str) -> dict[str, Any]:
    """Build a User-Agent string for the given OS, browser, and version."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    if os_name not in OS_OPTIONS:
        result["error"] = f"Unknown OS: {os_name}."
        return result
    if browser not in BROWSER_OPTIONS:
        result["error"] = f"Unknown browser: {browser}."
        return result
    if (os_name, browser) in _UNSUPPORTED_COMBOS:
        result["error"] = f"{browser} was never released for {os_name}."
        return result

    version = (version or "").strip()
    if not version:
        result["error"] = "Enter a version number."
        return result
    if not all(part.isdigit() for part in version.split(".")):
        result["error"] = "Version must look like a dotted number, e.g. 128.0.0.0."
        return result

    platform = _OS_TOKENS[os_name]
    major = version.split(".")[0]

    if browser == "Chrome":
        ua = f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
    elif browser == "Edge":
        ua = f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36 Edg/{version}"
    elif browser == "Firefox":
        ua = f"Mozilla/5.0 ({platform}; rv:{version}) Gecko/20100101 Firefox/{version}"
    else:  # Safari
        webkit = "605.1.15"
        if os_name == "iOS 17":
            ua = f"Mozilla/5.0 ({platform}) AppleWebKit/{webkit} (KHTML, like Gecko) Version/{version} Mobile/15E148 Safari/{webkit}"
        else:
            ua = f"Mozilla/5.0 ({platform}) AppleWebKit/{webkit} (KHTML, like Gecko) Version/{version} Safari/{webkit}"

    result.update({"ok": True, "output": ua, "major_version": major})
    return result
