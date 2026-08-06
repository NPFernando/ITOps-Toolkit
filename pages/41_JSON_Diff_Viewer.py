from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.json_diff import diff_json
from utils.text_tools import MAX_JSON_LENGTH
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="JSON Diff Viewer", layout="wide")
apply_app_shell(active_page="JSON Diff Viewer")


render_page_header(
    "JSON Diff Viewer",
    "Structurally compare two JSON documents by key/path, not by line -- unaffected by key reordering.",
)

with tool_form_panel("json_diff"):
    render_form_intro("Compare JSON", "Paste two JSON documents to compare.")
    with st.form("json-diff-form"):
        col_a, col_b = st.columns(2)
        text_a = col_a.text_area("First JSON", height=280, max_chars=MAX_JSON_LENGTH, placeholder='{"a": 1}')
        text_b = col_b.text_area("Second JSON", height=280, max_chars=MAX_JSON_LENGTH, placeholder='{"a": 2}')
        submitted = st.form_submit_button("Compare")

if submitted:
    st.session_state["json_diff_result"] = diff_json(text_a, text_b)

result = st.session_state.get("json_diff_result")

if result is None:
    render_empty_state("Ready to compare", "Structural differences (added/removed/changed, by path) appear here after comparison.")

if result is not None:
    with tool_result_panel("json_diff_result_panel", related_to="json_diff"):
        render_section_heading("Differences", "Added, removed, and changed values by JSON path.")
        if not result["ok"]:
            st.error(result["error"])
        elif result["identical"]:
            st.success("The two documents are structurally identical.")
        else:
            if result["truncated"]:
                st.warning(f"Showing the first {len(result['differences'])} differences.")
            st.dataframe(
                pd.DataFrame(
                    [
                        {"Path": d["path"], "Type": d["type"], "Old value": d["old"], "New value": d["new"]}
                        for d in result["differences"]
                    ]
                ),
                width="stretch",
                hide_index=True,
            )
