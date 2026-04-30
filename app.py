from __future__ import annotations

import streamlit as st

from utils.ui import (
    apply_app_shell,
    filter_tools,
    github_url,
    render_feature_strip,
    render_home_hero,
    render_important_notice,
    render_tool_section,
)


st.set_page_config(page_title="ITOps Toolkit", page_icon=":material/build:", layout="wide")
apply_app_shell(active_page="Home")


repo_url = github_url()
if repo_url:
    _, action_col = st.columns([1, 0.14])
    with action_col:
        st.link_button("GitHub", repo_url, icon=":material/code:", width="stretch")

search_query = render_home_hero()
render_tool_section(filter_tools(search_query), query=search_query)
render_feature_strip()
render_important_notice()
