from __future__ import annotations

from html import escape
from datetime import datetime, timezone

import streamlit as st

from utils import roadmap
from utils.ai_tools import optional_ai_configured, summarize_feature_requests_with_azure
from utils.cache_policy import (
    ROADMAP_AI_TRIAGE_CACHE_TTL_SECONDS,
    ROADMAP_BOARD_CACHE_TTL_SECONDS,
    cache_freshness_message,
    compose_cache_key,
    runtime_cache_scope,
)
from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.ui import (
    apply_app_shell,
    render_control_heading,
    render_failure_note,
    render_form_intro,
    render_section_heading,
    render_status_note,
    roadmap_badge_icon_html,
    tool_form_panel,
)


_baseline = start_page_baseline("Roadmap & Feedback")
st.set_page_config(page_title="Roadmap & Feedback", page_icon=":material/route:", layout="wide")
apply_app_shell(active_page="Roadmap & Feedback")
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


def _status_tone(status: str) -> str:
    return {
        "Planned": "planned",
        "In Progress": "progress",
        "Complete": "done",
        "AI Recommended": "ai",
    }.get(status, "planned")


def _status_icon_key(status: str) -> str:
    return {
        "Planned": "status_planned",
        "In Progress": "status_progress",
        "Complete": "status_done",
        "AI Recommended": "status_ai",
    }.get(status, "status_planned")


def _board_card(label: str, count: int) -> str:
    return (
        '<div class="roadmap-board-card">'
        f"<span>{escape(label)}</span>"
        f"<strong>{count}</strong>"
        "</div>"
    )


def _roadmap_card(item: roadmap.RoadmapItem) -> str:
    tone = _status_tone(item.status)
    title_html = escape(item.title)
    if item.url:
        title_html = f'<a href="{escape(item.url)}" target="_blank" rel="noopener noreferrer">{title_html}</a>'
    source_label = "Seed"
    source_icon = "source_seed"
    if item.source == "github":
        source_label = f"GitHub #{item.number}" if item.number else "GitHub"
        source_icon = "source_github"
    return (
        f'<article class="roadmap-item-card roadmap-item-{tone}">'
        f'<div class="roadmap-vote-pill"><span>^</span>{item.votes}</div>'
        '<div class="roadmap-item-body">'
        f'<div class="roadmap-card-title">{title_html}</div>'
        '<div class="roadmap-card-meta">'
        f'<span class="roadmap-item-category">{escape(item.category)}</span>'
        f'<span class="roadmap-status-badge">{roadmap_badge_icon_html(_status_icon_key(item.status), "•")}{escape(item.status)}</span>'
        f'<span class="roadmap-source-badge roadmap-source-{escape(item.source)}">{roadmap_badge_icon_html(source_icon, "•")}{escape(source_label)}</span>'
        "</div>"
        f"<p>{escape(item.description)}</p>"
        f"<small>{escape(item.rationale)}</small>"
        "</div>"
        "</article>"
    )


def _empty_column() -> str:
    return (
        '<div class="roadmap-empty-column">'
        "<strong>No matches</strong>"
        "<p>Try another search or category filter.</p>"
        "</div>"
    )


def _roadmap_column(status: str, status_items: tuple[roadmap.RoadmapItem, ...]) -> str:
    cards = "".join(_roadmap_card(item) for item in status_items) or _empty_column()
    return (
        f'<section class="roadmap-column roadmap-column-{_status_tone(status)}">'
        '<div class="roadmap-column-title">'
        '<span class="roadmap-status-dot"></span>'
        f'<div class="roadmap-column-name">{escape(status)}</div>'
        f"<strong>{len(status_items)}</strong>"
        "</div>"
        f'<div class="roadmap-column-list">{cards}</div>'
        "</section>"
    )


@st.cache_data(ttl=ROADMAP_BOARD_CACHE_TTL_SECONDS, show_spinner=False)
def _cached_roadmap_board(_cache_key: str, repo_url: str) -> dict:
    return {
        "board": roadmap.load_roadmap_board(repo_url=repo_url),
        "cached_at": datetime.now(timezone.utc).isoformat(),
    }


@st.cache_data(ttl=ROADMAP_AI_TRIAGE_CACHE_TTL_SECONDS, show_spinner=False)
def _cached_triage_summary(_cache_key: str, open_items: tuple[roadmap.RoadmapItem, ...]) -> dict:
    """Cached for an hour so repeated clicks (by any visitor) reuse one AI call
    per hour rather than paying for the same summary over and over."""
    return {
        "triage": summarize_feature_requests_with_azure(list(open_items)),
        "cached_at": datetime.now(timezone.utc).isoformat(),
    }


