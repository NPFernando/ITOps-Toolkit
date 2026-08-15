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


MAX_RANGE_SIZE = 4096


def _expand_cidr(cidr_text: str) -> dict[str, object]:
    text = (cidr_text or "").strip()
    if not text:
        return {"ok": False, "error": "Enter an IPv4 CIDR (example: 10.0.0.0/30).", "addresses": []}
    try:
        network = ipaddress.IPv4Network(text, strict=False)
    except ValueError:
        return {"ok": False, "error": "Enter a valid IPv4 CIDR range.", "addresses": []}
    if network.num_addresses > MAX_RANGE_SIZE:
        return {"ok": False, "error": f"Range too large. Limit to {MAX_RANGE_SIZE} addresses or fewer.", "addresses": []}
    return {"ok": True, "error": "", "addresses": [str(ip) for ip in network]}


def _expand_start_end(start_text: str, end_text: str) -> dict[str, object]:
    start_raw = (start_text or "").strip()
    end_raw = (end_text or "").strip()
    if not start_raw or not end_raw:
        return {"ok": False, "error": "Enter both start and end IPv4 addresses.", "addresses": []}
    try:
        start_ip = ipaddress.IPv4Address(start_raw)
        end_ip = ipaddress.IPv4Address(end_raw)
    except ipaddress.AddressValueError:
        return {"ok": False, "error": "Enter valid IPv4 addresses for start and end.", "addresses": []}
    if int(end_ip) < int(start_ip):
        return {"ok": False, "error": "End IPv4 address must be greater than or equal to start.", "addresses": []}
    count = int(end_ip) - int(start_ip) + 1
    if count > MAX_RANGE_SIZE:
        return {"ok": False, "error": f"Range too large. Limit to {MAX_RANGE_SIZE} addresses or fewer.", "addresses": []}
    return {
        "ok": True,
        "error": "",
        "addresses": [str(ipaddress.IPv4Address(value)) for value in range(int(start_ip), int(end_ip) + 1)],
    }


def expand_range(mode: str, cidr_text: str, start_text: str, end_text: str) -> dict[str, object]:
    if mode == "CIDR":
        return _expand_cidr(cidr_text)
    return _expand_start_end(start_text, end_text)


_baseline = start_page_baseline("IPv4 Range Expander")
st.set_page_config(page_title="IPv4 Range Expander", layout="wide")
apply_app_shell(active_page="IPv4 Range Expander")
mark_page_baseline(_baseline, "shell-ready")

render_page_header("IPv4 Range Expander", "Expand IPv4 CIDR blocks or start/end ranges into explicit host lists.")

with tool_form_panel("ipv4_range_expander"):
    render_form_intro("Choose expansion mode", "Grouped input sections and one full-width action support small-screen operations.")
    with st.form("ipv4-range-expander-form"):
        st.markdown('<div class="tool-panel-eyebrow">Expansion mode</div>', unsafe_allow_html=True)
        mode = st.selectbox("Mode", options=("CIDR", "Start + End"))
        st.markdown('<div class="tool-panel-eyebrow">Range input</div>', unsafe_allow_html=True)
        cidr_input = st.text_input("CIDR input", placeholder="10.0.0.0/30", disabled=mode != "CIDR")
        start_input = st.text_input("Start IPv4", placeholder="10.0.0.1", disabled=mode != "Start + End")
        end_input = st.text_input("End IPv4", placeholder="10.0.0.5", disabled=mode != "Start + End")
        submitted = st.form_submit_button("Expand IPv4 range", use_container_width=True)

if submitted:
    st.session_state["ipv4_range_expander_result"] = expand_range(mode, cidr_input, start_input, end_input)

result = st.session_state.get("ipv4_range_expander_result")
if result is None:
    render_empty_state("Ready to expand", "Expanded IPv4 addresses appear here after submission.")
    render_status_note(
        "Outcome: awaiting IPv4 range expansion",
        f"Choose CIDR or Start + End mode, then submit. Maximum expansion is {MAX_RANGE_SIZE} addresses.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("ipv4_range_expander_result_panel", related_to="ipv4_range_expander"):
        render_section_heading("Expanded addresses", eyebrow="Result")
        if not result["ok"]:
            render_status_note("Outcome: IPv4 range expansion blocked", str(result["error"]), tone="warning")
        else:
            addresses = result["addresses"]
            render_status_note("Outcome: IPv4 range expansion complete", f"Expanded {len(addresses)} address(es).", tone="success")
            st.code("\n".join(str(item) for item in addresses), language=None)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
