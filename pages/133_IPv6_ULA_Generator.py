from __future__ import annotations

import random

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


def generate_ula_prefix(seed_value: int | None = None) -> str:
    rng = random.Random(seed_value) if seed_value is not None else random.SystemRandom()
    global_id = rng.getrandbits(40)
    high = (global_id >> 24) & 0xFFFF
    mid = (global_id >> 8) & 0xFFFF
    low = ((global_id & 0xFF) << 8) & 0xFFFF
    return f"fd{high:04x}:{mid:04x}:{low:04x}::/48"


def derive_subnet(prefix: str, subnet_id: int) -> str:
    root = prefix.split("::", 1)[0]
    return f"{root}:{subnet_id:04x}::/64"


_baseline = start_page_baseline("IPv6 ULA Generator")
st.set_page_config(page_title="IPv6 ULA Generator", layout="wide")
apply_app_shell(active_page="IPv6 ULA Generator")
mark_page_baseline(_baseline, "shell-ready")

render_page_header(
    "IPv6 ULA Generator",
    "Generate a Unique Local Address prefix (fd00::/8) and preview deterministic /64 subnets.",
)

with tool_form_panel("ipv6_ula_generator"):
    render_form_intro("Choose optional seed and subnet preview", "Use a seed for deterministic output during runbooks or testing.")
    with st.form("ipv6-ula-generator-form"):
        st.markdown('<div class="tool-panel-eyebrow">Generation seed</div>', unsafe_allow_html=True)
        seed_text = st.text_input("Optional integer seed", placeholder="Leave blank for secure random")
        st.markdown('<div class="tool-panel-eyebrow">Subnet preview</div>', unsafe_allow_html=True)
        subnet_count = st.slider("How many /64 subnets to preview", 1, 8, 4)
        submitted = st.form_submit_button("Generate ULA prefix", use_container_width=True)

if submitted:
    seed_raw = seed_text.strip()
    if seed_raw and not seed_raw.isdigit():
        st.session_state["ipv6_ula_result"] = {
            "ok": False,
            "error": "Seed must be an integer containing digits only.",
            "prefix": "",
            "subnets": [],
            "seeded": False,
        }
    else:
        seed_value = int(seed_raw) if seed_raw else None
        prefix = generate_ula_prefix(seed_value)
        subnets = [derive_subnet(prefix, index) for index in range(subnet_count)]
        st.session_state["ipv6_ula_result"] = {"ok": True, "error": "", "prefix": prefix, "subnets": subnets, "seeded": seed_value is not None}

result = st.session_state.get("ipv6_ula_result")
if result is None:
    render_empty_state("Ready to generate", "Your ULA /48 prefix and /64 subnet preview appear here.")
    render_status_note(
        "Awaiting generation input",
        "Optionally provide a numeric seed, choose subnet preview size, then select Generate ULA prefix.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("ipv6_ula_result_panel", related_to="ipv6_ula_generator"):
        render_section_heading("ULA output", eyebrow="Result")
        if not result["ok"]:
            render_status_note("Outcome: ULA input validation required", str(result["error"]), tone="warning")
        else:
            mode = "deterministic seed mode" if result["seeded"] else "secure random mode"
            render_status_note("Outcome: ULA prefix generated", f"Generated in {mode}.", tone="success")
            st.code(str(result["prefix"]), language=None)
            st.markdown("**Suggested /64 subnets**")
            st.code("\n".join(result["subnets"]), language=None)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
