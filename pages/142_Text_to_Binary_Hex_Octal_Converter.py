from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.ui import (
    apply_app_shell,
    render_control_heading,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


def convert_text_radix(text: str) -> dict[str, str | bool]:
    raw = text or ""
    if not raw.strip():
        return {"ok": False, "error": "Enter text to convert.", "binary": "", "hex": "", "octal": ""}

    payload = raw.encode("utf-8")
    return {
        "ok": True,
        "error": "",
        "binary": " ".join(f"{byte:08b}" for byte in payload),
        "hex": " ".join(f"{byte:02X}" for byte in payload),
        "octal": " ".join(f"{byte:03o}" for byte in payload),
    }


_baseline = start_page_baseline("Text to Binary Hex Octal Converter")
st.set_page_config(page_title="Text to Binary Hex Octal Converter", layout="wide")
apply_app_shell(active_page="Text to Binary Hex Octal Converter")
mark_page_baseline(_baseline, "shell-ready")

render_page_header("Text to Binary Hex Octal Converter", "Convert plain text into binary, hexadecimal, and octal byte sequences.")

with tool_form_panel("text_to_binary_hex_octal_converter"):
    render_form_intro("Provide text input", "Use one full-width action to generate all encoded outputs for quick mobile copy/paste.")
    with st.form("text-to-binary-hex-octal-converter-form"):
        render_control_heading("Source text")
        input_text = st.text_area("Text input", height=180, placeholder="Hello", key="text_radix_input")
        submitted = st.form_submit_button("Convert text", use_container_width=True)

if submitted:
    st.session_state["text_radix_result"] = convert_text_radix(input_text)

result = st.session_state.get("text_radix_result")
with tool_result_panel("text_radix_result", related_to="text_to_binary_hex_octal_converter"):
    render_section_heading("Converted output", eyebrow="Result")
    if result is None:
        render_empty_state("Ready to encode", "Binary, hex, and octal output appears here after submission.")
        render_status_note("Outcome: conversion awaiting input", "Paste text, then choose Convert text.", tone="neutral")
    elif not bool(result["ok"]):
        render_status_note("Outcome: text conversion blocked", f"{result['error']} Provide plain text to continue.", tone="warning")
    else:
        render_status_note("Outcome: text conversion complete", "Binary, hex, and octal byte values are ready.", tone="success")
        st.code(f"Binary: {result['binary']}\nHex: {result['hex']}\nOctal: {result['octal']}", language=None)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
