from __future__ import annotations

import streamlit as st

from utils.caa_record_builder import TAGS, build_caa_record
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


_baseline = start_page_baseline("CAA Record Builder")
st.set_page_config(page_title="CAA Record Builder", layout="wide")
apply_app_shell(active_page="CAA Record Builder")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "CAA Record Builder",
    "Build a DNS CAA (Certification Authority Authorization) record, restricting which CAs may issue certificates for a domain.",
)

with tool_form_panel("caa_record_builder"):
    render_form_intro("Choose a tag and value", "")
    with st.form("caa-record-builder-form"):
        tag = st.radio("Tag", TAGS)
        value = st.text_input("Value", placeholder="letsencrypt.org")
        critical = st.checkbox("Critical (unrecognized CAs must refuse to issue)")
        submitted = st.form_submit_button("Build record", use_container_width=True)

if submitted:
    st.session_state["caa_record_builder_result"] = build_caa_record(tag, value, critical)

result = st.session_state.get("caa_record_builder_result")

if result is None:
    render_empty_state("Ready to build", "The CAA record appears here.")
    render_status_note(
        "Awaiting CAA input",
        "Choose a CAA tag, enter a value, and build the record to generate output.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("caa_record_builder_result_panel", related_to="caa_record_builder"):
        render_section_heading("CAA record", eyebrow="Result")
        if not result["ok"]:
            render_status_note(
                "Cannot build CAA record yet",
                f"{result['error']} Provide a valid value for the selected tag and build the record again.",
                tone="warning",
            )
        else:
            render_status_note("CAA record ready", "The zone-file CAA record is ready below.", tone="success")
            st.code(result["zone_line"], language=None)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
