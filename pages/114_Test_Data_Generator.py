from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.test_data_generator import MAX_COUNT, generate_test_data
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


_baseline = start_page_baseline("Test Data Generator")
st.set_page_config(page_title="Test Data Generator", layout="wide")
apply_app_shell(active_page="Test Data Generator")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "Test Data Generator",
    "Generate fake names, emails, usernames, and phone numbers for filling in forms and test fixtures.",
    warning="Synthetic data from a small built-in name list, not a realistic population sample. Emails use IANA-reserved example domains (example.com/.org/.net) and phone numbers use the North American fictional-use range (555-01XX), so nothing generated here can collide with a real address.",
)

with tool_form_panel("test_data_generator"):
    render_form_intro("Choose how many records", "")
    with st.form("test-data-generator-form"):
        c1, c2 = st.columns(2)
        count = c1.number_input("Count", min_value=1, max_value=MAX_COUNT, value=10, step=1)
        seed = c2.number_input("Seed (blank = random each time)", value=None, step=1)
        submitted = st.form_submit_button("Generate", use_container_width=True)

if submitted:
    st.session_state["test_data_generator_result"] = generate_test_data(int(count), int(seed) if seed is not None else None)

result = st.session_state.get("test_data_generator_result")

if result is None:
    render_empty_state("Ready to generate", "The generated records appear here.")
    render_status_note("Awaiting generation input", "Choose count and optional seed, then generate records.", tone="neutral")

if result is not None:
    with tool_result_panel("test_data_generator_result_panel", related_to="test_data_generator"):
        render_section_heading("Generated records", eyebrow="Result")
        if not result["ok"]:
            render_failure_note(
                "Test data generation",
                result["error"],
                remediation="Adjust the count or seed and generate again.",
            )
        else:
            render_status_note(
                "Generation complete",
                f"Created {len(result['records'])} synthetic record(s) suitable for safe form and fixture testing.",
                tone="success",
            )
            st.dataframe(pd.DataFrame(result["records"]), width="stretch", hide_index=True)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
