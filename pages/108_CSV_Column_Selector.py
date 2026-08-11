from __future__ import annotations

import streamlit as st

from utils.csv_column_selector import MAX_INPUT_LENGTH, select_columns
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="CSV Column Selector", layout="wide")
apply_app_shell(active_page="CSV Column Selector")


render_page_header(
    "CSV Column Selector",
    "Extract and reorder specific columns from CSV/TSV by header name.",
)

_DELIMITERS = {"Comma (CSV)": ",", "Tab (TSV)": "\t"}

with tool_form_panel("csv_column_selector"):
    render_form_intro("Paste CSV or TSV and the columns to keep", "Comma-separated column names, in the order you want them.")
    with st.form("csv-column-selector-form"):
        delimiter_label = st.selectbox("Delimiter", list(_DELIMITERS.keys()))
        csv_input = st.text_area("Input", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="name,age,city\nAlice,30,NYC\nBob,25,LA")
        columns_input = st.text_input("Columns to keep", placeholder="city, name")
        submitted = st.form_submit_button("Select columns")

if submitted:
    st.session_state["csv_column_selector_result"] = select_columns(csv_input, columns_input, _DELIMITERS[delimiter_label])

result = st.session_state.get("csv_column_selector_result")

if result is None:
    render_empty_state("Ready to select", "The extracted columns appear here.")

if result is not None:
    with tool_result_panel("csv_column_selector_result_panel", related_to="csv_column_selector"):
        render_section_heading("Result", eyebrow="Output")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["output"], language=None)
            st.download_button("Download as .csv", result["output"], file_name="selected_columns.csv", mime="text/csv")
