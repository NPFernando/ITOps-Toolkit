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
    recent_tool_slugs,
    render_feature_strip,
    render_form_intro,
    render_fragment,
    render_control_heading,
    render_home_hero,
    render_important_notice,
    render_status_note,
    render_guided_workflows,
    render_tool_section,
    shared_favorite_tools,
    sort_tools,
    tool_form_panel,
)


_baseline = start_page_baseline("Home")
st.set_page_config(page_title="ITOps Toolkit", page_icon=":material/build:", layout="wide")
apply_app_shell(active_page="Home")
mark_page_baseline(_baseline, "shell-ready")
mark_page_baseline(_baseline, "wave27-shell-mobile")
mark_page_baseline(_baseline, "wave28-shell-mobile")


repo_url = github_url()
if repo_url:
    render_control_heading("Project")
    st.link_button("GitHub", repo_url, icon=":material/code:", width="stretch")

search_query = render_home_hero()

shared_favorites = shared_favorite_tools()
favorites = favorite_tools()
recent_slugs = list(recent_tool_slugs())
recent_tools = recent_or_popular_tools(recent_slugs)
newest_tools = tuple(tool for tool in TOOLS if tool.is_new)

if st.session_state.pop("home_force_quick_access", False):
    st.session_state["home_navigation_mode"] = "Quick access"

with tool_form_panel("home_navigation_controls"):
    render_form_intro("Choose how to browse tools", "Filter by profession and switch between quick access or full catalog.")
    render_control_heading("Filter by profession")
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

    render_control_heading("Navigation")
    navigation_mode = st.pills(
        "Home navigation",
        options=("Quick access", "All tools"),
        required=True,
        label_visibility="collapsed",
        key="home_navigation_mode",
    )

show_all_flag = st.session_state.get("home_show_all", False)
# `show_all` also factors in an active search/profession filter, which can
# already be expanding the section independently of the flag -- label and
# toggle off of this combined state (not the raw flag) so the button doesn't
# read "Show all tools" while the section is already expanded, and so
# clicking it while a filter is doing the showing doesn't set a flag that
# then outlives the filter (previously left the section stuck open after
# clearing the filter).
show_all = show_all_flag or bool(search_query.strip()) or profession != "All" or navigation_mode == "All tools"
button_label = "Hide all tools" if show_all else "Show all tools"
button_icon = ":material/expand_less:" if show_all else ":material/apps:"
with tool_form_panel("home_primary_action"):
    render_form_intro("Toggle catalog visibility", "Use a full-width action to expand or collapse the tool catalog.")
    render_control_heading("Catalog action")
    if st.button(button_label, icon=button_icon, use_container_width=True):
        if show_all and navigation_mode == "All tools" and not search_query.strip() and profession == "All":
            st.session_state["home_force_quick_access"] = True
            st.session_state["home_show_all"] = False
        else:
            st.session_state["home_show_all"] = not show_all
        st.rerun()

if show_all:
    filtered_tools = filter_tools(search_query, profession)
    if search_query.strip():
        all_heading = "Matching Tools"
    elif profession != "All":
        all_heading = f"{profession} Tools"
    else:
        all_heading = "All Tools"
    with tool_form_panel("home_sort_controls"):
        render_form_intro("Sort visible tools", "Choose how to order the tools currently shown.")
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
    all_tools = sort_tools(filtered_tools, sort_mode)
    if all_tools:
        render_status_note(
            "Outcome: full catalog visible",
            f"Showing {len(all_tools)} tool(s) in {all_heading}.",
            tone="success",
        )
    else:
        render_status_note(
            "Outcome: catalog filters need adjustment",
            "No tools matched the current search and profession filters. Adjust filters to continue.",
            tone="warning",
        )
    render_fragment(
        "home_all_tools",
        lambda: render_tool_section(
            all_tools,
            heading=all_heading,
            key_prefix="all",
            prefer_fragment_rerun=True,
        ),
    )
else:
    render_status_note(
        "Outcome: quick access ready",
        "Browse favorites, recents, and guided workflows, or expand to the full tool catalog.",
        tone="neutral",
    )
    searched_tools = filter_tools(search_query, profession) if search_query.strip() else ()
    quick_access_tools = sort_tools(filter_tools("", profession), "default")
    quick_access_slugs = {tool.slug for tool in quick_access_tools}

    def _scoped(items: tuple) -> tuple:
        matches = tuple(tool for tool in items if tool.slug in quick_access_slugs)
        if not search_query.strip():
            return matches
        searched = {tool.slug for tool in searched_tools}
        return tuple(tool for tool in matches if tool.slug in searched)

    render_control_heading("Quick access")
    render_fragment(
        "home_guided_workflows",
        lambda: render_guided_workflows(query=search_query, profession=profession),
    )
    if favorites:
        scoped_favorites = _scoped(favorites)
        if scoped_favorites:
            render_fragment(
                "home_favorites_tools",
                lambda: render_tool_section(
                    scoped_favorites,
                    heading="Your Favorites",
                    section_id=None,
                    key_prefix="fav",
                    show_reorder=True,
                    prefer_fragment_rerun=True,
                ),
            )
            with st.popover("Share favorites", icon=":material/share:"):
                st.caption("Anyone with this link can view your current favorites list. It won't affect their own favorites.")
                st.code(favorites_share_link(favorites), language=None)

    scoped_recent_tools = _scoped(recent_tools)
    if scoped_recent_tools:
        recents_heading = "Recently Used" if recent_slugs else "Popular to Start"
        render_fragment(
            "home_recent_tools",
            lambda: render_tool_section(
                scoped_recent_tools,
                heading=recents_heading,
                section_id=None,
                key_prefix="recent",
                prefer_fragment_rerun=True,
            ),
        )

    if shared_favorites:
        scoped_shared = _scoped(shared_favorites)
        if scoped_shared:
            render_fragment(
                "home_shared_favorites_tools",
                lambda: render_tool_section(
                    scoped_shared,
                    heading="Shared Favorites",
                    section_id=None,
                    key_prefix="shared",
                    prefer_fragment_rerun=True,
                ),
            )
            st.caption("Someone shared this list with you. It's separate from your own favorites.")

    if newest_tools:
        scoped_new = _scoped(newest_tools)
        if scoped_new:
            render_fragment(
                "home_new_tools",
                lambda: render_tool_section(
                    scoped_new,
                    heading="New & Noteworthy",
                    section_id=None,
                    key_prefix="new",
                    prefer_fragment_rerun=True,
                ),
            )

render_feature_strip()
render_important_notice()
mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
