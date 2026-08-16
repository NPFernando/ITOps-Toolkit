from __future__ import annotations

import streamlit as st

from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)
from utils.user_agent_tools import MAX_INPUT_LENGTH, parse_user_agent


st.set_page_config(page_title="User-Agent Parser", layout="wide")
apply_app_shell(active_page="User-Agent Parser")


render_page_header(
    "User-Agent Parser",
    "Break a User-Agent header down into likely browser, OS, and device details.",
    warning="Best-effort, rule-based parsing covering common browsers, OSes, and bots -- not an exhaustive database.",
)

with tool_form_panel("user_agent_parser"):
    render_form_intro("Paste a User-Agent string", "From a request header, log line, or browser's own devtools.")
    with st.form("user-agent-form"):
        ua_input = st.text_input(
            "User-Agent",
            max_chars=MAX_INPUT_LENGTH,
            placeholder="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...",
        )
        submitted = st.form_submit_button("Parse")

if submitted:
    # Stored in session_state (not rendered directly here) because the sidebar's
    # quick-search box, favorite-star buttons, and any other widget outside this
    # page's st.form trigger reruns of their own -- on those reruns `submitted` is
    # False again, which would otherwise collapse this whole results section the
    # instant any of them is touched.
    st.session_state["user_agent_parser_result"] = parse_user_agent(ua_input)

result = st.session_state.get("user_agent_parser_result")

if result is None:
    render_empty_state("Ready to parse", "Browser, OS, and device details appear here after you submit a User-Agent.")

if submitted:
    result = parse_user_agent(ua_input)
    with tool_result_panel("user_agent_result", related_to="user_agent_parser"):
        render_section_heading("Parsed details", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        elif result["is_bot"]:
            st.info(f"Detected as a bot/automated client: **{result['bot_name']}**")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Browser", result["browser"] or "Unknown")
            c2.metric("OS", result["os"] or "Unknown")
            c3.metric("Device type", result["device_type"])
            if result["browser_version"] or result["os_version"]:
                st.caption(
                    f"Browser version: {result['browser_version'] or 'unknown'} | "
                    f"OS version: {result['os_version'] or 'unknown'}"
                )
