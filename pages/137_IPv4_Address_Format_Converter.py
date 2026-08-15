from __future__ import annotations

import ipaddress

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
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


def _ipv4_to_formats(address_text: str) -> dict[str, object]:
    text = (address_text or "").strip()
    if not text:
        return {"ok": False, "error": "Enter an IPv4 address.", "data": {}}
    try:
        ip = ipaddress.IPv4Address(text)
    except ipaddress.AddressValueError:
        return {"ok": False, "error": "Enter a valid IPv4 address in dotted-decimal format.", "data": {}}

    value = int(ip)
    return {
        "ok": True,
        "error": "",
        "data": {
            "Dotted decimal": str(ip),
            "Integer": str(value),
            "Hex": f"0x{value:08X}",
            "Binary": f"{value:032b}",
        },
    }


def _integer_to_ipv4(integer_text: str) -> dict[str, object]:
    text = (integer_text or "").strip()
    if not text:
        return {"ok": False, "error": "Enter an IPv4 integer value.", "data": {}}
    if not text.isdigit():
        return {"ok": False, "error": "IPv4 integer value must contain digits only.", "data": {}}
    value = int(text)
    if value < 0 or value > 0xFFFFFFFF:
        return {"ok": False, "error": "IPv4 integer value must be between 0 and 4294967295.", "data": {}}
    ip = ipaddress.IPv4Address(value)
    return {"ok": True, "error": "", "data": {"Dotted decimal": str(ip), "Integer": str(value)}}


def convert_ipv4_address(mode: str, raw_value: str) -> dict[str, object]:
    if mode == "IPv4 to other formats":
        return _ipv4_to_formats(raw_value)
    return _integer_to_ipv4(raw_value)


_baseline = start_page_baseline("IPv4 Address Format Converter")
st.set_page_config(page_title="IPv4 Address Format Converter", layout="wide")
apply_app_shell(active_page="IPv4 Address Format Converter")
mark_page_baseline(_baseline, "shell-ready")

render_page_header("IPv4 Address Format Converter", "Convert IPv4 values between dotted decimal, integer, hexadecimal, and binary forms.")

with tool_form_panel("ipv4_format_converter"):
    render_form_intro("Choose conversion mode", "Grouped controls and one full-width action improve quick mobile conversion tasks.")
    with st.form("ipv4-format-converter-form"):
        st.markdown('<div class="tool-panel-eyebrow">Conversion mode</div>', unsafe_allow_html=True)
        mode = st.selectbox("Mode", options=("IPv4 to other formats", "Integer to IPv4"))
        st.markdown('<div class="tool-panel-eyebrow">Input value</div>', unsafe_allow_html=True)
        placeholder = "192.168.10.25" if mode == "IPv4 to other formats" else "3232238105"
        input_value = st.text_input("IPv4 input", placeholder=placeholder)
        submitted = st.form_submit_button("Convert IPv4 value", use_container_width=True)

if submitted:
    st.session_state["ipv4_format_converter_result"] = convert_ipv4_address(mode, input_value)

result = st.session_state.get("ipv4_format_converter_result")
if result is None:
    render_empty_state("Ready to convert", "Converted IPv4 output appears here after submission.")
    render_status_note(
        "Outcome: awaiting IPv4 conversion",
        "Select conversion mode, provide input, then choose Convert IPv4 value.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("ipv4_format_converter_result_panel", related_to="ipv4_format_converter"):
        render_section_heading("Converted IPv4 values", eyebrow="Result")
        if not result["ok"]:
            render_status_note("Outcome: IPv4 conversion blocked", str(result["error"]), tone="warning")
        else:
            render_status_note("Outcome: IPv4 conversion complete", "Use any output format needed for tooling or runbooks.", tone="success")
            st.code("\n".join(f"{k}: {v}" for k, v in result["data"].items()), language=None)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
