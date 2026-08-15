from __future__ import annotations

import streamlit as st

from utils.network_calc import calculate_subnet
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_failure_note,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Subnet Calculator", layout="wide")
apply_app_shell(active_page="Subnet Calculator")


render_page_header(
    "Subnet Calculator",
    "Calculate IPv4/IPv6 network, broadcast, host range, and usable host counts from a CIDR block.",
)

with tool_form_panel("subnet_calculator"):
    render_form_intro("Enter a CIDR block", "Accepts a bare IP (treated as /32 or /128) or a full CIDR block.")
    with st.form("subnet-form"):
        cidr_input = st.text_input(
            "IP address or CIDR",
            placeholder="192.168.1.0/24",
            help="Enter an IPv4/IPv6 address or CIDR block.",
        )
        submitted = st.form_submit_button("Calculate subnet")

if submitted:
    # Stored in session_state (not rendered directly here) because the sidebar's
    # quick-search box, favorite-star buttons, and any other widget outside this
    # page's st.form trigger reruns of their own -- on those reruns `submitted` is
    # False again, which would otherwise collapse this whole results section the
    # instant any of them is touched.
    st.session_state["subnet_calculator_result"] = calculate_subnet(cidr_input)

result = st.session_state.get("subnet_calculator_result")

if result is None:
    render_empty_state("Ready to calculate a subnet", "Network details appear here after you calculate a CIDR block.")

if result is not None:
    with tool_result_panel("subnet_result", related_to="subnet_calculator"):
        render_section_heading("Subnet details", "Computed from the entered address or CIDR block.")
        if not result["ok"]:
            render_failure_note(
                "Subnet calculation",
                result["error"],
                remediation="Enter a valid IPv4 or IPv6 address/CIDR block and calculate again.",
            )
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("IP version", f"v{result['version']}")
            c2.metric("Prefix length", f"/{result['prefix_length']}")
            c3.metric("Total addresses", f"{result['total_addresses']:,}")
            c4.metric("Usable hosts", f"{result['usable_hosts']:,}")

            rows = [
                {"Field": "Network address", "Value": result["network"]},
                {"Field": "Netmask", "Value": result["netmask"]},
                {"Field": "First host", "Value": result["first_host"]},
                {"Field": "Last host", "Value": result["last_host"]},
                {"Field": "Private range", "Value": "Yes" if result["is_private"] else "No"},
            ]
            if result["version"] == 4:
                rows.insert(2, {"Field": "Wildcard mask", "Value": result["wildcard_mask"]})
                rows.insert(3, {"Field": "Broadcast address", "Value": result["broadcast"]})
            st.caption("Subnet result fields")
            st.table(rows)
