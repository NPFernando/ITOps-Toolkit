from __future__ import annotations

import streamlit as st

from utils.user_agent_builder import BROWSER_OPTIONS, OS_OPTIONS, build_user_agent
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="User-Agent Builder", layout="wide")
apply_app_shell(active_page="User-Agent Builder")


render_page_header(
    "User-Agent Builder",
    "Build a User-Agent string for a chosen OS, browser, and version -- the reverse of User Agent Parser.",
)

with tool_form_panel("user_agent_builder"):
    render_form_intro("Choose OS, browser, and version", "Pick a real-world combination.")
    with st.form("user-agent-builder-form"):
        c1, c2, c3 = st.columns(3)
        os_name = c1.selectbox("OS", OS_OPTIONS)
        browser = c2.selectbox("Browser", BROWSER_OPTIONS)
        version = c3.text_input("Version", value="128.0.0.0", placeholder="128.0.0.0")
        submitted = st.form_submit_button("Build")

if submitted:
    st.session_state["user_agent_builder_result"] = build_user_agent(os_name, browser, version)

result = st.session_state.get("user_agent_builder_result")

if result is None:
    render_empty_state("Ready to build", "The User-Agent string appears here.")

if result is not None:
    with tool_result_panel("user_agent_builder_result_panel", related_to="user_agent_builder"):
        render_section_heading("User-Agent string", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["output"], language=None)
