from __future__ import annotations

import streamlit as st

from utils.csv_column_selector import MAX_INPUT_LENGTH, select_columns
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


st.set_page_config(page_title="CSV Column Selector", layout="wide")
apply_app_shell(active_page="CSV Column Selector")

st.markdown(
    """
    <style>
    @media (max-width: 768px) {
      div[data-testid="stSelectbox"] > div,
      div[data-testid="stTextInput"] input,
      div[data-testid="stTextArea"] textarea {
        font-size: 1rem;
      }
      div[data-testid="stFormSubmitButton"] button,
      div[data-testid="stDownloadButton"] button {
        width: 100%;
        min-height: 2.75rem;
      }
      div[data-testid="stCodeBlock"] pre {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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
        submitted = st.form_submit_button("Select columns", use_container_width=True)

if submitted:
    st.session_state["csv_column_selector_result"] = select_columns(csv_input, columns_input, _DELIMITERS[delimiter_label])

result = st.session_state.get("csv_column_selector_result")

if result is None:
    render_empty_state("Ready to select", "The extracted columns appear here.")
    render_status_note("Awaiting tabular input", "Paste CSV/TSV text, choose columns, then run selection.", tone="neutral")

if result is not None:
    with tool_result_panel("csv_column_selector_result_panel", related_to="csv_column_selector"):
        render_section_heading("Result", eyebrow="Output")
        if not result["ok"]:
            render_failure_note(
                "Column selection",
                result["error"],
                remediation="Confirm the input has a header row and the requested column names, then try again.",
            )
        else:
            render_status_note("Column selection complete", "The selected columns are ready below and can be downloaded as CSV.", tone="success")
            st.code(result["output"], language=None)
            st.download_button("Download as .csv", result["output"], file_name="selected_columns.csv", mime="text/csv", use_container_width=True)
