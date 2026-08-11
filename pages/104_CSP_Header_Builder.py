from __future__ import annotations

import streamlit as st

from utils.csp_builder import DIRECTIVES, build_csp
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="CSP Header Builder", layout="wide")
apply_app_shell(active_page="CSP Header Builder")


render_page_header(
    "CSP Header Builder",
    "Build a Content-Security-Policy header value from directives and source lists, entirely locally.",
    warning="Known keyword sources ('self', 'none', 'unsafe-inline', 'unsafe-eval', 'unsafe-hashes', 'strict-dynamic', 'report-sample') are auto-quoted; anything else (a host, scheme, or nonce/hash) is left unquoted.",
)

with tool_form_panel("csp_builder"):
    render_form_intro("Enter sources per directive", "Space or comma-separated, e.g. self unsafe-inline https://cdn.example.com. Leave a directive blank to skip it.")
    with st.form("csp-builder-form"):
        directive_inputs = {}
        for directive in DIRECTIVES:
            directive_inputs[directive] = st.text_input(directive, key=f"csp_{directive}")
        submitted = st.form_submit_button("Build header")

if submitted:
    st.session_state["csp_builder_result"] = build_csp(directive_inputs)

result = st.session_state.get("csp_builder_result")

if result is None:
    render_empty_state("Ready to build", "The Content-Security-Policy header value appears here.")

if result is not None:
    with tool_result_panel("csp_builder_result_panel", related_to="csp_builder"):
        render_section_heading("Content-Security-Policy", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["output"], language=None)
