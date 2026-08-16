from __future__ import annotations

import streamlit as st

from utils.ip_geolocation import lookup_ip_geolocation
from utils.ui import apply_app_shell, display_rows_frame, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="IP Geolocation Lookup", layout="wide")
apply_app_shell(active_page="IP Geolocation Lookup")


render_page_header(
    "IP Geolocation Lookup",
    "Resolve an IP address to approximate geography, ASN, and ISP/org info.",
)

with tool_form_panel("ip_geolocation"):
    render_form_intro("Look up an IP", "Enter a public IPv4 or IPv6 address.")
    with st.form("ip-geolocation-form"):
        ip = st.text_input("IP address", placeholder="8.8.8.8")
        submitted = st.form_submit_button("Look up")

if submitted:
    st.session_state["ip_geolocation_result"] = lookup_ip_geolocation(ip)

result = st.session_state.get("ip_geolocation_result")

if result is None:
    render_empty_state("Ready to look up an IP", "Approximate location, ASN, and ISP/org info appear here after the lookup.")

if result is not None:
    with tool_result_panel("ip_geolocation_result_panel", related_to="ip_geolocation"):
        render_section_heading("Result", "Approximate location and network ownership.")
        if not result["ok"]:
            st.error(result["error"])
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Country", result["country"] or "Unknown")
            c2.metric("Region", result["region"] or "Unknown")
            c3.metric("City", result["city"] or "Unknown")

            rows = [
                {"field": "Postal code", "value": result["postal"] or "Unknown"},
                {"field": "Latitude", "value": result["latitude"]},
                {"field": "Longitude", "value": result["longitude"]},
                {"field": "Timezone", "value": result["timezone"] or "Unknown"},
                {"field": "ISP", "value": result["isp"] or "Unknown"},
                {"field": "Organization", "value": result["org"] or "Unknown"},
                {"field": "ASN", "value": result["asn"] or "Unknown"},
            ]
            st.dataframe(display_rows_frame(rows), width="stretch", hide_index=True)
