from __future__ import annotations

import streamlit as st

from utils.cidr_aggregator import MAX_INPUT_LENGTH, aggregate_cidrs
from utils.ui import (
    apply_app_shell,
    display_rows_frame,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="CIDR Aggregator", layout="wide")
apply_app_shell(active_page="CIDR Aggregator")


render_page_header(
    "CIDR Aggregator",
    "Summarize a list of IPs or CIDR blocks into the minimal set of covering supernets.",
)

with tool_form_panel("cidr_aggregator"):
    render_form_intro("Enter addresses", "One IP address or CIDR block per line. IPv4 and IPv6 are both supported.")
    with st.form("cidr-form"):
        cidr_input = st.text_area(
            "Addresses",
            height=220,
            max_chars=MAX_INPUT_LENGTH,
            placeholder="192.168.0.0/24\n192.168.1.0/24\n10.0.0.0/8",
        )
        submitted = st.form_submit_button("Aggregate")

if submitted:
    # Stored in session_state (not rendered directly here) because the sidebar's
    # quick-search box, favorite-star buttons, and any other widget outside this
    # page's st.form trigger reruns of their own -- on those reruns `submitted` is
    # False again, which would otherwise collapse this whole results section the
    # instant any of them is touched.
    st.session_state["cidr_aggregator_result"] = aggregate_cidrs(cidr_input)

result = st.session_state.get("cidr_aggregator_result")

if result is None:
    render_empty_state("Ready to aggregate", "The minimal covering set of networks appears here after you submit.")

if result is not None:
    with tool_result_panel("cidr_result", related_to="cidr_aggregator"):
        render_section_heading("Aggregated networks", f"{result['input_count']} entries in.")
        if not result["ok"]:
            st.error(result["error"])
        else:
            c1, c2 = st.columns(2)
            c1.metric("Input entries", result["input_count"])
            c2.metric("Output networks", result["output_count"])
            rows = [
                {"CIDR": n["cidr"], "Version": f"IPv{n['version']}", "Total addresses": n["total_addresses"]}
                for n in result["networks"]
            ]
            st.dataframe(display_rows_frame(rows), width="stretch", hide_index=True)
