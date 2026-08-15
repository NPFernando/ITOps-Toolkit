from __future__ import annotations

import streamlit as st

from utils.cache_control_tool import DIRECTIVE_DESCRIPTIONS, MAX_INPUT_LENGTH, build_cache_control, explain_cache_control
from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
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


_baseline = start_page_baseline("Cache-Control Tool")
st.set_page_config(page_title="Cache-Control Tool", layout="wide")
apply_app_shell(active_page="Cache-Control Tool")
mark_page_baseline(_baseline, "shell-ready")


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
            max_age = st.number_input("max-age (seconds, blank = omit)", value=None, min_value=0, step=1)
            s_maxage = st.number_input("s-maxage (seconds, blank = omit)", value=None, min_value=0, step=1)
            build_submitted = st.form_submit_button("Build header", use_container_width=True)

    if build_submitted:
        st.session_state["cache_control_build_result"] = build_cache_control(
            flags,
            int(max_age) if max_age is not None else None,
            int(s_maxage) if s_maxage is not None else None,
        )

    build_result = st.session_state.get("cache_control_build_result")

    if build_result is None:
        render_empty_state("Ready to build", "The Cache-Control header value appears here.")
        render_status_note("Awaiting directives", "Pick one or more directives and build a header value.", tone="neutral")

    if build_result is not None:
        with tool_result_panel("cache_control_build_result_panel", related_to="cache_control_tool"):
            render_section_heading("Cache-Control", eyebrow="Result")
            if not build_result["ok"]:
                render_failure_note(
                    "Header generation",
                    build_result["error"],
                    remediation="Adjust directive selections and retry.",
                )
            else:
                render_status_note("Header ready", "The Cache-Control header value is ready to copy.", tone="success")
                st.code(build_result["output"], language=None)

with explain_tab:
    with tool_form_panel("cache_control_explain"):
        render_form_intro("Paste a Cache-Control header value", "")
        with st.form("cache-control-explain-form"):
            header_input = st.text_input("Header value", placeholder="public, max-age=3600, must-revalidate", max_chars=MAX_INPUT_LENGTH)
            explain_submitted = st.form_submit_button("Explain", use_container_width=True)

    if explain_submitted:
        st.session_state["cache_control_explain_result"] = explain_cache_control(header_input)

    explain_result = st.session_state.get("cache_control_explain_result")

    if explain_result is None:
        render_empty_state("Ready to explain", "Each directive's meaning appears here.")
        render_status_note("Awaiting header value", "Paste a Cache-Control value to explain each directive.", tone="neutral")

    if explain_result is not None:
        with tool_result_panel("cache_control_explain_result_panel", related_to="cache_control_tool"):
            render_section_heading("Directives", eyebrow="Result")
            if not explain_result["ok"]:
                render_failure_note(
                    "Directive explanation",
                    explain_result["error"],
                    remediation="Provide a valid Cache-Control header value and retry.",
                )
            else:
                render_status_note("Directive explanation ready", "Directive meanings are listed below.", tone="success")
                for entry in explain_result["directives"]:
                    st.markdown(f"**{entry['directive']}** -- {entry['description']}")

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
