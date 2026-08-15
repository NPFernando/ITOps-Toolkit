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


def generate_random_mac(locally_administered: bool, multicast: bool, seed_value: int | None = None) -> str:
    rng = random.Random(seed_value) if seed_value is not None else random.SystemRandom()
    octets = [rng.randrange(0, 256) for _ in range(6)]
    first = octets[0]
    first = (first | 0b10) if locally_administered else (first & 0b11111101)
    first = (first | 0b1) if multicast else (first & 0b11111110)
    octets[0] = first
    return ":".join(f"{item:02X}" for item in octets)


_baseline = start_page_baseline("Random MAC Address Generator")
st.set_page_config(page_title="Random MAC Address Generator", layout="wide")
apply_app_shell(active_page="Random MAC Address Generator")
mark_page_baseline(_baseline, "shell-ready")

render_page_header(
    "Random MAC Address Generator",
    "Generate a randomized MAC address with explicit local/global and unicast/multicast bit controls.",
)

with tool_form_panel("random_mac_generator"):
    render_form_intro("Set addressing bits", "Grouped toggles and one primary action improve mobile readability.")
    with st.form("random-mac-generator-form"):
        st.markdown('<div class="tool-panel-eyebrow">Addressing mode</div>', unsafe_allow_html=True)
        locally_administered = st.checkbox("Set locally administered bit", value=True)
        multicast = st.checkbox("Set multicast bit", value=False)
        st.markdown('<div class="tool-panel-eyebrow">Deterministic test seed</div>', unsafe_allow_html=True)
        seed_text = st.text_input("Optional integer seed", placeholder="Leave blank for secure random")
        submitted = st.form_submit_button("Generate MAC address", use_container_width=True)

if submitted:
    seed_raw = seed_text.strip()
    if seed_raw and not seed_raw.isdigit():
        st.session_state["random_mac_generator_result"] = {
            "ok": False,
            "error": "Seed must be an integer containing digits only.",
            "mac": "",
            "seeded": False,
        }
    else:
        seed_value = int(seed_raw) if seed_raw else None
        mac_value = generate_random_mac(locally_administered, multicast, seed_value=seed_value)
        st.session_state["random_mac_generator_result"] = {"ok": True, "error": "", "mac": mac_value, "seeded": seed_value is not None}

result = st.session_state.get("random_mac_generator_result")
if result is None:
    render_empty_state("Ready to generate", "A randomized MAC address appears here after submission.")
    render_status_note(
        "Awaiting MAC generation options",
        "Choose addressing bits, optionally provide a numeric seed, then select Generate MAC address.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("random_mac_result_panel", related_to="random_mac_generator"):
        render_section_heading("MAC output", eyebrow="Result")
        if not result["ok"]:
            render_status_note("Outcome: MAC input validation required", str(result["error"]), tone="warning")
        else:
            mode = "deterministic seed mode" if result["seeded"] else "secure random mode"
            render_status_note("Outcome: MAC address generated", f"Generated in {mode}.", tone="success")
            st.code(str(result["mac"]), language=None)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
