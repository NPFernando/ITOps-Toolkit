from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
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
    render_form_intro,
    render_fragment,
    render_control_heading,
    render_home_hero,
    render_important_notice,
    render_section_heading,
    render_status_note,
    render_guided_workflows,
    render_tool_section,
    shared_favorite_tools,
    sort_tools,
)


_baseline = start_page_baseline("Home")
st.set_page_config(page_title="ITOps Toolkit", page_icon=":material/build:", layout="wide")
apply_app_shell(active_page="Home")
mark_page_baseline(_baseline, "shell-ready")
mark_page_baseline(_baseline, "wave27-shell-mobile")
mark_page_baseline(_baseline, "wave28-shell-mobile")
mark_page_baseline(_baseline, "wave29-shell-mobile")
mark_page_baseline(_baseline, "wave30-shell-mobile")
mark_page_baseline(_baseline, "wave31-shell-mobile")
mark_page_baseline(_baseline, "wave32-shell-mobile")
mark_page_baseline(_baseline, "wave33-shell-mobile")
mark_page_baseline(_baseline, "wave34-shell-mobile")
mark_page_baseline(_baseline, "wave35-shell-mobile")
mark_page_baseline(_baseline, "wave36-shell-mobile")
mark_page_baseline(_baseline, "wave37-shell-mobile")
mark_page_baseline(_baseline, "wave38-shell-mobile")
mark_page_baseline(_baseline, "wave39-shell-mobile")
mark_page_baseline(_baseline, "wave40-shell-mobile")
mark_page_baseline(_baseline, "wave41-shell-mobile")
mark_page_baseline(_baseline, "wave42-shell-mobile")
mark_page_baseline(_baseline, "wave43-shell-mobile")
mark_page_baseline(_baseline, "wave44-shell-mobile")
mark_page_baseline(_baseline, "wave45-shell-mobile")
mark_page_baseline(_baseline, "wave46-shell-mobile")
mark_page_baseline(_baseline, "wave47-shell-mobile")
mark_page_baseline(_baseline, "wave48-shell-mobile")
mark_page_baseline(_baseline, "wave49-shell-mobile")
mark_page_baseline(_baseline, "wave50-shell-mobile")


repo_url = github_url()
if repo_url:
    render_control_heading("Project")
    st.link_button("GitHub", repo_url, icon=":material/code:", width="stretch")

search_query = render_home_hero()

shared_favorites = shared_favorite_tools()
if shared_favorites:
    render_tool_section(shared_favorites, heading="Shared Favorites", section_id=None, key_prefix="shared")
    st.caption("Someone shared this list with you. It's separate from your own favorites below.")

favorites = favorite_tools()
if favorites:
    render_tool_section(favorites, heading="Favorites", section_id=None, key_prefix="fav")
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
    required=True,  # without this, clicking the already-selected pill deselects it to
    # None (documented st.pills behavior with required=False) -- profession != "All"
    # then evaluates True for None, so show_all sticks and the heading renders the
    # literal string "None Tools" instead of "All Tools". Same bug class as PR #63.
    label_visibility="collapsed",
    key="home_profession_filter",
)

show_all_flag = st.session_state.get("home_show_all", False)
button_label = "Hide all tools" if show_all_flag else "Show all tools"
button_icon = ":material/expand_less:" if show_all_flag else ":material/apps:"
if st.button(button_label, icon=button_icon):
    st.session_state["home_show_all"] = not show_all_flag
    st.rerun()
show_all = st.session_state.get("home_show_all", False) or bool(search_query.strip()) or profession != "All"

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
        required=True,  # without this, clicking the already-selected pill deselects it
        # to None, which would then KeyError on the dict lookup below and crash the
        # whole home page. Same bug class as PR #63.
        label_visibility="collapsed",
        key="home_sort_mode",
    )
    sort_mode = {"Default": "default", "A-Z": "az", "Z-A": "za"}[sort_mode_label]
    all_tools = sort_tools(filter_tools(search_query, profession), sort_mode)
    render_tool_section(all_tools, heading=all_heading, key_prefix="all")

render_feature_strip()
render_important_notice()
mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
