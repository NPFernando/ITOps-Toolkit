from __future__ import annotations

import streamlit as st

from utils.wsl_path_converter import TARGETS, convert_path
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="WSL Path Converter", layout="wide")
apply_app_shell(active_page="WSL Path Converter")


render_page_header(
    "WSL Path Converter",
    "Convert a filesystem path between Windows, WSL, and Git Bash forms -- WSL mounts drives at /mnt/c/..., Git Bash mounts them at /c/... instead.",
)

with tool_form_panel("wsl_path_converter"):
    render_form_intro("Enter a path and target format", "")
    with st.form("wsl-path-converter-form"):
        path_input = st.text_input("Path", placeholder=r"C:\Users\naveen\file.txt")
        target = st.radio("Convert to", TARGETS, horizontal=True)
        submitted = st.form_submit_button("Convert")

if submitted:
    st.session_state["wsl_path_converter_result"] = convert_path(path_input, target)

result = st.session_state.get("wsl_path_converter_result")

if result is None:
    render_empty_state("Ready to convert", "The converted path appears here.")

if result is not None:
    with tool_result_panel("wsl_path_converter_result_panel", related_to="wsl_path_converter"):
        render_section_heading("Converted path", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["output"], language=None)
