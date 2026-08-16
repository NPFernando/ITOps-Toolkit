from __future__ import annotations

import streamlit as st

from utils.qr_tools import MAX_TEXT_LENGTH, WIFI_SECURITY_TYPES, build_wifi_payload, generate_qr_code
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_failure_note,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="QR Code Generator", layout="wide")
apply_app_shell(active_page="QR Code Generator")


render_page_header(
    "QR Code Generator",
    "Generate a QR code for a URL, plain text, or Wi-Fi credentials.",
)

text_tab, wifi_tab = st.tabs(["Text / URL", "Wi-Fi"])

with text_tab:
    with tool_form_panel("qr_text"):
        render_form_intro("Text or URL", "Enter a URL or any text -- updates live as you type.")
        text_value = st.text_input("Text or URL", max_chars=MAX_TEXT_LENGTH, placeholder="https://example.com")
    with tool_result_panel("qr_text_result", related_to="qr_code_generator"):
        render_section_heading("QR code", "Scan with a phone camera to open the link or read the text.")
        if not text_value.strip():
            render_empty_state("Ready for input", "A QR code appears here as soon as you type.")
        else:
            result = generate_qr_code(text_value)
            if not result["ok"]:
                render_failure_note("Text input", result["error"], remediation="Provide text or a URL up to the allowed length.")
            else:
                render_status_note("QR code generated", "QR image generated from the provided text/URL.", tone="success")
                st.image(result["png_bytes"], width=280)
                st.download_button("Download PNG", result["png_bytes"], file_name="qr-code.png", mime="image/png")

with wifi_tab:
    render_status_note(
        "Password embedded in the QR image",
        "The generated code contains your Wi-Fi password in plain text -- anyone who scans it can read it. "
        "Be careful where you display, save, or share the resulting image.",
        tone="warning",
    )
    with tool_form_panel("qr_wifi"):
        render_form_intro("Wi-Fi credentials", "Most phone cameras can join a network directly from a scanned QR code.")
        col_ssid, col_security = st.columns(2)
        ssid = col_ssid.text_input("Network name (SSID)")
        security = col_security.selectbox("Security", WIFI_SECURITY_TYPES)
        password = st.text_input("Password", type="password", disabled=security == "nopass")
        hidden = st.checkbox("Hidden network")
    with tool_result_panel("qr_wifi_result", related_to="qr_code_generator"):
        render_section_heading("QR code", "Scan to join the Wi-Fi network directly.")
        if not ssid.strip():
            render_empty_state("Ready for input", "A QR code appears here once you enter a network name.")
        else:
            wifi_result = build_wifi_payload(ssid, password, security, hidden)
            if not wifi_result["ok"]:
                render_failure_note("Wi-Fi input", wifi_result["error"], remediation="Check SSID/security/password fields and retry.")
            else:
                qr_result = generate_qr_code(wifi_result["payload"])
                if not qr_result["ok"]:
                    render_failure_note("QR generation", qr_result["error"], remediation="Adjust the input length and try again.")
                else:
                    render_status_note("Wi-Fi QR generated", "QR image generated from the provided Wi-Fi credentials.", tone="success")
                    st.image(qr_result["png_bytes"], width=280)
                    st.download_button("Download PNG", qr_result["png_bytes"], file_name="wifi-qr-code.png", mime="image/png", key="qr_wifi_download")
