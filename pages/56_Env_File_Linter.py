from __future__ import annotations

import streamlit as st

from utils.env_linter import MAX_INPUT_LENGTH, lint_env
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title=".env File Linter", layout="wide")
apply_app_shell(active_page=".env File Linter")


render_page_header(
    ".env File Linter",
    "Paste .env content to flag duplicate keys, unquoted values with spaces, unterminated quotes, and other common mistakes.",
)

with tool_form_panel("env_linter"):
    render_form_intro("Lint", "Paste the contents of a .env file.")
    with st.form("env-linter-form"):
        text = st.text_area("Env content", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="DATABASE_URL=postgres://...\nDEBUG=true")
        submitted = st.form_submit_button("Lint")

if submitted:
    # Stored in session_state so the results survive the sidebar's own
    # reruns (quick-search box, favorite stars) after the initial submit.
    st.session_state["env_linter_state"] = lint_env(text)

state = st.session_state.get("env_linter_state")

if state is None:
    render_empty_state("Ready to lint", "Issues found in your .env content appear here.")

if state is not None:
    with tool_result_panel("env_linter_result", related_to="env_linter"):
        render_section_heading("Lint results", eyebrow="Result")
        if not state["ok"]:
            st.error(state["error"])
        elif not state["issues"]:
            st.success("No issues found.")
        else:
            st.table([{"Line": issue["line"], "Issue": issue["message"]} for issue in state["issues"]])
