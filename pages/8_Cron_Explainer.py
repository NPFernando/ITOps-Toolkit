from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.text_tools import explain_cron
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Cron Explainer", layout="wide")
apply_app_shell(active_page="Cron Explainer")


render_page_header("Cron Explainer", "Supports common 5-field cron expressions.")

with tool_form_panel("cron_explainer"):
    render_form_intro("Explain cron", "Enter a common 5-field cron expression to preview its schedule.")
    with st.form("cron-form"):
        expression = st.text_input("Cron expression", placeholder="*/15 * * * *")
        submitted = st.form_submit_button("Explain cron")

if not submitted:
    render_empty_state("Ready to explain a schedule", "A readable explanation and the next five run times appear after validation.")

if submitted:
    with tool_result_panel("cron_result"):
        result = explain_cron(expression)
        render_section_heading("Cron result", "Readable schedule summary and next run times.")
        if result["ok"]:
            st.success("Valid cron expression")
        else:
            st.error(result["error"])

        render_section_heading("Readable explanation", eyebrow="Schedule")
        st.info(result["description"])

        render_section_heading("Next 5 run times", eyebrow="Schedule")
        if result["next_runs"]:
            st.dataframe(pd.DataFrame({"run_time": result["next_runs"]}), width="stretch", hide_index=True)
        else:
            st.caption("No run times available for invalid input.")
