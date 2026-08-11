from __future__ import annotations

import streamlit as st

from utils.deterministic_uuid import MAX_INPUT_LENGTH, NAMESPACES, generate_deterministic_uuid
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Deterministic UUID Generator", layout="wide")
apply_app_shell(active_page="Deterministic UUID Generator")


render_page_header(
    "Deterministic UUID Generator",
    "Generate a namespace-based UUID (v3 MD5 or v5 SHA-1) -- the same namespace and name always produce the same UUID.",
)

with tool_form_panel("deterministic_uuid"):
    render_form_intro("Enter a namespace and name", "Choose a standard namespace and enter a name to hash.")
    with st.form("deterministic-uuid-form"):
        namespace = st.selectbox("Namespace", list(NAMESPACES.keys()))
        version = st.radio("Version", (5, 3), horizontal=True, format_func=lambda v: f"v{v} ({'SHA-1' if v == 5 else 'MD5'})")
        name = st.text_input("Name", placeholder="example.com", max_chars=MAX_INPUT_LENGTH)
        submitted = st.form_submit_button("Generate")

if submitted:
    st.session_state["deterministic_uuid_result"] = generate_deterministic_uuid(namespace, name, version)

result = st.session_state.get("deterministic_uuid_result")

if result is None:
    render_empty_state("Ready to generate", "The generated UUID appears here.")

if result is not None:
    with tool_result_panel("deterministic_uuid_result_panel", related_to="deterministic_uuid"):
        render_section_heading("Generated UUID", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["result"], language=None)
