from __future__ import annotations

import streamlit as st

from utils.cidr_overlap import MAX_INPUT_LENGTH, check_cidr_overlaps
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="CIDR Overlap Checker", layout="wide")
apply_app_shell(active_page="CIDR Overlap Checker")


render_page_header(
    "CIDR Overlap Checker",
    "Check whether any of a list of IPs or CIDR blocks overlap -- a pre-flight check before allocating a new subnet.",
)

with tool_form_panel("cidr_overlap"):
    render_form_intro("Enter addresses", "One IP address or CIDR block per line. IPv4 and IPv6 are both supported.")
    with st.form("cidr-overlap-form"):
        cidr_input = st.text_area(
            "Addresses",
            height=220,
            max_chars=MAX_INPUT_LENGTH,
            placeholder="10.0.0.0/24\n10.0.0.128/25\n192.168.0.0/24",
        )
        submitted = st.form_submit_button("Check overlap")

if submitted:
    st.session_state["cidr_overlap_result"] = check_cidr_overlaps(cidr_input)

result = st.session_state.get("cidr_overlap_result")

if result is None:
    render_empty_state("Ready to check", "Any overlapping pairs appear here after you submit.")

if result is not None:
    with tool_result_panel("cidr_overlap_result_panel", related_to="cidr_overlap"):
        render_section_heading("Overlap check", f"{result.get('input_count', 0)} entries in." if result["ok"] else "Result")
        if not result["ok"]:
            st.error(result["error"])
        elif not result["has_overlaps"]:
            st.success("No overlaps found among the entered ranges.")
        else:
            st.warning(f"{len(result['overlaps'])} overlapping pair(s) found:")
            st.table([{"Range A": o["a"], "Range B": o["b"]} for o in result["overlaps"]])
