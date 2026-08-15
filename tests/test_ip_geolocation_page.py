from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import ip_geolocation


IP_GEO_PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "42_IP_Geolocation_Lookup.py")


def test_ip_geolocation_page_zero_coordinates_do_not_render_as_unknown(monkeypatch):
    """Regression: Latitude/Longitude used to render a bare Python value with
    no fallback, unlike every other field on this page (which fall back to
    "Unknown" via `x or "Unknown"`). Applying that same `or "Unknown"` pattern
    to these two fields would have been a *new* bug -- a real coordinate of
    exactly 0.0 (equator/prime meridian) is falsy in Python and would
    incorrectly render as "Unknown" too. Confirm 0.0 renders as 0.0/0 and a
    genuinely missing coordinate (None) renders as "Unknown"."""

    def fake_lookup(ip):
        return {
            "ok": True,
            "country": "Testland",
            "region": "Test Region",
            "city": "Test City",
            "postal": "00000",
            "latitude": 0.0,
            "longitude": None,
            "timezone": "UTC",
            "isp": "Test ISP",
            "org": "Test Org",
            "asn": "AS0",
            "error": None,
        }

    monkeypatch.setattr(ip_geolocation, "lookup_ip_geolocation", fake_lookup)

    app = AppTest.from_file(IP_GEO_PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("8.8.8.8")
    app.button[0].click().run()
    assert not app.exception

    frame = app.dataframe[0].value
    rows = dict(zip(frame["field"], frame["value"], strict=True))
    assert rows["Latitude"] == "0.0"
    assert rows["Longitude"] == "Unknown"


def test_ip_geolocation_page_error_uses_warning_status_semantics(monkeypatch):
    def fake_lookup(ip):
        return {
            "ok": False,
            "error": "request timed out",
        }

    monkeypatch.setattr(ip_geolocation, "lookup_ip_geolocation", fake_lookup)

    app = AppTest.from_file(IP_GEO_PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("8.8.8.8")
    app.button[0].click().run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "IP geolocation lookup temporarily unavailable" in markdown
    assert "tool-status-note-warning" in markdown
