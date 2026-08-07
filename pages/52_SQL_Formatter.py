from __future__ import annotations

import streamlit as st

from utils.sql_formatter import KEYWORD_CASES, MAX_INPUT_LENGTH, format_sql
from utils.ui import apply_app_shell, render_form_intro, render_page_header, render_section_heading, render_status_note, tool_form_panel, tool_result_panel


st.set_page_config(page_title="SQL Formatter", layout="wide")
apply_app_shell(active_page="SQL Formatter")


render_page_header(
    "SQL Formatter",
    "Reformat a pasted SQL query with consistent indentation and keyword casing.",
)

render_status_note(
    "Reformats, doesn't validate",
    "This is a lenient formatter, not a SQL validator for a specific dialect -- it never rejects input as \"invalid SQL,\" it just reformats whatever you give it.",
    tone="neutral",
)

with tool_form_panel("sql_formatter"):
    render_form_intro("Format SQL", "Paste a query -- updates live as you type.")
    col_case, col_indent = st.columns(2)
    keyword_case = col_case.selectbox("Keyword case", KEYWORD_CASES)
    indent_width = col_indent.slider("Indent width", 1, 8, 2)
    sql_input = st.text_area("SQL query", height=220, max_chars=MAX_INPUT_LENGTH, placeholder="select id, name from users where active=1;")

result = format_sql(sql_input, keyword_case, indent_width)
with tool_result_panel("sql_formatter_result", related_to="sql_formatter"):
    render_section_heading("Formatted SQL", "Reindented with consistent keyword casing.")
    if not result["ok"]:
        st.error(result["error"])
    else:
        st.code(result["formatted"], language="sql")
