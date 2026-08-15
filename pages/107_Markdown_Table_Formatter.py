from __future__ import annotations

import streamlit as st

from utils.markdown_table_formatter import MAX_INPUT_LENGTH, format_markdown_table
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


st.set_page_config(page_title="Markdown Table Formatter", layout="wide")
apply_app_shell(active_page="Markdown Table Formatter")

st.markdown(
    """
    <style>
    @media (max-width: 768px) {
      div[data-testid="stTextArea"] textarea {
        font-size: 1rem;
      }
      div[data-testid="stFormSubmitButton"] button {
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
    "Markdown Table Formatter",
    "Paste a Markdown table with ragged/misaligned columns and get it re-aligned to consistent, padded widths.",
)

with tool_form_panel("markdown_table_formatter"):
    render_form_intro("Paste a Markdown table", "Header row, separator row (e.g. |---|---|), then data rows.")
    with st.form("markdown-table-formatter-form"):
        table_input = st.text_area(
            "Table",
            height=200,
            max_chars=MAX_INPUT_LENGTH,
            placeholder="| Name | Age |\n|---|---|\n| Alice | 30 |\n| Bob | 25 |",
        )
        submitted = st.form_submit_button("Format", use_container_width=True)

if submitted:
    st.session_state["markdown_table_formatter_result"] = format_markdown_table(table_input)

result = st.session_state.get("markdown_table_formatter_result")

if result is None:
    render_empty_state("Ready to format", "The re-aligned table appears here.")
    render_status_note("Awaiting table input", "Paste a Markdown table and run formatting to align columns.", tone="neutral")

if result is not None:
    with tool_result_panel("markdown_table_formatter_result_panel", related_to="markdown_table_formatter"):
        render_section_heading("Formatted table", eyebrow="Result")
        if not result["ok"]:
            render_failure_note(
                "Table formatting",
                result["error"],
                remediation="Provide a Markdown table with a header and separator row, then try again.",
            )
        else:
            render_status_note("Formatting complete", "The table has been realigned and is ready to copy.", tone="success")
            st.code(result["output"], language="markdown")
