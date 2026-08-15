from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGES_DIR = Path(__file__).resolve().parent.parent / "pages"


def _run(page_name: str) -> AppTest:
    app = AppTest.from_file(str(PAGES_DIR / page_name), default_timeout=30)
    app.run()
    assert not app.exception
    return app


def _markdown(app: AppTest) -> str:
    return " ".join(item.value for item in app.markdown)


def test_wave22_pages_show_neutral_status_before_submit():
    pages = (
        "129_Docker_Run_to_Compose.py",
        "130_NATO_Phonetic_Converter.py",
        "131_WiFi_QR_Code_Generator.py",
        "132_HMAC_Generator.py",
        "133_IPv6_ULA_Generator.py",
        "134_Random_MAC_Address_Generator.py",
    )

    for page_name in pages:
        app = _run(page_name)
        md = _markdown(app)
        assert "tool-empty-state" in md
        assert "tool-status-note-neutral" in md
        assert 'role="status"' in md
        assert 'aria-live="polite"' in md


def test_docker_page_uses_warning_and_success_states():
    app = _run("129_Docker_Run_to_Compose.py")

    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-warning" in md
    assert "Outcome: command validation required" in md
    assert 'role="alert"' in md

    app.text_area[0].set_value("docker run -p 8080:80 nginx:latest")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: compose YAML generated" in md
    code = " ".join(item.value for item in app.code)
    assert "services:" in code
    assert "nginx:latest" in code


def test_nato_page_uses_warning_and_success_states():
    app = _run("130_NATO_Phonetic_Converter.py")

    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-warning" in md
    assert "Outcome: input required" in md
    assert 'role="alert"' in md

    app.text_area[0].set_value("AB")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: conversion complete" in md
    output = " ".join(item.value for item in app.code)
    assert "Alpha Bravo" in output


def test_wifi_page_uses_warning_and_success_states():
    app = _run("131_WiFi_QR_Code_Generator.py")

    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-warning" in md
    assert "Outcome: WiFi input validation required" in md
    assert 'role="alert"' in md

    app.text_input[0].set_value("OfficeWiFi")
    app.text_input[1].set_value("hunter22")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: WiFi QR generated" in md
    assert len(app.image) > 0


def test_hmac_page_uses_warning_and_success_states():
    app = _run("132_HMAC_Generator.py")

    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-warning" in md
    assert "Outcome: HMAC input validation required" in md
    assert 'role="alert"' in md

    app.text_area[0].set_value("payload")
    app.text_input[0].set_value("secret")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: HMAC digest generated" in md
    digest = " ".join(item.value for item in app.code)
    assert len(digest) >= 32


def test_ipv6_page_rejects_invalid_seed_and_returns_seeded_result():
    app = _run("133_IPv6_ULA_Generator.py")

    app.text_input[0].set_value("not-a-number")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-warning" in md
    assert "Outcome: ULA input validation required" in md
    assert 'role="alert"' in md

    app.text_input[0].set_value("42")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: ULA prefix generated" in md
    code = " ".join(item.value for item in app.code)
    assert "fd" in code
    assert "::/48" in code


def test_mac_page_rejects_invalid_seed_and_returns_seeded_result():
    app = _run("134_Random_MAC_Address_Generator.py")

    app.text_input[0].set_value("not-a-number")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-warning" in md
    assert "Outcome: MAC input validation required" in md
    assert 'role="alert"' in md

    app.text_input[0].set_value("42")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: MAC address generated" in md
    code = " ".join(item.value for item in app.code)
    assert code.count(":") == 5
