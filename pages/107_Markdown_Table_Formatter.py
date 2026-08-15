from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
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


_baseline = start_page_baseline("Markdown Table Formatter")
st.set_page_config(page_title="Markdown Table Formatter", layout="wide")
apply_app_shell(active_page="Markdown Table Formatter")
mark_page_baseline(_baseline, "shell-ready")


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
            render_status_note("Formatting complete", "The formatted Markdown table is ready to copy.", tone="success")
            st.code(result["output"], language="markdown")

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
