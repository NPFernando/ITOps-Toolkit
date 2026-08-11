from __future__ import annotations

import streamlit as st

from utils.cron_overlap import MAX_LOOKAHEAD_DAYS, find_cron_overlaps
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Cron Overlap Checker", layout="wide")
apply_app_shell(active_page="Cron Overlap Checker")


render_page_header(
    "Cron Overlap Checker",
    "Check whether two cron schedules ever fire in the same minute -- useful for spotting jobs that might contend for the same resource.",
)

with tool_form_panel("cron_overlap"):
    render_form_intro("Enter two cron expressions", "")
    with st.form("cron-overlap-form"):
        c1, c2 = st.columns(2)
        expr_a = c1.text_input("Schedule A", placeholder="*/5 * * * *")
        expr_b = c2.text_input("Schedule B", placeholder="*/7 * * * *")
        lookahead_days = st.slider("Lookahead window (days)", 1, MAX_LOOKAHEAD_DAYS, 7)
        submitted = st.form_submit_button("Check for overlaps")

if submitted:
    st.session_state["cron_overlap_result"] = find_cron_overlaps(expr_a, expr_b, lookahead_days)

result = st.session_state.get("cron_overlap_result")

if result is None:
    render_empty_state("Ready to check", "Any overlapping run times appear here.")

if result is not None:
    with tool_result_panel("cron_overlap_result_panel", related_to="cron_overlap"):
        render_section_heading("Overlap check", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Schedule A runs", result["count_a"])
            c2.metric("Schedule B runs", result["count_b"])
            c3.metric("Overlaps", len(result["overlaps"]))
            if result["overlaps"]:
                st.warning("Both schedules fire at these times:")
                st.code("\n".join(result["overlaps"]), language=None)
            else:
                st.success("No overlapping run times found in this window.")
