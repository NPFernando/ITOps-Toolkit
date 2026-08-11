from __future__ import annotations

import streamlit as st

from utils.css_gradient_generator import MAX_STOPS, build_gradient
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="CSS Gradient Generator", layout="wide")
apply_app_shell(active_page="CSS Gradient Generator")


render_page_header(
    "CSS Gradient Generator",
    "Build a linear-gradient() or radial-gradient() CSS declaration from a list of hex color stops.",
)

with tool_form_panel("css_gradient_generator"):
    render_form_intro("Enter color stops", f"One per line: a hex color, optionally followed by a comma and a position (e.g. #ff0000, 25%). Up to {MAX_STOPS} stops.")
    with st.form("css-gradient-form"):
        stops_input = st.text_area("Color stops", height=180, placeholder="#ff0000, 0%\n#00ff00, 50%\n#0000ff, 100%")
        c1, c2 = st.columns(2)
        gradient_type = c1.radio("Type", ("linear", "radial"), horizontal=True)
        angle_or_shape = c2.text_input("Angle (linear) or shape (radial)", value="90deg", placeholder="90deg, or circle at center")
        submitted = st.form_submit_button("Generate")

if submitted:
    st.session_state["css_gradient_result"] = build_gradient(stops_input, gradient_type, angle_or_shape)

result = st.session_state.get("css_gradient_result")

if result is None:
    render_empty_state("Ready to generate", "The CSS gradient declaration appears here.")

if result is not None:
    with tool_result_panel("css_gradient_result_panel", related_to="css_gradient_generator"):
        render_section_heading("CSS", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["output"], language="css")
