from __future__ import annotations

import streamlit as st

from utils.robots_meta_builder import FOLLOWING, INDEXING, build_robots_meta
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Robots Meta Tag Builder", layout="wide")
apply_app_shell(active_page="Robots Meta Tag Builder")


render_page_header(
    "Robots Meta Tag Builder",
    'Build a <meta name="robots" content="..."> tag -- distinct from robots.txt, which applies site-wide.',
)

with tool_form_panel("robots_meta_builder"):
    render_form_intro("Choose directives", "")
    with st.form("robots-meta-form"):
        c1, c2 = st.columns(2)
        indexing = c1.radio("Indexing", INDEXING, horizontal=True)
        following = c2.radio("Following", FOLLOWING, horizontal=True)
        c3, c4, c5 = st.columns(3)
        noarchive = c3.checkbox("noarchive")
        nosnippet = c4.checkbox("nosnippet")
        noimageindex = c5.checkbox("noimageindex")
        c6, c7, c8 = st.columns(3)
        max_snippet = c6.number_input("max-snippet (blank = default)", value=None, min_value=-1, step=1)
        max_image_preview = c7.selectbox("max-image-preview", ("", "none", "standard", "large"))
        max_video_preview = c8.number_input("max-video-preview (blank = default)", value=None, min_value=-1, step=1)
        submitted = st.form_submit_button("Build tag")

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

if result is not None:
    with tool_result_panel("robots_meta_result_panel", related_to="robots_meta_builder"):
        render_section_heading("Meta tag", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["output"], language="html")
