from __future__ import annotations

import streamlit as st

from utils.mac_tools import analyze_mac
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="MAC Address Tool", layout="wide")
apply_app_shell(active_page="MAC Address Tool")


render_page_header(
    "MAC Address Tool",
    "Validate a MAC address and view it in colon, hyphen, dot, and bare formats, plus address-class bits.",
)

with tool_form_panel("mac_tool"):
    render_form_intro("Enter a MAC address", "Accepts colon, hyphen, dot, or bare separators.")
    with st.form("mac-form"):
        mac_input = st.text_input("MAC address", placeholder="00:1A:2B:3C:4D:5E")
        submitted = st.form_submit_button("Analyze")

if not submitted:
    render_empty_state("Ready to analyze a MAC address", "Formatted addresses and address-class bits appear here.")

if submitted:
    result = analyze_mac(mac_input)
    with tool_result_panel("mac_result", related_to="mac_address_tool"):
        render_section_heading("MAC address details", "Canonical formats and address-class bits.")
        if not result["ok"]:
            st.error(result["error"])
        else:
            c1, c2 = st.columns(2)
            c1.metric("Unicast / Multicast", "Multicast" if result["is_multicast"] else "Unicast")
            c2.metric("Universal / Local", "Locally administered" if result["is_local"] else "Universally administered")

            rows = [
                {"Format": "Colon", "Value": result["colon"]},
                {"Format": "Hyphen", "Value": result["hyphen"]},
                {"Format": "Dot", "Value": result["dot"]},
                {"Format": "Bare", "Value": result["bare"]},
                {"Format": "OUI (vendor)", "Value": result["oui"]},
                {"Format": "NIC (device)", "Value": result["nic"]},
            ]
            st.table(rows)
