from __future__ import annotations

import streamlit as st

from utils.ui import (
    PROFESSIONS,
    TOOLS,
    apply_app_shell,
    favorite_tools,
    favorites_share_link,
    filter_tools,
    github_url,
    recent_or_popular_tools,
    render_feature_strip,
    render_home_hero,
    render_important_notice,
    render_tool_section,
    shared_favorite_tools,
    sort_tools,
)


st.set_page_config(page_title="ITOps Toolkit", page_icon=":material/build:", layout="wide")
apply_app_shell(active_page="Home")


repo_url = github_url()
if repo_url:
    _, action_col = st.columns([1, 0.14])
    with action_col:
        st.link_button("GitHub", repo_url, icon=":material/code:", width="stretch")

search_query = render_home_hero()

shared_favorites = shared_favorite_tools()
if shared_favorites:
    render_tool_section(shared_favorites, heading="Shared Favorites", section_id=None, key_prefix="shared")
    st.caption("Someone shared this list with you. It's separate from your own favorites below.")

favorites = favorite_tools()
if favorites:
    render_tool_section(favorites, heading="Favorites", section_id=None, key_prefix="fav", show_reorder=True)
    with st.popover("Share favorites", icon=":material/share:"):
        st.caption("Anyone with this link can view your current favorites list. It won't affect their own favorites.")
        st.code(favorites_share_link(favorites), language=None)

recent_param = st.query_params.get("recent", "")
recent_slugs = [slug for slug in recent_param.split(",") if slug]
recent_tools = recent_or_popular_tools(recent_slugs)
recents_heading = "Recently Used" if recent_slugs else "Popular Tools"
render_tool_section(recent_tools, heading=recents_heading, section_id=None, key_prefix="recent")

newest_tools = tuple(tool for tool in TOOLS if tool.is_new)
if newest_tools:
    render_tool_section(newest_tools, heading="Newest Tools", section_id=None, key_prefix="new")

profession = st.pills(
    "Filter by profession",
    options=("All", *PROFESSIONS),
    default="All",
    label_visibility="collapsed",
    key="home_profession_filter",
)
show_all_clicked = st.button("Show all tools", icon=":material/apps:")
if show_all_clicked:
    st.session_state["home_show_all"] = True
show_all = st.session_state.get("home_show_all", False) or bool(search_query.strip()) or profession != "All"

if show_all:
    if search_query.strip():
        all_heading = "Matching Tools"
    elif profession != "All":
        all_heading = f"{profession} Tools"
    else:
        all_heading = "All Tools"
    sort_mode_label = st.pills(
        "Sort",
        options=("Default", "A-Z", "Z-A"),
        default="Default",
        label_visibility="collapsed",
        key="home_sort_mode",
    )
    sort_mode = {"Default": "default", "A-Z": "az", "Z-A": "za"}[sort_mode_label]
    all_tools = sort_tools(filter_tools(search_query, profession), sort_mode)
    render_tool_section(all_tools, heading=all_heading, key_prefix="all")

render_feature_strip()
render_important_notice()
