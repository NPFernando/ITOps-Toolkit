from __future__ import annotations

import streamlit as st

from utils.csv_to_markdown import MAX_INPUT_LENGTH, convert_csv_to_markdown
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="CSV to Markdown Table", layout="wide")
apply_app_shell(active_page="CSV to Markdown Table")


render_page_header(
    "CSV to Markdown Table",
    "Paste CSV or TSV and get a Markdown table, ready to paste into a README, PR description, or wiki page.",
)

_DELIMITERS = {"Comma (CSV)": ",", "Tab (TSV)": "\t"}

with tool_form_panel("csv_to_markdown"):
    render_form_intro("Paste CSV or TSV", "Include a header row.")
    with st.form("csv-to-markdown-form"):
        delimiter_label = st.selectbox("Delimiter", list(_DELIMITERS.keys()))
        csv_input = st.text_area("Input", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="name,age\nAlice,30\nBob,25")
        submitted = st.form_submit_button("Convert")

if submitted:
    st.session_state["csv_to_markdown_result"] = convert_csv_to_markdown(csv_input, _DELIMITERS[delimiter_label])

result = st.session_state.get("csv_to_markdown_result")

if result is None:
    render_empty_state("Ready to convert", "The Markdown table appears here after conversion.")

if result is not None:
    with tool_result_panel("csv_to_markdown_result_panel", related_to="csv_to_markdown"):
        render_section_heading("Markdown table", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["output"], language="markdown")
            st.download_button("Download as .md", result["output"], file_name="table.md", mime="text/markdown")
