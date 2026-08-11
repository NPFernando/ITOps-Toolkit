from __future__ import annotations

import streamlit as st

from utils.json_to_typescript import MAX_INPUT_LENGTH, json_to_typescript
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="JSON to TypeScript", layout="wide")
apply_app_shell(active_page="JSON to TypeScript")


render_page_header(
    "JSON to TypeScript",
    "Infer a TypeScript interface from a JSON document, with nested objects broken out into their own interfaces.",
)

with tool_form_panel("json_to_typescript"):
    render_form_intro("Paste JSON", "")
    with st.form("json-to-typescript-form"):
        json_input = st.text_area(
            "JSON",
            height=280,
            max_chars=MAX_INPUT_LENGTH,
            placeholder='{"name": "Alice", "age": 30, "address": {"city": "NYC"}}',
        )
        root_name_input = st.text_input("Root interface name", value="Root")
        submitted = st.form_submit_button("Generate")

if submitted:
    st.session_state["json_to_typescript_result"] = json_to_typescript(json_input, root_name_input)

result = st.session_state.get("json_to_typescript_result")

if result is None:
    render_empty_state("Ready to generate", "The TypeScript interface(s) appear here.")

if result is not None:
    with tool_result_panel("json_to_typescript_result_panel", related_to="json_to_typescript"):
        render_section_heading("TypeScript", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["output"], language="typescript")
