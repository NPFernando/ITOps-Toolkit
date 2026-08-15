from __future__ import annotations

from html import escape

import streamlit as st

from utils import roadmap
from utils.ai_tools import optional_ai_configured, summarize_feature_requests_with_azure
from utils.ui import apply_app_shell, render_section_heading, render_status_note


st.set_page_config(page_title="Roadmap & Feedback", page_icon=":material/route:", layout="wide")
apply_app_shell(active_page="Roadmap & Feedback")


def _status_tone(status: str) -> str:
    return {
        "Planned": "planned",
        "In Progress": "progress",
        "Complete": "done",
        "AI Recommended": "ai",
    }.get(status, "planned")


def _board_card(label: str, count: int) -> str:
    return (
        '<div class="roadmap-board-card">'
        f"<span>{escape(label)}</span>"
        f"<strong>{count}</strong>"
        "</div>"
    )


def _roadmap_notice(title: str, description: str, tone: str, mark: str) -> str:
    return (
        f'<div class="roadmap-notice roadmap-notice-{escape(tone)}" role="note">'
        f'<div class="roadmap-notice-mark" aria-hidden="true">{escape(mark)}</div>'
        '<div>'
        f"<strong>{escape(title)}</strong>"
        f"<p>{escape(description)}</p>"
        "</div>"
        "</div>"
    )


def _roadmap_card(item: roadmap.RoadmapItem) -> str:
    tone = _status_tone(item.status)
    title_html = escape(item.title)
    if item.url:
        title_html = f'<a href="{escape(item.url)}" target="_blank" rel="noopener noreferrer">{title_html}</a>'
    source_label = "Seed"
    if item.source == "github":
        source_label = f"GitHub #{item.number}" if item.number else "GitHub"
    return (
        f'<article class="roadmap-item-card roadmap-item-{tone}">'
        f'<div class="roadmap-vote-pill"><span>^</span>{item.votes}</div>'
        '<div class="roadmap-item-body">'
        f'<div class="roadmap-card-title">{title_html}</div>'
        '<div class="roadmap-card-meta">'
        f'<span class="roadmap-item-category">{escape(item.category)}</span>'
        f'<span class="roadmap-status-badge">{escape(item.status)}</span>'
        f'<span class="roadmap-source-badge roadmap-source-{escape(item.source)}">{escape(source_label)}</span>'
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


@st.cache_data(ttl=300, show_spinner=False)
def _cached_roadmap_board(repo_url: str, loader_token: int) -> roadmap.RoadmapBoard:
    return roadmap.load_roadmap_board(repo_url=repo_url)


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_triage_summary(open_items: tuple[roadmap.RoadmapItem, ...]) -> dict:
    """Cached for an hour so repeated clicks (by any visitor) reuse one AI call
    per hour rather than paying for the same summary over and over."""
    return summarize_feature_requests_with_azure(list(open_items))


feedback_url = roadmap.github_feature_request_url()
repo_url = roadmap.github_repository_url()
board = _cached_roadmap_board(repo_url, id(roadmap.load_roadmap_board))

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

st.markdown(
    '<div class="roadmap-notice-grid">'
    + _roadmap_notice(
        "Public-safe feedback only",
        "Submit ideas through GitHub Issues. Do not include secrets, internal hostnames, customer logs, tokens, keys, or private data.",
        "warning",
        "!",
    )
    + _roadmap_notice(
        "AI Recommended is curated",
        "The \"AI Recommended\" status label is a static, curated tag, not AI output. An optional, opt-in AI triage "
        "summary is available further down this page and only runs when explicitly requested.",
        "ai",
        "AI",
    )
    + "</div>",
    unsafe_allow_html=True,
)

if board.github_error:
    st.markdown(
        _roadmap_notice("GitHub unavailable, showing seed data", board.github_error, "neutral", "IT"),
        unsafe_allow_html=True,
    )

counts = roadmap.category_counts(board.items)
st.markdown('<div class="roadmap-section-label">Boards</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="roadmap-board-grid">'
    + "".join(_board_card(label, count) for label, count in counts.items())
    + "</div>",
    unsafe_allow_html=True,
)

search_col, filter_col = st.columns([1.4, 1], gap="large")
with search_col:
    query = st.text_input("Search roadmap", placeholder="Search features, categories, or ideas...")
with filter_col:
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

selected_category = category or "All"
filtered_items = roadmap.filter_roadmap_items(query, selected_category, board.items)
items_by_status = roadmap.roadmap_items_by_status(filtered_items)

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
        "AI triage unavailable",
        "Configure Azure OpenAI settings to enable this. The roadmap board above works the same either way.",
        tone="neutral",
    )
elif not open_items:
    render_status_note("Nothing to triage", "All roadmap items are currently marked Complete.", tone="neutral")
else:
    if st.button(f"Summarize {len(open_items)} open items with AI", icon=":material/auto_awesome:"):
        with st.spinner("Generating triage summary..."):
            triage = _cached_triage_summary(tuple(open_items))
        if triage.get("enabled"):
            render_status_note("AI triage summary", triage["summary"], tone="ai")
        else:
            status_tone = "warning" if triage.get("status") == "error" else "neutral"
            render_status_note("AI triage summary", triage["message"], tone=status_tone)

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
