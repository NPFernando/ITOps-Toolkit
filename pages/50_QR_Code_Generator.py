from __future__ import annotations

import streamlit as st

from utils.qr_tools import MAX_TEXT_LENGTH, WIFI_SECURITY_TYPES, build_wifi_payload, generate_qr_code
from utils.ui import apply_app_shell, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


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
        result = generate_qr_code(text_value)
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.image(result["png_bytes"], width=280)
            st.download_button("Download PNG", result["png_bytes"], file_name="qr-code.png", mime="image/png")

with wifi_tab:
    with tool_form_panel("qr_wifi"):
        render_form_intro("Wi-Fi credentials", "Most phone cameras can join a network directly from a scanned QR code.")
        col_ssid, col_security = st.columns(2)
        ssid = col_ssid.text_input("Network name (SSID)")
        security = col_security.selectbox("Security", WIFI_SECURITY_TYPES)
        password = st.text_input("Password", type="password", disabled=security == "nopass")
        hidden = st.checkbox("Hidden network")
    with tool_result_panel("qr_wifi_result", related_to="qr_code_generator"):
        render_section_heading("QR code", "Scan to join the Wi-Fi network directly.")
        wifi_result = build_wifi_payload(ssid, password, security, hidden)
        if not wifi_result["ok"]:
            st.error(wifi_result["error"])
        else:
            qr_result = generate_qr_code(wifi_result["payload"])
            if not qr_result["ok"]:
                st.error(qr_result["error"])
            else:
                st.image(qr_result["png_bytes"], width=280)
                st.download_button("Download PNG", qr_result["png_bytes"], file_name="wifi-qr-code.png", mime="image/png", key="qr_wifi_download")
