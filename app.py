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

st.markdown('<div class="tool-panel-eyebrow">Filter by profession</div>', unsafe_allow_html=True)
profession = st.pills(
    "Filter by profession",
    options=("All", *PROFESSIONS),
    default="All",
    label_visibility="collapsed",
    key="home_profession_filter",
)

show_all_flag = st.session_state.get("home_show_all", False)
# `show_all` also factors in an active search/profession filter, which can
# already be expanding the section independently of the flag -- label and
# toggle off of this combined state (not the raw flag) so the button doesn't
# read "Show all tools" while the section is already expanded, and so
# clicking it while a filter is doing the showing doesn't set a flag that
# then outlives the filter (previously left the section stuck open after
# clearing the filter).
show_all = show_all_flag or bool(search_query.strip()) or profession != "All"
button_label = "Hide all tools" if show_all else "Show all tools"
button_icon = ":material/expand_less:" if show_all else ":material/apps:"
if st.button(button_label, icon=button_icon):
    st.session_state["home_show_all"] = not show_all
    st.rerun()

if show_all:
    if search_query.strip():
        all_heading = "Matching Tools"
    elif profession != "All":
        all_heading = f"{profession} Tools"
    else:
        all_heading = "All Tools"
    st.markdown('<div class="tool-panel-eyebrow">Sort</div>', unsafe_allow_html=True)
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
