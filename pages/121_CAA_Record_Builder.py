from __future__ import annotations

import streamlit as st

from utils.caa_record_builder import TAGS, build_caa_record
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


_baseline = start_page_baseline("CAA Record Builder")
st.set_page_config(page_title="CAA Record Builder", layout="wide")
apply_app_shell(active_page="CAA Record Builder")
mark_page_baseline(_baseline, "shell-ready")
mark_page_baseline(_baseline, "wave28-shell-mobile")


render_page_header(
    "CAA Record Builder",
    "Build a DNS CAA (Certification Authority Authorization) record, restricting which CAs may issue certificates for a domain.",
)

with tool_form_panel("caa_record_builder"):
    render_form_intro("Choose a tag and value", "Grouped controls and one full-width action keep CAA record setup ergonomic on mobile.")
    with st.form("caa-record-builder-form"):
        render_control_heading("Authorization settings")
        tag = st.radio("Tag", TAGS)
        render_control_heading("Record value")
        value = st.text_input("Value", placeholder="letsencrypt.org")
        render_control_heading("Validation behavior")
        critical = st.checkbox("Critical (unrecognized CAs must refuse to issue)")
        render_control_heading("Primary action")
        submitted = st.form_submit_button("Build record", use_container_width=True)

if submitted:
    st.session_state["caa_record_builder_result"] = build_caa_record(tag, value, critical)

result = st.session_state.get("caa_record_builder_result")

if result is None:
    render_empty_state("Ready to build", "The CAA record appears here.")
    render_status_note(
        "Outcome: CAA record builder ready",
        "No CAA record has been built yet. Choose a tag, enter a value, then select Build record to continue.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("caa_record_builder_result_panel", related_to="caa_record_builder"):
        render_section_heading("CAA record", eyebrow="Result")
        if not result["ok"]:
            render_status_note(
                "Outcome: CAA record build blocked",
                f"CAA record generation did not complete. {result['error']} Provide a valid value for the selected tag, then build again.",
                tone="warning",
            )
        else:
            render_status_note("Outcome: CAA record build complete", "The zone-file CAA record is ready below.", tone="success")
            st.code(result["zone_line"], language=None)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
