from __future__ import annotations

import streamlit as st

from utils.cron_overlap import MAX_LOOKAHEAD_DAYS, find_cron_overlaps
from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
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


_baseline = start_page_baseline("Cron Overlap Checker")
st.set_page_config(page_title="Cron Overlap Checker", layout="wide")
apply_app_shell(active_page="Cron Overlap Checker")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "Cron Overlap Checker",
    "Check whether two cron schedules ever fire in the same minute -- useful for spotting jobs that might contend for the same resource.",
)

with tool_form_panel("cron_overlap"):
    render_form_intro("Enter two cron expressions", "")
    with st.form("cron-overlap-form"):
        st.markdown('<div class="tool-panel-eyebrow">Schedule A</div>', unsafe_allow_html=True)
        expr_a = st.text_input("Schedule A", placeholder="*/5 * * * *")
        st.markdown('<div class="tool-panel-eyebrow">Schedule B</div>', unsafe_allow_html=True)
        expr_b = st.text_input("Schedule B", placeholder="*/7 * * * *")
        lookahead_days = st.slider("Lookahead window (days)", 1, MAX_LOOKAHEAD_DAYS, 7)
        submitted = st.form_submit_button("Check for overlaps", use_container_width=True)

if submitted:
    st.session_state["cron_overlap_result"] = find_cron_overlaps(expr_a, expr_b, lookahead_days)

result = st.session_state.get("cron_overlap_result")

if result is None:
    render_empty_state("Ready to check", "Any overlapping run times appear here.")
    render_status_note("Awaiting cron input", "Enter both schedules and run the overlap check.", tone="neutral")

if result is not None:
    with tool_result_panel("cron_overlap_result_panel", related_to="cron_overlap"):
        render_section_heading("Overlap check", eyebrow="Result")
        if not result["ok"]:
            render_failure_note("Cron overlap check", result["error"], remediation="Provide valid cron expressions and rerun.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Schedule A runs", result["count_a"])
            c2.metric("Schedule B runs", result["count_b"])
            c3.metric("Overlaps", len(result["overlaps"]))
            if result["overlaps"]:
                st.caption("Shared run times (same minute):")
                st.code("\n".join(result["overlaps"]), language=None)
                render_status_note(
                    "Overlaps detected",
                    f"Found {len(result['overlaps'])} shared minute(s) in this lookahead window. Resolve collisions before running both jobs together.",
                    tone="warning",
                )
            else:
                render_status_note(
                    "No overlaps detected",
                    "No shared run minutes were found between these schedules in the selected lookahead window.",
                    tone="success",
                )

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
