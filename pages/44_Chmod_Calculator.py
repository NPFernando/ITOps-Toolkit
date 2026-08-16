from __future__ import annotations

import streamlit as st

from utils.chmod_tools import octal_to_symbolic, symbolic_to_octal
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="chmod Calculator", layout="wide")
apply_app_shell(active_page="chmod Calculator")


render_page_header(
    "chmod Calculator",
    "Convert between symbolic (rwxr-xr-x) and octal (755) Unix file permission notation.",
)

octal_tab, symbolic_tab, build_tab = st.tabs(["Octal to symbolic", "Symbolic to octal", "Build visually"])


def _render_result(result: dict) -> None:
    if not result["ok"]:
        render_status_note("Invalid permission input", result["error"], tone="warning")
        return
    c1, c2 = st.columns(2)
    c1.metric("Symbolic", result["symbolic"])
    c2.metric("Octal", result["octal"])
    st.table(result["breakdown"])
    flags = [flag for flag, present in (("setuid", result["setuid"]), ("setgid", result["setgid"]), ("sticky", result["sticky"])) if present]
    if flags:
        st.caption(f"Special bits: {', '.join(flags)}")


with octal_tab:
    with tool_form_panel("chmod_octal_to_symbolic"):
        render_form_intro("Octal to symbolic", "Enter 3 or 4 octal digits (e.g. 755 or 4755).")
        octal_input = st.text_input("Octal", placeholder="755", key="chmod_octal_input")
    with tool_result_panel("chmod_octal_result", related_to="chmod_calculator"):
        render_section_heading("Result", "Owner, group, and other permissions.")
        if not octal_input.strip():
            render_empty_state("Ready for input", "Owner, group, and other permissions appear here as soon as you type.")
        else:
            _render_result(octal_to_symbolic(octal_input))

with symbolic_tab:
    with tool_form_panel("chmod_symbolic_to_octal"):
        render_form_intro("Symbolic to octal", "Enter 9 permission characters (e.g. rwxr-xr-x).")
        symbolic_input = st.text_input("Symbolic", placeholder="rwxr-xr-x", key="chmod_symbolic_input")
    with tool_result_panel("chmod_symbolic_result", related_to="chmod_calculator"):
        render_section_heading("Result", "Owner, group, and other permissions.")
        if not symbolic_input.strip():
            render_empty_state("Ready for input", "Owner, group, and other permissions appear here as soon as you type.")
        else:
            _render_result(symbolic_to_octal(symbolic_input))

with build_tab:
    with tool_form_panel("chmod_build"):
        render_form_intro("Build permissions", "Check the boxes for each permission bit.")
        cols = st.columns(3)
        digits = []
        for col, who in zip(cols, ("Owner", "Group", "Other"), strict=True):
            with col:
                st.markdown(f"**{who}**")
                r = st.checkbox("Read", key=f"chmod_build_{who}_r")
                w = st.checkbox("Write", key=f"chmod_build_{who}_w")
                x = st.checkbox("Execute", key=f"chmod_build_{who}_x")
                digits.append((4 if r else 0) + (2 if w else 0) + (1 if x else 0))
    with tool_result_panel("chmod_build_result", related_to="chmod_calculator"):
        render_section_heading("Build result", "Owner, group, and other permissions.")
        octal_value = "".join(str(d) for d in digits)
        _render_result(octal_to_symbolic(octal_value))
