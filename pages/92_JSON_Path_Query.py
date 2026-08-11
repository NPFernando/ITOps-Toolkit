from __future__ import annotations

import streamlit as st

from utils.json_path_query import MAX_INPUT_LENGTH, query_json_path
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="JSON Path Query", layout="wide")
apply_app_shell(active_page="JSON Path Query")


render_page_header(
    "JSON Path Query",
    "Extract a value from JSON with a simple dotted path, e.g. user.addresses[0].city.",
    warning='Supports dotted keys and [index] array access only -- no wildcards, filters, or slicing (not a full JSONPath/JMESPath implementation).',
)

with tool_form_panel("json_path_query"):
    render_form_intro("Paste JSON and a path", "e.g. user.addresses[0].city")
    with st.form("json-path-query-form"):
        json_input = st.text_area(
            "JSON",
            height=280,
            max_chars=MAX_INPUT_LENGTH,
            placeholder='{"user": {"name": "Alice", "addresses": [{"city": "NYC"}]}}',
        )
        path_input = st.text_input("Path", placeholder="user.addresses[0].city")
        submitted = st.form_submit_button("Query")

if submitted:
    st.session_state["json_path_query_result"] = query_json_path(json_input, path_input)

result = st.session_state.get("json_path_query_result")

if result is None:
    render_empty_state("Ready to query", "The value at that path appears here.")

if result is not None:
    with tool_result_panel("json_path_query_result_panel", related_to="json_path_query"):
        render_section_heading("Value", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["output"], language="json")