feedback_url = roadmap.github_feature_request_url()
repo_url = roadmap.github_repository_url()
board_cache_key = compose_cache_key(
    "roadmap-board",
    repo_url=repo_url,
    scope=runtime_cache_scope(),
)
board_payload = _cached_roadmap_board(board_cache_key, repo_url)
board = board_payload["board"]

st.markdown(
    f"""
    <section class="roadmap-hero">
        <div>
            <div class="roadmap-kicker">Public roadmap</div>
            <h1>Roadmap & Feedback</h1>
            <p>Track curated roadmap items and public GitHub feature requests from the ITOps Toolkit repository.</p>
            <div class="roadmap-tab-row">
                <span class="roadmap-tab-active">Roadmap</span>
                <a href="{escape(feedback_url)}" target="_blank" rel="noopener noreferrer">Feedback via GitHub</a>
            </div>
        </div>
        <div class="roadmap-actions">
            <a class="roadmap-submit-link" href="{escape(feedback_url)}" target="_blank" rel="noopener noreferrer">Submit idea</a>
            <a class="roadmap-secondary-link" href="{escape(repo_url)}" target="_blank" rel="noopener noreferrer">View GitHub</a>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

render_status_note(
    "Outcome: public feedback safety reminder",
    "Submit ideas through public GitHub Issues only. Do not include secrets, internal hostnames, customer logs, tokens, keys, or private data.",
    tone="warning",
)
render_status_note(
    "Outcome: AI Recommended label clarified",
    "The \"AI Recommended\" status is a static curated tag, not generated AI output. Optional AI triage runs only when explicitly requested.",
    tone="neutral",
)
board_freshness_tone, board_freshness = cache_freshness_message(
    "Roadmap board",
    board_payload["cached_at"],
    ROADMAP_BOARD_CACHE_TTL_SECONDS,
)
render_status_note("Outcome: roadmap cache checked", board_freshness, tone=board_freshness_tone)

if board.github_error:
    render_failure_note(
        "GitHub roadmap sync",
        board.github_error,
        remediation="The seed roadmap is already loaded. Refresh later to retry GitHub issue sync.",
    )
else:
    render_status_note(
        "Outcome: roadmap sync complete",
        "Seed roadmap items and public GitHub issues are loaded into this board view.",
        tone="success",
    )

counts = roadmap.category_counts(board.items)
st.markdown('<div class="roadmap-section-label">Boards</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="roadmap-board-grid">'
    + "".join(_board_card(label, count) for label, count in counts.items())
    + "</div>",
    unsafe_allow_html=True,
)

render_section_heading("Browse roadmap items", "Use search and category filters to focus the board view.", eyebrow="Explore")
with tool_form_panel("roadmap_filters"):
    render_form_intro("Search and filter roadmap", "Use keyword search and category pills to narrow the board.")
    render_section_heading(
        "Filter setup",
        description="Set search terms and category scope first so roadmap results are easier to scan.",
        eyebrow="Step 1",
        heading_level="h3",
    )
    with st.form("roadmap-filters-form"):
        render_control_heading("Keyword search")
        query = st.text_input("Search roadmap", placeholder="Search features, categories, or ideas...")
        render_control_heading("Category filter")
        category = st.pills(
            "Filter category",
            options=("All", *roadmap.roadmap_categories()),
            default="All",
            required=True,  # without this, clicking the already-selected pill deselects it
            # to None (documented st.pills behavior with required=False). Already safely
            # coerced by `category or "All"` below, but fixed at the source anyway --
            # same bug class as PR #63.
            label_visibility="collapsed",
        )
        st.caption("Search first, then narrow with category pills to keep the board readable on mobile screens.")
        render_control_heading("Apply filters")
        st.caption("Read order: set search + category, apply filters, then review status outcomes before scanning cards.")
        submitted_filters = st.form_submit_button("Apply filters", use_container_width=True)

if submitted_filters or "roadmap_filter_state" not in st.session_state:
    st.session_state["roadmap_filter_state"] = {
        "query": query,
        "category": category or "All",
    }

query_state = st.session_state.get("roadmap_filter_state", {}).get("query", "")
selected_category = st.session_state.get("roadmap_filter_state", {}).get("category", "All")
filtered_items = roadmap.filter_roadmap_items(query_state, selected_category, board.items)
items_by_status = roadmap.roadmap_items_by_status(filtered_items)

render_section_heading(
    "Roadmap results",
    description="Review status outcomes first, then scan grouped columns for matching roadmap cards.",
    eyebrow="Step 2",
    heading_level="h3",
)
st.caption("If you're new, begin with Planned and In Progress columns before opening issue links.")

if not filtered_items:
    render_status_note(
        "Outcome: roadmap filters need adjustment",
        "No roadmap items matched the active search and category filters. Change filters to continue.",
        tone="warning",
    )
    st.caption("If you're new, clear all filters, then add search or category one step at a time.")
elif query_state.strip() or selected_category != "All":
    render_status_note(
        "Outcome: roadmap filters applied",
        f"Showing {len(filtered_items)} roadmap item(s) that match the active filters.",
        tone="success",
    )
    st.caption("New to roadmap review? Start with In Progress cards, then scan Planned and Complete.")
else:
    render_status_note(
        "Outcome: roadmap board ready",
        f"Showing all {len(filtered_items)} roadmap item(s). Apply search and category filters to narrow the board.",
        tone="neutral",
    )
    st.caption("If you're new, begin with Planned and In Progress columns before opening issue links.")

st.markdown(
    f"""
    <div class="roadmap-summary-line">
        <strong>{len(filtered_items)} roadmap items shown</strong>
        <span>Seed items are merged with public GitHub Issues; Streamlit does not store feedback.</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="roadmap-columns-grid">'
    + "".join(_roadmap_column(status, items_by_status[status]) for status in roadmap.ROADMAP_STATUSES)
    + "</div>",
    unsafe_allow_html=True,
)

