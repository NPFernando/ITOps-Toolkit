from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.qr_tools import WIFI_SECURITY_TYPES, build_wifi_payload, generate_qr_code
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


_baseline = start_page_baseline("WiFi QR Code Generator")
st.set_page_config(page_title="WiFi QR Code Generator", layout="wide")
apply_app_shell(active_page="WiFi QR Code Generator")
mark_page_baseline(_baseline, "shell-ready")

render_page_header(
    "WiFi QR Code Generator",
    "Generate a QR code that lets phones join a WiFi network without manual password entry.",
    warning="The QR payload includes the WiFi password in plain text for scanners.",
)

with tool_form_panel("wifi_qr_generator"):
    render_form_intro("Enter WiFi settings", "Grouped controls keep network setup readable on small screens.")
    with st.form("wifi-qr-code-form"):
        st.markdown('<div class="tool-panel-eyebrow">Network identity</div>', unsafe_allow_html=True)
        ssid = st.text_input("Network name (SSID)")
        st.markdown('<div class="tool-panel-eyebrow">Security and password</div>', unsafe_allow_html=True)
        security = st.selectbox("Security type", WIFI_SECURITY_TYPES)
        password = st.text_input("Password", type="password", disabled=security == "nopass")
        hidden = st.checkbox("Hidden network")
        submitted = st.form_submit_button("Generate WiFi QR code", use_container_width=True)

if submitted:
    payload_result = build_wifi_payload(ssid, password, security, hidden)
    if payload_result["ok"]:
        st.session_state["wifi_qr_result"] = generate_qr_code(payload_result["payload"])
    else:
        st.session_state["wifi_qr_result"] = payload_result

result = st.session_state.get("wifi_qr_result")
if result is None:
    render_empty_state("Ready to generate", "A WiFi QR image appears here after submission.")
    render_status_note(
        "Awaiting WiFi details",
        "Enter SSID, security settings, and password (when required), then select Generate WiFi QR code.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("wifi_qr_result_panel", related_to="wifi_qr_generator"):
        render_section_heading("WiFi QR output", eyebrow="Result")
        if not result["ok"]:
            render_status_note("Outcome: WiFi input validation required", str(result["error"]), tone="warning")
        else:
            render_status_note("Outcome: WiFi QR generated", "Scan this code from a phone camera to join the network.", tone="success")
            st.image(result["png_bytes"], width=280)
            st.download_button("Download PNG", result["png_bytes"], file_name="wifi-qr-code.png", mime="image/png")

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
