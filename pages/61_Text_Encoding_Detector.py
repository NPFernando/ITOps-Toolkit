from __future__ import annotations

import streamlit as st

from utils.encoding_tools import convert_to_utf8, detect_encoding
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Text Encoding Detector", layout="wide")
apply_app_shell(active_page="Text Encoding Detector")


render_page_header(
    "Text Encoding Detector",
    "Upload a text file to detect its character encoding, preview the decoded content, and convert it to UTF-8.",
)

with tool_form_panel("encoding_detector"):
    render_form_intro("Detect encoding", "Upload a text file.")
    with st.form("encoding-detector-form"):
        uploaded = st.file_uploader("File", key="encoding_detector_file")
        submitted = st.form_submit_button("Detect")

if submitted:
    if uploaded is None:
        st.session_state["encoding_detector_state"] = {"error": "Upload a file to detect its encoding.", "detected": None, "converted": None}
    else:
        data = uploaded.getvalue()
        st.session_state["encoding_detector_state"] = {
            "error": None,
            "detected": detect_encoding(data),
            "converted": convert_to_utf8(data),
        }

state = st.session_state.get("encoding_detector_state")

if state is None:
    render_empty_state("Ready to detect", "The detected encoding, confidence, and a decoded preview appear here after upload.")

if state is not None:
    with tool_result_panel("encoding_detector_result", related_to="encoding_detector"):
        render_section_heading("Detected encoding", eyebrow="Result")
        if state["error"] is not None:
            st.error(state["error"])
        elif not state["detected"]["ok"]:
            st.error(state["detected"]["error"])
        else:
            detected = state["detected"]
            c1, c2 = st.columns(2)
            c1.metric("Encoding", detected["encoding"])
            c2.metric("Confidence", f"{detected['confidence']}%")
            st.caption("Preview (first 500 characters):")
            st.code(detected["preview"])

            converted = state["converted"]
            if converted["ok"]:
                st.download_button(
                    "Download as UTF-8",
                    converted["utf8_text"].encode("utf-8"),
                    file_name="converted-utf8.txt",
                    mime="text/plain",
                )
