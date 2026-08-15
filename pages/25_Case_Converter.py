from __future__ import annotations

import streamlit as st

from utils.case_tools import MAX_INPUT_LENGTH, convert_case
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Case Converter", layout="wide")
apply_app_shell(active_page="Case Converter")

st.markdown(
    """
    <style>
    @media (max-width: 768px) {
      div[data-testid="stTextInput"] input {
        font-size: 1rem;
      }
      div[data-testid="stTextArea"] textarea {
        font-size: 1rem;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


render_page_header(
    "Case Converter",
    "Convert text between slug-case, snake_case, camelCase, PascalCase, and Title Case.",
)

with tool_form_panel("case_converter"):
    render_form_intro("Enter text", "Words are detected from spaces, dashes, underscores, and camelCase boundaries.")
    with st.form("case-form"):
        text_input = st.text_area("Text", max_chars=MAX_INPUT_LENGTH, placeholder="helloWorld_fooBar", height=120)
        submitted = st.form_submit_button("Convert", use_container_width=True)
        st.caption("Keyboard tip: focus Convert and press Enter or Space to submit.")

if submitted:
    # Stored in session_state (not rendered directly here) because the sidebar's
    # quick-search box, favorite-star buttons, and any other widget outside this
    # page's st.form trigger reruns of their own -- on those reruns `submitted` is
    # False again, which would otherwise collapse this whole results section the
    # instant any of them is touched.
    st.session_state["case_converter_result"] = convert_case(text_input)

result = st.session_state.get("case_converter_result")

if result is None:
    render_empty_state("Ready to convert", "Every case variant appears here after you submit some text.")

if result is not None:
    with tool_result_panel("case_result", related_to="case_converter"):
        render_section_heading("Converted forms", eyebrow="Result")
        if not result["ok"]:
            render_status_note("Conversion unavailable", result["error"], tone="warning")
        else:
            render_status_note("Conversion complete", "All case variants are available below.", tone="success")
            st.text_input("slug-case", value=result["slug_case"], disabled=True)
            st.text_input("snake_case", value=result["snake_case"], disabled=True)
            st.text_input("SCREAMING_SNAKE_CASE", value=result["upper_snake_case"], disabled=True)
            st.text_input("camelCase", value=result["camel_case"], disabled=True)
            st.text_input("PascalCase", value=result["pascal_case"], disabled=True)
            st.text_input("Title Case", value=result["title_case"], disabled=True)
