from __future__ import annotations

import streamlit as st

from utils.env_diff import MAX_INPUT_LENGTH, diff_env
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title=".env File Diff", layout="wide")
apply_app_shell(active_page=".env File Diff")


render_page_header(
    ".env File Diff",
    "Compare two .env files and see which keys were added, removed, or changed.",
)

with tool_form_panel("env_diff"):
    render_form_intro("Paste two .env files", "")
    with st.form("env-diff-form"):
        col_a, col_b = st.columns(2)
        text_a = col_a.text_area("First .env", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="A=1\nB=2")
        text_b = col_b.text_area("Second .env", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="A=1\nB=changed\nC=3")
        submitted = st.form_submit_button("Compare")

if submitted:
    st.session_state["env_diff_result"] = diff_env(text_a, text_b)

result = st.session_state.get("env_diff_result")

if result is None:
    render_empty_state("Ready to compare", "Added, removed, and changed keys appear here.")

if result is not None:
    with tool_result_panel("env_diff_result_panel", related_to="env_diff"):
        render_section_heading("Differences", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.caption(f"{result['unchanged_count']} unchanged key(s).")
            if result["added"]:
                st.markdown("**Added**")
                st.table([{"Key": r["key"], "Value": r["value"]} for r in result["added"]])
            if result["removed"]:
                st.markdown("**Removed**")
                st.table([{"Key": r["key"], "Value": r["value"]} for r in result["removed"]])
            if result["changed"]:
                st.markdown("**Changed**")
                st.table([{"Key": r["key"], "Old": r["old"], "New": r["new"]} for r in result["changed"]])
            if not (result["added"] or result["removed"] or result["changed"]):
                st.success("No differences found.")
