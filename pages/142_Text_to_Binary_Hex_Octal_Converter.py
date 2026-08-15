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
mark_page_baseline(_baseline, "wave27-shell-mobile")
mark_page_baseline(_baseline, "wave29-shell-mobile")
mark_page_baseline(_baseline, "wave30-shell-mobile")
mark_page_baseline(_baseline, "wave31-shell-mobile")
mark_page_baseline(_baseline, "wave32-shell-mobile")
mark_page_baseline(_baseline, "wave33-shell-mobile")
mark_page_baseline(_baseline, "wave34-shell-mobile")
mark_page_baseline(_baseline, "wave35-shell-mobile")
mark_page_baseline(_baseline, "wave36-shell-mobile")
mark_page_baseline(_baseline, "wave37-shell-mobile")

render_page_header("Text to Binary Hex Octal Converter", "Convert plain text into binary, hexadecimal, and octal byte sequences.")

with tool_form_panel("text_to_binary_hex_octal_converter"):
    render_form_intro("Provide source text", "Keep source input and one full-width action together for fast mobile conversion.")
    render_section_heading(
        "Input setup",
        description="Enter source text, then run one action to produce all byte-format outputs.",
        eyebrow="Step 1",
        heading_level="h3",
    )
    with st.form("text-to-binary-hex-octal-converter-form"):
        render_control_heading("Source text")
        input_text = st.text_area("Text input", height=180, placeholder="Hello", key="text_radix_input")
        st.caption("Conversion uses UTF-8 bytes and updates all three outputs together for easier verification.")
        render_control_heading("Primary action")
        st.caption("Read order: enter source text, run convert, then confirm status and compare all three encoded outputs.")
        st.caption("If you're new, start with a short word first, then compare all three encodings.")
        submitted = st.form_submit_button("Convert text", use_container_width=True)

if submitted:
    st.session_state["text_radix_result"] = convert_text_radix(input_text)

result = st.session_state.get("text_radix_result")
with tool_result_panel("text_radix_result", related_to="text_to_binary_hex_octal_converter"):
    render_section_heading(
        "Encoded output",
        description="Scan binary, hexadecimal, and octal rows together for quick verification.",
        eyebrow="Step 2",
        heading_level="h3",
    )
    if result is None:
        render_empty_state("Ready to encode", "Binary, hex, and octal output appears here after submission.")
        render_status_note("Outcome: conversion awaiting input", "Paste source text, then choose Convert text.", tone="neutral")
    elif not bool(result["ok"]):
        render_status_note("Outcome: text conversion blocked", f"{result['error']} Add plain text and run conversion again.", tone="warning")
        st.caption("If you're new, start with a short word first, then compare all three encodings.")
    else:
        render_status_note(
            "Outcome: text conversion complete",
            "UTF-8 byte values in binary, hexadecimal, and octal are ready.",
            tone="success",
        )
        st.caption("Tip: compare the same byte order across binary, hex, and octal for easier checks.")
        st.code(f"Binary: {result['binary']}\nHex: {result['hex']}\nOctal: {result['octal']}", language=None)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
