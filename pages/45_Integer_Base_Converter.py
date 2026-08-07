from __future__ import annotations

import streamlit as st

from utils.base_converter import BASES, convert_base
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Integer Base Converter", layout="wide")
apply_app_shell(active_page="Integer Base Converter")


render_page_header(
    "Integer Base Converter",
    "Convert a number between binary, octal, decimal, and hexadecimal, live as you type.",
)

with tool_form_panel("base_converter"):
    render_form_intro("Convert", "Enter a number and its base -- output updates as you type.")
    col_value, col_base = st.columns([2, 1])
    value = col_value.text_input("Number", placeholder="255, ff, 0b1010, 377...")
    from_base = col_base.selectbox("From base", list(BASES))

with tool_result_panel("base_converter_result", related_to="base_converter"):
    render_section_heading("Result", "Rendered in every supported base.")
    if not value.strip():
        render_empty_state("Ready for input", "The number appears here in every supported base as soon as you type.")
    else:
        result = convert_base(value, from_base)
        if not result["ok"]:
            st.error(result["error"])
        else:
            cols = st.columns(4)
            for col, (label, base_value) in zip(cols, result["values"].items(), strict=True):
                col.metric(label, base_value)
