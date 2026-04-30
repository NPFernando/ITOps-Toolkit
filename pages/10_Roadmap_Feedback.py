from __future__ import annotations

from html import escape

import streamlit as st

from utils.roadmap import (
    ROADMAP_STATUSES,
    category_counts,
    filter_roadmap_items,
    github_feature_request_url,
    github_repository_url,
    roadmap_categories,
    roadmap_items_by_status,
)
from utils.ui import apply_app_shell, render_status_note


st.set_page_config(page_title="Roadmap & Feedback", page_icon=":material/route:", layout="wide")
apply_app_shell(active_page="Roadmap & Feedback")


def _status_tone(status: str) -> str:
    return {
        "Planned": "planned",
        "In Progress": "progress",
        "Implemented": "done",
        "AI Recommended": "ai",
    }.get(status, "planned")


def _board_card(label: str, count: int) -> str:
    return f"""
    <div class="roadmap-board-card">
        <span>{escape(label)}</span>
        <strong>{count}</strong>
    </div>
    """


def _roadmap_card(item) -> str:
    tone = _status_tone(item.status)
    return f"""
    <article class="roadmap-item-card roadmap-item-{tone}">
        <div class="roadmap-vote-pill"><span>^</span>{item.votes}</div>
        <div class="roadmap-item-body">
            <h3>{escape(item.title)}</h3>
            <div class="roadmap-card-meta">
                <span class="roadmap-item-category">{escape(item.category)}</span>
                <span class="roadmap-status-badge">{escape(item.status)}</span>
            </div>
            <p>{escape(item.description)}</p>
            <small>{escape(item.rationale)}</small>
        </div>
    </article>
    """


feedback_url = github_feature_request_url()
repo_url = github_repository_url()

st.markdown(
    f"""
    <section class="roadmap-hero">
        <div>
            <div class="roadmap-kicker">Public roadmap</div>
            <h1>Roadmap & Feedback</h1>
            <p>Track what is implemented, what is planned, and which safe AI ideas fit the toolkit direction.</p>
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
    "Public-safe feedback only",
    "Submit ideas through GitHub Issues. Do not include secrets, internal hostnames, customer logs, tokens, keys, or private data.",
    tone="warning",
)

render_status_note(
    "AI Recommended is curated",
    "These ideas are static recommendations based on the current toolkit direction. This page does not call Azure/OpenAI or send feedback to an AI model.",
    tone="ai",
)

counts = category_counts()
st.markdown(
    "<div class=\"roadmap-board-grid\">"
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
        options=("All", *roadmap_categories()),
        default="All",
        label_visibility="collapsed",
    )

selected_category = category or "All"
filtered_items = filter_roadmap_items(query, selected_category)
items_by_status = roadmap_items_by_status(filtered_items)

st.markdown(
    f"""
    <div class="roadmap-summary-line">
        <strong>{len(filtered_items)}</strong> roadmap items shown
        <span>Feedback opens GitHub; no ideas are stored by Streamlit.</span>
    </div>
    """,
    unsafe_allow_html=True,
)

columns = st.columns(4, gap="large")
for index, status in enumerate(ROADMAP_STATUSES):
    status_items = items_by_status[status]
    with columns[index]:
        st.markdown(
            f"""
            <section class="roadmap-column roadmap-column-{_status_tone(status)}">
                <div class="roadmap-column-title">
                    <span></span>
                    <h2>{escape(status)}</h2>
                    <strong>{len(status_items)}</strong>
                </div>
            """,
            unsafe_allow_html=True,
        )
        if not status_items:
            st.markdown(
                """
                <div class="roadmap-empty-column">
                    <strong>No matches</strong>
                    <p>Try another search or category filter.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        for item in status_items:
            st.markdown(_roadmap_card(item), unsafe_allow_html=True)
        st.markdown("</section>", unsafe_allow_html=True)

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
