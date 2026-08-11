from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.test_data_generator import MAX_COUNT, generate_test_data
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Test Data Generator", layout="wide")
apply_app_shell(active_page="Test Data Generator")


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
        submitted = st.form_submit_button("Generate")

if submitted:
    st.session_state["test_data_generator_result"] = generate_test_data(int(count), int(seed) if seed is not None else None)

result = st.session_state.get("test_data_generator_result")

if result is None:
    render_empty_state("Ready to generate", "The generated records appear here.")

if result is not None:
    with tool_result_panel("test_data_generator_result_panel", related_to="test_data_generator"):
        render_section_heading("Generated records", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.dataframe(pd.DataFrame(result["records"]), width="stretch", hide_index=True)
