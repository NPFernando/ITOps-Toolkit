from __future__ import annotations

import streamlit as st

from utils.csv_cleaner import MAX_INPUT_LENGTH, clean_csv
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="CSV/TSV Cleaner", layout="wide")
apply_app_shell(active_page="CSV/TSV Cleaner")


render_page_header(
    "CSV/TSV Cleaner",
    "Paste messy CSV/TSV and trim cell whitespace, drop empty rows, and/or remove duplicate rows.",
)

_DELIMITERS = {"Comma (CSV)": ",", "Tab (TSV)": "\t"}

with tool_form_panel("csv_cleaner"):
    render_form_intro("Paste CSV or TSV", "Choose what to clean up.")
    with st.form("csv-cleaner-form"):
        delimiter_label = st.selectbox("Delimiter", list(_DELIMITERS.keys()))
        csv_input = st.text_area("Input", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="name, age \nAlice ,30\nAlice ,30\n,\n")
        c1, c2, c3 = st.columns(3)
        trim_cells = c1.checkbox("Trim cell whitespace", value=True)
        drop_empty_rows = c2.checkbox("Drop empty rows", value=True)
        dedupe_rows = c3.checkbox("Remove duplicate rows", value=False)
        submitted = st.form_submit_button("Clean")

if submitted:
    st.session_state["csv_cleaner_result"] = clean_csv(csv_input, _DELIMITERS[delimiter_label], trim_cells, drop_empty_rows, dedupe_rows)

result = st.session_state.get("csv_cleaner_result")

if result is None:
    render_empty_state("Ready to clean", "The cleaned CSV/TSV appears here.")

if result is not None:
    with tool_result_panel("csv_cleaner_result_panel", related_to="csv_cleaner"):
        render_section_heading("Cleaned output", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            c1, c2 = st.columns(2)
            c1.metric("Rows kept", result["row_count"])
            c2.metric("Rows removed", result["removed_count"])
            st.code(result["output"], language=None)
            st.download_button("Download as .csv", result["output"], file_name="cleaned.csv", mime="text/csv")
