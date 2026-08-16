from __future__ import annotations

import streamlit as st

from utils.color_tools import MAX_INPUT_LENGTH, parse_color
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Color Converter", layout="wide")
apply_app_shell(active_page="Color Converter")


render_page_header(
    "Color Converter",
    "Convert colors between HEX, RGB, and HSL, with a live swatch preview.",
)

with tool_form_panel("color_converter"):
    render_form_intro("Enter a color", "Accepts #rrggbb, rgb(r, g, b), or hsl(h, s%, l%).")
    with st.form("color-form"):
        color_input = st.text_input("Color", max_chars=MAX_INPUT_LENGTH, placeholder="#126bff")
        submitted = st.form_submit_button("Convert")

if submitted:
    # Stored in session_state (not rendered directly here) because the sidebar's
    # quick-search box, favorite-star buttons, and any other widget outside this
    # page's st.form trigger reruns of their own -- on those reruns `submitted` is
    # False again, which would otherwise collapse this whole results section the
    # instant any of them is touched.
    st.session_state["color_converter_result"] = parse_color(color_input)

result = st.session_state.get("color_converter_result")

if result is None:
    render_empty_state("Ready to convert", "HEX, RGB, and HSL forms appear here after you submit a color.")

if result is not None:
    with tool_result_panel("color_result", related_to="color_converter"):
        render_section_heading("Converted forms", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            swatch, fields = st.columns([1, 3])
            with swatch:
                st.markdown(
                    f'<div style="width:100%; aspect-ratio:1; border-radius:8px; '
                    f'border:1px solid var(--itops-surface-border); background:{result["hex"]};"></div>',
                    unsafe_allow_html=True,
                )
            with fields:
                st.text_input("HEX", value=result["hex"], disabled=True)
                st.text_input("RGB", value=result["rgb"], disabled=True)
                st.text_input("HSL", value=result["hsl"], disabled=True)
