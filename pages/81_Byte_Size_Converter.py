from __future__ import annotations

import streamlit as st

from utils.byte_size_converter import MAX_INPUT_LENGTH, UNITS, bytes_to_human, human_to_bytes
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Byte Size Converter", layout="wide")
apply_app_shell(active_page="Byte Size Converter")


render_page_header(
    "Byte Size Converter",
    "Convert a byte count to human-readable units (KB/MB/GB/TB), or the reverse.",
)

to_human_tab, to_bytes_tab = st.tabs(["Bytes to human-readable", "Human-readable to bytes"])

with to_human_tab:
    with tool_form_panel("bytes_to_human"):
        render_form_intro("Enter a byte count", "Choose binary (1024-based) or decimal (1000-based) units.")
        with st.form("bytes-to-human-form"):
            count_input = st.text_input("Bytes", placeholder="5368709120", max_chars=MAX_INPUT_LENGTH)
            unit_system = st.radio("Unit system", ("Binary (1024)", "Decimal (1000)"), horizontal=True)
            to_human_submitted = st.form_submit_button("Convert")

    if to_human_submitted:
        st.session_state["bytes_to_human_result"] = bytes_to_human(count_input, binary=unit_system.startswith("Binary"))

    to_human_result = st.session_state.get("bytes_to_human_result")

    if to_human_result is None:
        render_empty_state("Ready to convert", "The human-readable size appears here.")

    if to_human_result is not None:
        with tool_result_panel("bytes_to_human_result_panel", related_to="byte_size_converter"):
            render_section_heading("Human-readable size", eyebrow="Result")
            if not to_human_result["ok"]:
                st.error(to_human_result["error"])
            else:
                st.metric("Size", to_human_result["result"])

with to_bytes_tab:
    with tool_form_panel("human_to_bytes"):
        render_form_intro("Enter a value and unit", "Choose binary (1024-based) or decimal (1000-based) units.")
        with st.form("human-to-bytes-form"):
            unit_system2 = st.radio("Unit system", ("Binary (1024)", "Decimal (1000)"), horizontal=True, key="unit_system2")
            is_binary = unit_system2.startswith("Binary")
            c1, c2 = st.columns(2)
            value_input = c1.text_input("Value", placeholder="5", max_chars=MAX_INPUT_LENGTH)
            unit_input = c2.selectbox("Unit", UNITS[is_binary])
            to_bytes_submitted = st.form_submit_button("Convert")

    if to_bytes_submitted:
        st.session_state["human_to_bytes_result"] = human_to_bytes(value_input, unit_input, binary=is_binary)

    to_bytes_result = st.session_state.get("human_to_bytes_result")

    if to_bytes_result is None:
        render_empty_state("Ready to convert", "The raw byte count appears here.")

    if to_bytes_result is not None:
        with tool_result_panel("human_to_bytes_result_panel", related_to="byte_size_converter"):
            render_section_heading("Byte count", eyebrow="Result")
            if not to_bytes_result["ok"]:
                st.error(to_bytes_result["error"])
            else:
                st.metric("Bytes", to_bytes_result["result"])
