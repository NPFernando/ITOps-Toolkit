from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.robots_meta_builder import FOLLOWING, INDEXING, build_robots_meta
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_failure_note,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


_baseline = start_page_baseline("Robots Meta Tag Builder")
st.set_page_config(page_title="Robots Meta Tag Builder", layout="wide")
apply_app_shell(active_page="Robots Meta Tag Builder")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "Robots Meta Tag Builder",
    'Build a <meta name="robots" content="..."> tag -- distinct from robots.txt, which applies site-wide.',
)

with tool_form_panel("robots_meta_builder"):
    render_form_intro("Choose directives", "")
    with st.form("robots-meta-form"):
        indexing = st.radio("Indexing", INDEXING, horizontal=False)
        following = st.radio("Following", FOLLOWING, horizontal=False)
        noarchive = st.checkbox("noarchive")
        nosnippet = st.checkbox("nosnippet")
        noimageindex = st.checkbox("noimageindex")
        max_snippet = st.number_input("max-snippet (blank = default)", value=None, min_value=-1, step=1)
        max_image_preview = st.selectbox("max-image-preview", ("", "none", "standard", "large"))
        max_video_preview = st.number_input("max-video-preview (blank = default)", value=None, min_value=-1, step=1)
        submitted = st.form_submit_button("Build tag", use_container_width=True)

if submitted:
    st.session_state["robots_meta_result"] = build_robots_meta(
        indexing, following, noarchive, nosnippet, noimageindex,
        int(max_snippet) if max_snippet is not None else None,
        max_image_preview,
        int(max_video_preview) if max_video_preview is not None else None,
    )

result = st.session_state.get("robots_meta_result")

if result is None:
    render_empty_state("Ready to build", "The meta tag appears here.")
    render_status_note("Awaiting directives", "Choose robots directives and select Build tag.", tone="neutral")

if result is not None:
    with tool_result_panel("robots_meta_result_panel", related_to="robots_meta_builder"):
        render_section_heading("Meta tag", eyebrow="Result")
        if not result["ok"]:
            render_failure_note(
                "Meta tag generation",
                result["error"],
                remediation="Adjust directives and retry the build.",
            )
        else:
            render_status_note("Meta tag ready", "The generated robots meta tag is ready to copy.", tone="success")
            st.code(result["output"], language="html")

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
