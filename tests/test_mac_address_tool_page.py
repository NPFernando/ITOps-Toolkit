from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import mac_tools


# Newer streamlit resolves AppTest.from_file()'s relative paths against the
# file that calls it (this test file's directory), not the working
# directory -- an absolute path avoids that resolution entirely.
MAC_PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "13_MAC_Address_Tool.py")
SAMPLE_MAC = "00:1A:2B:3C:4D:5E"


def _run_mac_page() -> AppTest:
    app = AppTest.from_file(MAC_PAGE, default_timeout=30)
    app.run()
    assert not app.exception
    return app


def _submit_mac(app: AppTest, mac: str = SAMPLE_MAC) -> AppTest:
    app.text_input[0].set_value(mac)
    app.button[0].click()
    app.run()
    assert not app.exception
    return app


def _page_text(app: AppTest) -> str:
    parts: list[str] = []
    for collection_name in ("markdown", "success", "warning", "error"):
        for item in getattr(app, collection_name, []):
            parts.append(str(getattr(item, "value", getattr(item, "body", ""))))
    return "\n".join(parts)


def test_mac_page_clicking_look_up_vendor_does_not_hide_results(monkeypatch):
    """Regression: "Look up vendor" renders outside `st.form`, so clicking it triggers a
    rerun in which the form's transient `submitted` value is False again. Results must be
    keyed off session_state, not `submitted`, or the whole results section (button
    included) disappears the instant it's clicked."""
    monkeypatch.setattr(mac_tools, "lookup_vendor", lambda oui: {"ok": True, "error": None, "vendor": "Fake Vendor Inc."})

    app = _submit_mac(_run_mac_page())
    lookup_buttons = [b for b in app.button if b.key == "mac_vendor_lookup_button"]
    assert lookup_buttons

    lookup_buttons[0].click()
    app.run()
    assert not app.exception

    text = _page_text(app)
    assert "Ready to analyze a MAC address" not in text
    assert "Fake Vendor Inc." in text
    still_present = [b for b in app.button if b.key == "mac_vendor_lookup_button"]
    assert still_present


def test_mac_page_vendor_result_does_not_leak_across_different_submissions(monkeypatch):
    """Regression: a stale vendor lookup from a previous MAC must not linger and display
    against a newly submitted, different MAC address."""
    monkeypatch.setattr(mac_tools, "lookup_vendor", lambda oui: {"ok": True, "error": None, "vendor": "Fake Vendor Inc."})

    app = _submit_mac(_run_mac_page())
    lookup_buttons = [b for b in app.button if b.key == "mac_vendor_lookup_button"]
    lookup_buttons[0].click()
    app.run()
    assert "Fake Vendor Inc." in _page_text(app)

    app = _submit_mac(app, "AA:BB:CC:DD:EE:FF")
    text = _page_text(app)
    assert "Fake Vendor Inc." not in text