render_section_heading(
    "AI-assisted triage",
    "Summarize open (not-yet-Complete) roadmap items into a short, maintainer-facing prioritization -- opt-in, and only sends public roadmap data (titles, descriptions, vote counts) already shown above.",
    eyebrow="Optional",
)
open_items = [item for item in board.items if item.status != "Complete"]
ai_available = optional_ai_configured()
if not ai_available:
    render_status_note(
        "Outcome: AI triage unavailable",
        "Configure Azure OpenAI settings to enable this. The roadmap board above works the same either way.",
        tone="neutral",
    )
elif not open_items:
    render_status_note("Outcome: no open roadmap items", "All roadmap items are currently marked Complete.", tone="neutral")
else:
    with tool_form_panel("roadmap_ai_triage_action"):
        render_form_intro(
            "Generate optional AI triage",
            "Runs only when clicked and uses public roadmap item text already shown on this page.",
        )
        render_section_heading("Optional triage", eyebrow="Step 2", heading_level="h3")
        render_control_heading("Triage action")
        st.caption("Use this after filtering so the summary reflects the items you are actively reviewing.")
        summarize_with_ai = st.button(f"Summarize {len(open_items)} open items with AI", icon=":material/auto_awesome:", use_container_width=True)
    if summarize_with_ai:
        triage_cache_key = compose_cache_key(
            "roadmap-ai-triage",
            open_items=open_items,
            scope=runtime_cache_scope(),
        )
        with st.spinner("Generating triage summary..."):
            triage_payload = _cached_triage_summary(triage_cache_key, tuple(open_items))
        triage = triage_payload["triage"]
        triage_tone, triage_freshness = cache_freshness_message(
            "AI triage summary",
            triage_payload["cached_at"],
            ROADMAP_AI_TRIAGE_CACHE_TTL_SECONDS,
        )
        render_status_note("Outcome: AI triage cache checked", triage_freshness, tone=triage_tone)
        if triage.get("enabled"):
            render_status_note(
                "Outcome: AI triage generated",
                "AI prioritization summary is available below for maintainer review.",
                tone="success",
            )
            render_status_note("Outcome: AI triage summary ready", triage["summary"], tone="neutral")
        else:
            if triage.get("status") == "error":
                render_failure_note(
                    "AI triage",
                    triage.get("message"),
                    remediation="Check Azure OpenAI configuration and retry when the service is available.",
                )
            else:
                render_status_note("Outcome: AI triage skipped", triage["message"], tone="neutral")

st.markdown(
    f"""
    <div class="roadmap-footer-note">
        <strong>Have a better idea?</strong>
        <span>Open a structured GitHub issue so it can be reviewed, discussed, and prioritized publicly.</span>
        <a href="{escape(feedback_url)}" target="_blank" rel="noopener noreferrer">Submit idea</a>
    </div>
    """,
    unsafe_allow_html=True,
)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
