from __future__ import annotations

import streamlit as st

from utils.cache_control_tool import DIRECTIVE_DESCRIPTIONS, MAX_INPUT_LENGTH, build_cache_control, explain_cache_control
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Cache-Control Tool", layout="wide")
apply_app_shell(active_page="Cache-Control Tool")


render_page_header(
    "Cache-Control Tool",
    "Build a Cache-Control header from directives, or paste one to see each directive explained.",
)

build_tab, explain_tab = st.tabs(["Build", "Explain"])

with build_tab:
    with tool_form_panel("cache_control_build"):
        render_form_intro("Choose directives", "")
        with st.form("cache-control-build-form"):
            flags = st.multiselect("Flag directives", list(DIRECTIVE_DESCRIPTIONS.keys()))
            c1, c2 = st.columns(2)
            max_age = c1.number_input("max-age (seconds, blank = omit)", value=None, min_value=0, step=1)
            s_maxage = c2.number_input("s-maxage (seconds, blank = omit)", value=None, min_value=0, step=1)
            build_submitted = st.form_submit_button("Build header")

    if build_submitted:
        st.session_state["cache_control_build_result"] = build_cache_control(
            flags,
            int(max_age) if max_age is not None else None,
            int(s_maxage) if s_maxage is not None else None,
        )

    build_result = st.session_state.get("cache_control_build_result")

    if build_result is None:
        render_empty_state("Ready to build", "The Cache-Control header value appears here.")

    if build_result is not None:
        with tool_result_panel("cache_control_build_result_panel", related_to="cache_control_tool"):
            render_section_heading("Cache-Control", eyebrow="Result")
            if not build_result["ok"]:
                st.error(build_result["error"])
            else:
                st.code(build_result["output"], language=None)

with explain_tab:
    with tool_form_panel("cache_control_explain"):
        render_form_intro("Paste a Cache-Control header value", "")
        with st.form("cache-control-explain-form"):
            header_input = st.text_input("Header value", placeholder="public, max-age=3600, must-revalidate", max_chars=MAX_INPUT_LENGTH)
            explain_submitted = st.form_submit_button("Explain")

    if explain_submitted:
        st.session_state["cache_control_explain_result"] = explain_cache_control(header_input)

    explain_result = st.session_state.get("cache_control_explain_result")

    if explain_result is None:
        render_empty_state("Ready to explain", "Each directive's meaning appears here.")

    if explain_result is not None:
        with tool_result_panel("cache_control_explain_result_panel", related_to="cache_control_tool"):
            render_section_heading("Directives", eyebrow="Result")
            if not explain_result["ok"]:
                st.error(explain_result["error"])
            else:
                for entry in explain_result["directives"]:
                    st.markdown(f"**{entry['directive']}** -- {entry['description']}")
