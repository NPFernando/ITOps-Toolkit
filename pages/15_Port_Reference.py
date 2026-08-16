from __future__ import annotations

import streamlit as st

from utils.port_reference import search_ports
from utils.ui import apply_app_shell, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Port Reference", layout="wide")
apply_app_shell(active_page="Port Reference")


render_page_header(
    "Port Reference",
    "Look up common network ports by number, protocol, service name, or description.",
)

with tool_form_panel("port_reference"):
    render_form_intro("Search ports", "Search by port number, protocol, service name, or keyword.")
    query = st.text_input("Search", placeholder="443, TCP, SSH, database...")

results = search_ports(query)
with tool_result_panel("port_reference_result", related_to="port_reference"):
    render_section_heading("Ports", f"{len(results)} matching port(s).")
    if results:
        st.table(
            [
                {"Port": entry.port, "Protocol": entry.protocol, "Service": entry.name, "Description": entry.description}
                for entry in results
            ]
        )
    else:
        st.info("No ports matched that search.")
