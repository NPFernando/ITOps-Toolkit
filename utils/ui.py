"""Shared Streamlit UI shell and design helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from html import escape
from typing import Any, Iterable

import pandas as pd
import streamlit as st

from utils.project_links import github_repository_url


MAX_RECENT_TOOLS = 5
PERSISTED_LIST_PARAMS: tuple[str, ...] = ("recent", "fav")


@dataclass(frozen=True)
class ToolMeta:
    title: str
    short_title: str
    description: str
    path: str
    icon: str
    accent: str
    slug: str
    professions: tuple[str, ...]
    category: str
    is_new: bool = False


PROFESSIONS: tuple[str, ...] = (
    "Support Engineer",
    "Network Engineer",
    "Automation Engineer",
    "Security Engineer",
    "Sysadmin / DevOps",
    "Cloud Engineer",
    "Helpdesk / L1",
    "Web Developer",
)

SIDEBAR_CATEGORIES: tuple[str, ...] = (
    "Network",
    "Security",
    "Web & Dev",
    "Ops & Automation",
    "Reference",
)


TOOLS: tuple[ToolMeta, ...] = (
    ToolMeta(
        title="Domain Health Checker",
        short_title="Domain Health Checker",
        description="Complete domain health check including DNS, SSL, HTTP, and security.",
        path="pages/1_Domain_Health_Checker.py",
        icon="GLB",
        accent="#1668f4",
        slug="domain_health",
        professions=("Network Engineer", "Security Engineer", "Sysadmin / DevOps", "Web Developer"),
        category="Network",
    ),
    ToolMeta(
        title="DNS Record Checker",
        short_title="DNS Record Checker",
        description="Look up DNS records including A, MX, TXT, SPF, DMARC, and more.",
        path="pages/2_DNS_Record_Checker.py",
        icon="DNS",
        accent="#23b84d",
        slug="dns_records",
        professions=("Network Engineer", "Sysadmin / DevOps", "Web Developer"),
        category="Network",
    ),
    ToolMeta(
        title="SSL Certificate Checker",
        short_title="SSL Certificate Checker",
        description="Check SSL certificate details, validity, issuer, subject, and expiration.",
        path="pages/3_SSL_Certificate_Checker.py",
        icon="LOCK",
        accent="#7047e8",
        slug="ssl_certificate",
        professions=("Security Engineer", "Web Developer", "Sysadmin / DevOps"),
        category="Security",
    ),
    ToolMeta(
        title="HTTP Status Checker",
        short_title="HTTP Status Checker",
        description="Check website status, response time, redirects, and security headers.",
        path="pages/4_HTTP_Status_Checker.py",
        icon="HTTP",
        accent="#ff6b13",
        slug="http_status",
        professions=("Web Developer", "Sysadmin / DevOps", "Support Engineer"),
        category="Web & Dev",
    ),
    ToolMeta(
        title="JSON Formatter",
        short_title="JSON Formatter",
        description="Format, validate, and minify your JSON instantly.",
        path="pages/5_JSON_Formatter.py",
        icon="{ }",
        accent="#11aab8",
        slug="json_formatter",
        professions=("Automation Engineer", "Web Developer", "Cloud Engineer"),
        category="Web & Dev",
    ),
    ToolMeta(
        title="Base64 Tool",
        short_title="Base64 Tool",
        description="Encode and decode Base64 text safely in your browser session.",
        path="pages/6_Base64_Tool.py",
        icon="64",
        accent="#0f7ff0",
        slug="base64_tool",
        professions=("Automation Engineer", "Web Developer", "Support Engineer"),
        category="Web & Dev",
    ),
    ToolMeta(
        title="JWT Decoder",
        short_title="JWT Decoder",
        description="Decode JWT headers and payloads locally without signature verification.",
        path="pages/7_JWT_Decoder.py",
        icon="JWT",
        accent="#3d5be9",
        slug="jwt_decoder",
        professions=("Web Developer", "Security Engineer", "Automation Engineer"),
        category="Security",
    ),
    ToolMeta(
        title="Cron Explainer",
        short_title="Cron Explainer",
        description="Explain common 5-field cron expressions and preview upcoming runs.",
        path="pages/8_Cron_Explainer.py",
        icon="CLK",
        accent="#6f55e9",
        slug="cron_explainer",
        professions=("Automation Engineer", "Sysadmin / DevOps", "Cloud Engineer"),
        category="Ops & Automation",
    ),
    ToolMeta(
        title="Log Troubleshooting Assistant",
        short_title="Log Troubleshooting",
        description="Find common operational error patterns in pasted logs.",
        path="pages/9_Log_Troubleshooting_Assistant.py",
        icon="LOG",
        accent="#1d78f0",
        slug="log_troubleshooting",
        professions=("Support Engineer", "Helpdesk / L1", "Sysadmin / DevOps"),
        category="Ops & Automation",
    ),
    ToolMeta(
        title="Subnet Calculator",
        short_title="Subnet Calculator",
        description="Calculate network, broadcast, host range, and usable hosts from a CIDR block.",
        path="pages/11_Subnet_Calculator.py",
        icon="NET",
        accent="#0e9f6e",
        slug="subnet_calculator",
        professions=("Network Engineer", "Sysadmin / DevOps", "Cloud Engineer"),
        category="Network",
        is_new=True,
    ),
    ToolMeta(
        title="Hash Generator",
        short_title="Hash Generator",
        description="Generate MD5/SHA/SHA-3 digests and HMAC signatures from text.",
        path="pages/12_Hash_Generator.py",
        icon="#",
        accent="#9333ea",
        slug="hash_generator",
        professions=("Security Engineer", "Automation Engineer"),
        category="Security",
        is_new=True,
    ),
    ToolMeta(
        title="MAC Address Tool",
        short_title="MAC Address Tool",
        description="Validate a MAC address and view colon, hyphen, dot, and bare formats.",
        path="pages/13_MAC_Address_Tool.py",
        icon="MAC",
        accent="#dc6803",
        slug="mac_address_tool",
        professions=("Network Engineer", "Sysadmin / DevOps"),
        category="Network",
        is_new=True,
    ),
    ToolMeta(
        title="Email Header Analyzer",
        short_title="Email Header Analyzer",
        description="Parse raw email headers into a summary, hop chain, and auth results.",
        path="pages/14_Email_Header_Analyzer.py",
        icon="EML",
        accent="#e03f6e",
        slug="email_header_analyzer",
        professions=("Security Engineer", "Support Engineer", "Helpdesk / L1"),
        category="Security",
        is_new=True,
    ),
    ToolMeta(
        title="Port Reference",
        short_title="Port Reference",
        description="Look up common network ports by number, protocol, or service name.",
        path="pages/15_Port_Reference.py",
        icon="P/T",
        accent="#0891b2",
        slug="port_reference",
        professions=("Network Engineer", "Security Engineer", "Helpdesk / L1"),
        category="Reference",
        is_new=True,
    ),
    ToolMeta(
        title="Password Generator",
        short_title="Password Generator",
        description="Generate a strong random password or a diceware-style passphrase.",
        path="pages/16_Password_Generator.py",
        icon="PWD",
        accent="#be123c",
        slug="password_generator",
        professions=("Security Engineer", "Support Engineer", "Helpdesk / L1", "Sysadmin / DevOps"),
        category="Security",
        is_new=True,
    ),
    ToolMeta(
        title="URL Encoder/Decoder",
        short_title="URL Encoder/Decoder",
        description="Percent-encode or decode URL components and query strings.",
        path="pages/17_URL_Encoder_Decoder.py",
        icon="URL",
        accent="#0284c7",
        slug="url_encoder_decoder",
        professions=("Web Developer", "Automation Engineer", "Support Engineer"),
        category="Web & Dev",
        is_new=True,
    ),
    ToolMeta(
        title="Regex Tester",
        short_title="Regex Tester",
        description="Test a regular expression against sample text with match positions and groups.",
        path="pages/18_Regex_Tester.py",
        icon="RGX",
        accent="#65a30d",
        slug="regex_tester",
        professions=("Automation Engineer", "Web Developer", "Support Engineer"),
        category="Web & Dev",
        is_new=True,
    ),
    ToolMeta(
        title="Timestamp Converter",
        short_title="Timestamp Converter",
        description="Convert between Unix epoch, ISO 8601, and human-readable timestamps across timezones.",
        path="pages/19_Timestamp_Converter.py",
        icon="EPO",
        accent="#0d9488",
        slug="timestamp_converter",
        professions=("Automation Engineer", "Sysadmin / DevOps", "Support Engineer", "Cloud Engineer"),
        category="Ops & Automation",
        is_new=True,
    ),
    ToolMeta(
        title="Text Diff Checker",
        short_title="Text Diff Checker",
        description="Compare two blocks of text and see exactly what changed, line by line.",
        path="pages/20_Text_Diff_Checker.py",
        icon="DIF",
        accent="#7c3aed",
        slug="text_diff_checker",
        professions=("Automation Engineer", "Web Developer", "Support Engineer"),
        category="Web & Dev",
        is_new=True,
    ),
    ToolMeta(
        title="JWT Encoder",
        short_title="JWT Encoder",
        description="Build and sign a JWT from a JSON payload, secret, and HMAC algorithm.",
        path="pages/21_JWT_Encoder.py",
        icon="JWT+",
        accent="#4338ca",
        slug="jwt_encoder",
        professions=("Web Developer", "Security Engineer", "Automation Engineer"),
        category="Security",
        is_new=True,
    ),
)

POPULAR_TOOLS = TOOLS[:5]
TITLE_TO_SLUG: dict[str, str] = {tool.title: tool.slug for tool in TOOLS}


def apply_app_shell(active_page: str) -> None:
    """Apply global theme CSS and render the shared sidebar shell.

    Sidebar renders first so the theme-toggle widget resolves this run's
    value into session_state before CSS is injected -- injecting CSS first
    would use last run's stale mode and make a mode switch lag by one click.
    """
    render_sidebar(active_page)
    _inject_global_css(current_theme_mode())
    slug = TITLE_TO_SLUG.get(active_page)
    if slug is not None:
        record_recent_visit(slug)
    _sync_local_storage_mirror(active_page)


def _get_persisted_slugs(param: str) -> list[str]:
    """Read a comma-separated slug list from the URL query params."""
    return [slug for slug in st.query_params.get(param, "").split(",") if slug]


def _set_persisted_slugs(param: str, slugs: list[str]) -> None:
    """Write a slug list back into the URL query params (removing the key when empty)."""
    if slugs:
        st.query_params[param] = ",".join(slugs)
    else:
        st.query_params.pop(param, None)


def record_recent_visit(slug: str) -> None:
    """Prepend ``slug`` to the recents list (deduped, capped) and persist it."""
    stored = _get_persisted_slugs("recent")
    stored = [slug, *(s for s in stored if s != slug)][:MAX_RECENT_TOOLS]
    _set_persisted_slugs("recent", stored)


def toggle_favorite(slug: str) -> None:
    """Add or remove ``slug`` from the favorites list."""
    stored = _get_persisted_slugs("fav")
    if slug in stored:
        stored = [s for s in stored if s != slug]
    else:
        stored = [*stored, slug]
    _set_persisted_slugs("fav", stored)


def _sync_local_storage_mirror(active_page: str) -> None:
    """Mirror the persisted-slug query params to/from browser localStorage.

    Runs client-side JS in a same-origin sandboxed iframe (confirmed via the
    installed streamlit static bundle: HTML-string iframes carry
    `allow-same-origin`, so they share the page's real localStorage).

    Python owns st.query_params as the live, in-session source of truth
    (record_recent_visit/toggle_favorite write it directly, no reload
    needed for those interactions). This function's jobs, run on every
    page for every tracked param:
    - Mirror Python's current value into localStorage (durable, one-way,
      no reload -- keeps localStorage in sync with whatever Python just
      wrote). Runs on every page: a tool page's record_recent_visit() only
      updates st.query_params for that pageview, so this mirror step is
      what actually makes it durable across sessions.
    - On Home only: if Python has no value for a param yet (fresh
      session/tab) but localStorage has one, seed the URL from localStorage
      with a single reload so Python picks it up next run. This is the
      only way to get data out of localStorage, since an iframe HTML
      string has no return channel to Python. Restricted to Home so
      tool-page URLs never get rewritten/reloaded just to carry a value
      only Home displays.

    NOTE: this assumes window.top.location.search already reflects this
    run's st.query_params writes by the time the iframe's script executes.
    That held in manual testing but is a real-browser timing assumption
    AppTest cannot exercise (no JS execution) -- verify manually after deploy.
    """
    st.iframe(
        f"""
        <script>
        (function() {{
            var KEYS = {json.dumps(list(PERSISTED_LIST_PARAMS))};
            var CAN_SEED = {json.dumps(active_page == "Home")};
            var params = new URLSearchParams(window.top.location.search);
            var changed = false;
            KEYS.forEach(function(key) {{
                var storageKey = "itops_" + key;
                var stored = localStorage.getItem(storageKey) || "";
                if (params.has(key)) {{
                    var current = params.get(key);
                    if (current !== stored) {{
                        try {{ localStorage.setItem(storageKey, current); }} catch (e) {{}}
                    }}
                }} else if (CAN_SEED && stored) {{
                    params.set(key, stored);
                    changed = true;
                }}
            }});
            if (changed) {{
                var search = params.toString();
                var newUrl = window.top.location.pathname + (search ? "?" + search : "") + window.top.location.hash;
                window.top.location.replace(newUrl);
            }}
        }})();
        </script>
        """,
        height=1,
    )


def render_sidebar(active_page: str) -> None:
    """Render branded navigation and persistent safety/about panels."""
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="brand-mark">IT</div>
                <div>
                    <div class="brand-name"><span>ITOps</span> Toolkit</div>
                    <div class="brand-subtitle">Free tools for IT admins, MSP engineers, and DevOps pros.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _render_theme_toggle()
        quick_search = st.text_input(
            "Quick search",
            placeholder="Jump to a tool...",
            label_visibility="collapsed",
            key="sidebar_quick_search",
            icon=":material/search:",
        )
        if quick_search.strip():
            _render_quick_search_results(active_page, quick_search)
        else:
            st.markdown('<div class="sidebar-section-label">Navigation</div>', unsafe_allow_html=True)
            _sidebar_link("Home", "app.py", active_page == "Home", ":material/home:")
            _sidebar_link(
                "Roadmap & Feedback",
                "pages/10_Roadmap_Feedback.py",
                active_page == "Roadmap & Feedback",
                ":material/route:",
            )
            _render_grouped_tool_links(active_page)

        st.markdown(
            """
            <div class="sidebar-info-card sidebar-safe-card">
                <div class="sidebar-card-title">SAFE TO USE</div>
                <p>This toolkit is public-safe. Do not paste passwords, private keys, tokens, or sensitive data.</p>
            </div>
            <div class="sidebar-info-card">
                <div class="sidebar-card-title">ABOUT</div>
                <p>ITOps Toolkit is an open source project built with Streamlit.</p>
                <p class="sidebar-card-muted">2026 ITOps Toolkit</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_home_hero() -> str:
    """Render the dashboard hero and return the current search query."""
    left, right = st.columns([1.1, 1], gap="large")
    with left:
        st.markdown(
            """
            <section class="home-hero-copy">
                <h1><span>ITOps</span> Toolkit</h1>
                <p>A collection of free, fast, and secure tools for IT admins,
                MSP engineers, automation engineers, and DevOps professionals.</p>
            </section>
            """,
            unsafe_allow_html=True,
        )
        query = st.text_input(
            "Search tools",
            placeholder="Search tools...",
            label_visibility="collapsed",
            key="tool_search",
        )
        st.markdown(
            """
            <div class="trust-chip-row">
                <span class="trust-chip">100% Free</span>
                <span class="trust-chip">Public Safe</span>
                <span class="trust-chip">No Signup</span>
                <span class="trust-chip">Open Source</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(_hero_visual_html(), unsafe_allow_html=True)
    return query


def render_tool_section(
    tools: Iterable[ToolMeta],
    query: str = "",
    heading: str | None = None,
    section_id: str | None = "all-tools",
    key_prefix: str = "tools",
) -> None:
    """Render a home page tool card grid.

    ``heading`` overrides the default label ("Matching Tools" when ``query``
    is set, otherwise "Popular Tools") -- used for e.g. the personalized
    "Recently Used" row. ``section_id`` sets the heading div's HTML id; pass
    None when rendering more than one section on the same page so IDs stay
    unique. ``key_prefix`` must also be unique per section on a page since
    the same tool can appear in more than one grid (e.g. recents + all
    tools) and Streamlit container keys must be unique.
    """
    tools = tuple(tools)
    section_label = heading if heading is not None else ("Matching Tools" if query.strip() else "Popular Tools")
    id_attr = f' id="{escape(section_id)}"' if section_id else ""
    st.markdown(
        f"""
        <div class="section-heading"{id_attr}>
            <div><span class="section-bolt">IT</span><h2>{escape(section_label)}</h2></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not tools:
        st.info("No tools match your search.")
        return

    favorite_slugs = set(_get_persisted_slugs("fav"))
    cols = st.columns(min(len(tools), 5), gap="large")
    for index, tool in enumerate(tools):
        with cols[index % len(cols)]:
            with st.container(key=f"tool_card_{key_prefix}_{tool.slug}"):
                delay_ms = min(index, 9) * 45
                st.markdown(_tool_card_html(tool, delay_ms=delay_ms), unsafe_allow_html=True)
                link_col, fav_col = st.columns([5, 1])
                with link_col:
                    _safe_page_link(tool.path, label="Open Tool", icon=":material/arrow_forward:", stretch_width=True)
                with fav_col:
                    is_fav = tool.slug in favorite_slugs
                    fav_icon = ":material/star:" if is_fav else ":material/star_border:"
                    fav_help = "Remove from favorites" if is_fav else "Add to favorites"
                    if st.button("", icon=fav_icon, key=f"fav_toggle_{key_prefix}_{tool.slug}", help=fav_help):
                        toggle_favorite(tool.slug)
                        st.rerun()


def render_feature_strip() -> None:
    st.markdown(
        """
        <div class="feature-strip">
            <div class="feature-item"><div class="feature-icon feature-blue">SH</div><div><strong>Fast & Reliable</strong><p>Instant results with accurate data from trusted sources.</p></div></div>
            <div class="feature-item"><div class="feature-icon feature-purple">ND</div><div><strong>No Data Stored</strong><p>We do not store or log your data. Your privacy is respected.</p></div></div>
            <div class="feature-item"><div class="feature-icon feature-green">PS</div><div><strong>Public Safe</strong><p>Built to be safe for public use. Remove sensitive info.</p></div></div>
            <div class="feature-item"><div class="feature-icon feature-orange">OS</div><div><strong>Open Source</strong><p>Transparent, open, and community driven.</p></div></div>
            <div class="feature-item"><div class="feature-icon feature-blue">MB</div><div><strong>Mobile Friendly</strong><p>Works on desktop, tablet, and mobile devices.</p></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_important_notice() -> None:
    st.markdown(
        """
        <div class="important-notice">
            <div class="notice-icon">i</div>
            <div><strong>Important Notice</strong><p>Do not paste passwords, private keys, tokens, or any sensitive customer data. This toolkit is for educational and troubleshooting purposes only.</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, description: str, warning: str | None = None) -> None:
    """Render a compact page header for tool pages."""
    tool = tool_by_title(title)
    icon = tool.icon if tool else "IT"
    accent = tool.accent if tool else "#1668f4"
    st.markdown(
        f"""
        <section class="tool-page-header" style="--tool-accent: {accent};">
            <div class="tool-page-icon">{escape(icon)}</div>
            <div>
                <h1>{escape(title)}</h1>
                <p>{escape(description)}</p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    if warning:
        st.warning(warning)


def tool_form_panel(key: str):
    return st.container(key=f"tool_form_panel_{_key_slug(key)}")


def tool_result_panel(key: str):
    return st.container(key=f"tool_result_panel_{_key_slug(key)}")


def tool_download_panel(key: str):
    return st.container(key=f"tool_download_panel_{_key_slug(key)}")


def display_rows_frame(rows: Iterable[dict[str, Any]]) -> pd.DataFrame:
    """Build a Streamlit-safe dataframe for mixed-value display rows."""
    return pd.DataFrame(
        {key: str(value) for key, value in row.items()}
        for row in rows
    )


def render_form_intro(title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="tool-form-intro">
            <div class="tool-panel-eyebrow">Input</div>
            <h2>{escape(title)}</h2>
            <p>{escape(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_heading(title: str, description: str | None = None, eyebrow: str = "Results") -> None:
    # description_html sits on the same line as </h2> above, not alone on its
    # own line, because when it's "" (no description) a whitespace-only line
    # there is a blank line per CommonMark -- which ends this raw HTML block
    # early and drops everything after it to a literal-text code block
    # instead of rendering as HTML. See _tool_card_html for the same fix.
    description_html = f"<p>{escape(description)}</p>" if description else ""
    st.markdown(
        f"""
        <div class="tool-section-heading">
            <div class="tool-panel-eyebrow">{escape(eyebrow)}</div>
            <h2>{escape(title)}</h2>{description_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="tool-empty-state">
            <div class="tool-empty-mark">IT</div>
            <div>
                <strong>{escape(title)}</strong>
                <p>{escape(description)}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_safe_note(title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="tool-safe-note">
            <strong>{escape(title)}</strong>
            <p>{escape(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_note(title: str, description: str, tone: str = "info") -> None:
    """Render a compact, escaped status panel for tool-page state messages."""
    allowed_tones = {"info", "success", "warning", "neutral", "ai"}
    normalized_tone = tone if tone in allowed_tones else "info"
    marks = {
        "info": "i",
        "success": "OK",
        "warning": "!",
        "neutral": "IT",
        "ai": "AI",
    }
    description_html = escape(description).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="tool-status-note tool-status-note-{normalized_tone}">
            <div class="tool-status-mark">{escape(marks[normalized_tone])}</div>
            <div>
                <strong>{escape(title)}</strong>
                <p>{description_html}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def filter_tools(query: str = "", profession: str = "All") -> tuple[ToolMeta, ...]:
    """Return every tool matching both the search text and the profession filter."""
    value = query.strip().lower()
    matches_query = (
        (lambda tool: True)
        if not value
        else (
            lambda tool: value in tool.title.lower()
            or value in tool.short_title.lower()
            or value in tool.description.lower()
            or value in tool.slug.replace("_", " ")
        )
    )
    matches_profession = (
        (lambda tool: True) if profession not in PROFESSIONS else (lambda tool: profession in tool.professions)
    )
    return tuple(tool for tool in TOOLS if matches_query(tool) and matches_profession(tool))


def _resolve_slugs(slugs: Iterable[str]) -> list[ToolMeta]:
    """Map slugs to ToolMeta, in order, skipping unknown/stale slugs and duplicates."""
    by_slug = {tool.slug: tool for tool in TOOLS}
    resolved: list[ToolMeta] = []
    seen: set[str] = set()
    for slug in slugs:
        tool = by_slug.get(slug)
        if tool is None or tool.slug in seen:
            continue
        resolved.append(tool)
        seen.add(tool.slug)
    return resolved


def recent_or_popular_tools(recent_slugs: Iterable[str]) -> tuple[ToolMeta, ...]:
    """Map recently-visited tool slugs (most-recent-first) to ToolMeta, padded with POPULAR_TOOLS.

    Unknown/stale slugs are skipped silently. Falls back entirely to
    POPULAR_TOOLS for a visitor with no recorded recents yet.
    """
    resolved = _resolve_slugs(recent_slugs)[:MAX_RECENT_TOOLS]
    seen = {tool.slug for tool in resolved}

    if len(resolved) < MAX_RECENT_TOOLS:
        for tool in POPULAR_TOOLS:
            if tool.slug in seen:
                continue
            resolved.append(tool)
            seen.add(tool.slug)
            if len(resolved) >= MAX_RECENT_TOOLS:
                break

    return tuple(resolved)


def favorite_tools() -> tuple[ToolMeta, ...]:
    """Return the visitor's favorited tools, in the order they were favorited. No padding."""
    return tuple(_resolve_slugs(_get_persisted_slugs("fav")))


def sort_tools(tools: tuple[ToolMeta, ...], mode: str) -> tuple[ToolMeta, ...]:
    """Sort a tool grid. "az"/"za" sort by title; anything else keeps declared order."""
    if mode == "az":
        return tuple(sorted(tools, key=lambda tool: tool.title.lower()))
    if mode == "za":
        return tuple(sorted(tools, key=lambda tool: tool.title.lower(), reverse=True))
    return tools


def tool_by_title(title: str) -> ToolMeta | None:
    return next((tool for tool in TOOLS if tool.title == title), None)


def github_url() -> str | None:
    return github_repository_url()


MAX_QUICK_SEARCH_RESULTS = 8


def _render_quick_search_results(active_page: str, query: str) -> None:
    """Render sidebar quick-search matches for ``query``, replacing the full nav list."""
    matches = filter_tools(query)[:MAX_QUICK_SEARCH_RESULTS]
    st.markdown('<div class="sidebar-section-label">Search Results</div>', unsafe_allow_html=True)
    if not matches:
        st.caption("No tools match.")
        return
    for tool in matches:
        _sidebar_link(tool.short_title, tool.path, active_page == tool.title, _material_icon_for(tool.slug))


def _render_grouped_tool_links(active_page: str) -> None:
    """Render the sidebar's tool links grouped by category.

    A category with more than one tool gets a collapsible st.expander
    (its own widget state persists each visitor's collapse/expand choice
    across reruns); a category with exactly one tool renders that tool's
    link directly with no group header -- same rule killer-tools-site
    uses for its single-tool categories.
    """
    by_category: dict[str, list[ToolMeta]] = {category: [] for category in SIDEBAR_CATEGORIES}
    for tool in TOOLS:
        by_category.setdefault(tool.category, []).append(tool)

    for category in SIDEBAR_CATEGORIES:
        tools = by_category.get(category, [])
        if not tools:
            continue
        if len(tools) == 1:
            tool = tools[0]
            _sidebar_link(tool.short_title, tool.path, active_page == tool.title, _material_icon_for(tool.slug))
            continue
        with st.expander(category, expanded=True, icon=None, key=f"sidebar_cat_{_key_slug(category)}"):
            for tool in tools:
                _sidebar_link(tool.short_title, tool.path, active_page == tool.title, _material_icon_for(tool.slug))


def _sidebar_link(label: str, path: str, active: bool, icon: str) -> None:
    state = "active" if active else "idle"
    with st.container(key=f"nav_{_key_slug(label)}_{state}"):
        _safe_page_link(path, label=label, icon=icon, stretch_width=True)


def _safe_page_link(path: str, label: str, icon: str, stretch_width: bool = False) -> None:
    try:
        width = "stretch" if stretch_width else "content"
        st.page_link(path, label=label, icon=icon, width=width)
    except KeyError:
        st.markdown(
            f'<a class="fallback-page-link" href="{_fallback_href(path)}">{escape(label)}</a>',
            unsafe_allow_html=True,
        )


def _fallback_href(path: str) -> str:
    if path == "app.py":
        return "/"
    filename = path.rsplit("/", 1)[-1].removesuffix(".py")
    parts = filename.split("_", 1)
    page_name = parts[1] if len(parts) == 2 and parts[0].isdigit() else filename
    return f"/{page_name}"


def _tool_card_html(tool: ToolMeta, delay_ms: int = 0) -> str:
    # NOTE: new_badge must not sit alone on its own line below. When it's ""
    # (not a new tool), a whitespace-only line there is a blank line per
    # CommonMark, which ends this raw HTML block early -- everything after
    # it then gets parsed as an indented code block instead of HTML, and
    # the card renders as literal escaped tag text. Keeping it on the same
    # line as the opening tag means that line is never blank.
    new_badge = '<span class="tool-card-badge-new">NEW</span>' if tool.is_new else ""
    return f"""
    <div class="tool-card-shell" style="--tool-accent: {tool.accent}; animation-delay: {delay_ms}ms;">{new_badge}
        <div class="tool-card-icon">{escape(tool.icon)}</div>
        <h3>{escape(tool.title)}</h3>
        <p>{escape(tool.description)}</p>
    </div>
    """


def _hero_visual_html() -> str:
    return """
    <div class="hero-visual" aria-hidden="true">
        <div class="dot-grid dot-grid-a"></div>
        <div class="dot-grid dot-grid-b"></div>
        <div class="hero-globe"><span></span></div>
        <div class="hero-shield">OK</div>
        <div class="laptop">
            <div class="laptop-screen">
                <div class="chart-line"></div>
                <div class="chart-line chart-line-two"></div>
                <div class="screen-grid"></div>
            </div>
            <div class="laptop-base"></div>
        </div>
        <div class="server-stack">
            <div></div><div></div><div></div>
        </div>
    </div>
    """


def _material_icon_for(slug: str) -> str:
    icons = {
        "domain_health": ":material/public:",
        "dns_records": ":material/dns:",
        "ssl_certificate": ":material/lock:",
        "http_status": ":material/speed:",
        "json_formatter": ":material/data_object:",
        "base64_tool": ":material/looks_6:",
        "jwt_decoder": ":material/verified_user:",
        "cron_explainer": ":material/schedule:",
        "log_troubleshooting": ":material/list_alt:",
        "subnet_calculator": ":material/lan:",
        "hash_generator": ":material/tag:",
        "mac_address_tool": ":material/settings_ethernet:",
        "email_header_analyzer": ":material/mail:",
        "port_reference": ":material/router:",
        "password_generator": ":material/password:",
        "url_encoder_decoder": ":material/link:",
        "regex_tester": ":material/pattern:",
        "timestamp_converter": ":material/schedule:",
        "text_diff_checker": ":material/difference:",
        "jwt_encoder": ":material/verified_user:",
    }
    return icons.get(slug, ":material/build:")


def _key_slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_")


THEME_MODE_KEY = "itops_theme_mode"

# Dark matches the shared palette reused across cloudscope, odysseus, and
# hermes-workspace. Light restores this app's original palette. Only these
# central tokens switch between modes -- decorative one-off gradients and
# shadows elsewhere in this file are not mode-aware (see THEME.md note in
# the PR/commit history) and keep their original literal values in both
# modes, since there's no way to visually verify a full per-mode conversion
# of ~150 one-off values in this environment.
_THEME_TOKENS = {
    "dark": {
        "blue": "#e06c75",
        "blue-dark": "#c65861",
        "ink": "#9cdef2",
        "muted": "#6b8a94",
        "line": "#355a66",
        "bg": "#282c34",
        "panel": "#1e2228",
        "sidebar": "#1e2228",
        "sidebar-2": "#111111",
        "green": "#50fa7b",
        "purple": "#c678dd",
        "orange": "#f0ad4e",
        # Card/panel surfaces on the main content area (not the sidebar,
        # which is always dark in both modes). Distinct from "panel" above,
        # which theme-toggle-era code already uses for a couple of other
        # things -- these back the tool-card / result-panel glass surfaces.
        "surface": "rgba(30, 34, 40, 0.82)",
        "surface-strong": "#1e2228",
        "surface-border": "rgba(53, 90, 102, 0.45)",
        "text-secondary": "#a9c2ce",
        "input-bg": "#20242b",
        "app-gradient-top": "#2a2e36",
        "app-gradient-bottom": "#1f232a",
    },
    "light": {
        "blue": "#126bff",
        "blue-dark": "#0a47c9",
        "ink": "#07142f",
        "muted": "#52637f",
        "line": "#d7e2f5",
        "bg": "#f6f9ff",
        "panel": "#fbfdff",
        "sidebar": "#071a33",
        "sidebar-2": "#0b2748",
        "green": "#22ba4f",
        "purple": "#6d55e9",
        "orange": "#ff6a13",
        "surface": "rgba(255, 255, 255, 0.84)",
        "surface-strong": "#ffffff",
        "surface-border": "#d4e0f2",
        "text-secondary": "#334765",
        "input-bg": "#ffffff",
        "app-gradient-top": "#fbfdff",
        "app-gradient-bottom": "#eef5ff",
    },
}


def current_theme_mode() -> str:
    """Return the active theme mode, defaulting to dark."""
    mode = st.session_state.get(THEME_MODE_KEY, "dark")
    return mode if mode in _THEME_TOKENS else "dark"


def _render_theme_toggle() -> None:
    """Sidebar control letting visitors switch between the dark (default) and light palette."""
    current_label = "Dark" if current_theme_mode() == "dark" else "Light"
    selection = st.segmented_control(
        "Theme",
        options=["Dark", "Light"],
        default=current_label,
        label_visibility="collapsed",
        key="itops_theme_toggle_control",
        persist_state="session",
    )
    st.session_state[THEME_MODE_KEY] = "dark" if selection == "Dark" else "light"


def _inject_global_css(mode: str) -> None:
    # NOTE: the CSS below is a plain (non f-string) template with a single
    # literal placeholder substituted via str.replace(). It is deliberately
    # NOT an f-string/`.format()` call, since the block contains thousands of
    # literal `{`/`}` CSS rule braces that would otherwise need escaping.
    tokens = _THEME_TOKENS[mode]
    root_vars = "\n            ".join(f"--itops-{name}: {value};" for name, value in tokens.items())
    css = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

        :root {
            __ITOPS_ROOT_VARS__
            --card-radius: 8px;
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }
        }

        html,
        body {
            background: var(--itops-bg);
        }

        .stApp {
            background:
                radial-gradient(circle at 70% 0%, rgba(18, 107, 255, 0.12), transparent 30%),
                linear-gradient(180deg, var(--itops-app-gradient-top) 0%, var(--itops-bg) 48%, var(--itops-app-gradient-bottom) 100%);
            color: var(--itops-ink);
            font-family: 'Manrope', 'Segoe UI', sans-serif;
        }

        [data-testid="stAppViewContainer"] {
            background: transparent;
        }

        .block-container {
            max-width: 1280px;
            padding: 2rem 2.4rem 2.8rem;
        }

        #MainMenu,
        footer,
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        [data-testid="stHeader"] {
            display: block !important;
            height: 0 !important;
            min-height: 0 !important;
            background: transparent !important;
            pointer-events: none;
        }

        [data-testid="stToolbar"] {
            display: block !important;
            background: transparent !important;
            pointer-events: none;
        }

        [data-testid="stExpandSidebarButton"] {
            position: fixed !important;
            top: 0.85rem !important;
            left: 0.85rem !important;
            width: 2.45rem !important;
            height: 2.45rem !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            border-radius: 8px !important;
            color: #ffffff !important;
            background: linear-gradient(135deg, #2487ff, #0f66ee) !important;
            box-shadow: 0 12px 26px rgba(13, 103, 242, 0.26) !important;
            pointer-events: auto !important;
            z-index: 1000000 !important;
        }

        [data-testid="stExpandSidebarButton"] * {
            color: inherit !important;
            fill: currentColor !important;
        }

        h1, h2, h3, p, label, div, span {
            letter-spacing: 0;
        }

        h1, h2, h3 {
            color: var(--itops-ink);
        }

        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 40% 15%, rgba(20, 111, 255, 0.26), transparent 26%),
                linear-gradient(180deg, var(--itops-sidebar) 0%, #061429 100%);
            border-right: 1px solid rgba(125, 161, 217, 0.18);
            top: 0;
            height: 100vh;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding: 1.25rem 1rem 1.8rem;
        }

        [data-testid="stSidebarHeader"],
        [data-testid="stSidebarCollapseButton"] {
            background: transparent !important;
            color: #dceaff !important;
        }

        [data-testid="stSidebarCollapseButton"] {
            visibility: visible !important;
        }

        [data-testid="stSidebarCollapseButton"] button {
            color: #dceaff !important;
            border-radius: 8px !important;
        }

        [data-testid="stSkeleton"],
        [data-testid="stSkeleton"] > div,
        [class*="Skeleton"] {
            border-radius: 8px !important;
            background-color: #e7f0ff !important;
            background-image: linear-gradient(90deg, #e7f0ff 0%, #f7fbff 50%, #e7f0ff 100%) !important;
        }

        [data-testid="stSpinner"],
        [data-testid="stSpinner"] * {
            color: var(--itops-blue) !important;
        }

        .sidebar-brand {
            display: flex;
            gap: 0.75rem;
            align-items: center;
            padding: 0.2rem 0.2rem 1.25rem;
            border-bottom: 1px solid rgba(178, 205, 246, 0.15);
            margin-bottom: 1rem;
        }

        .brand-mark {
            width: 3.1rem;
            height: 3.7rem;
            border-radius: 8px 8px 18px 18px;
            display: grid;
            place-items: center;
            color: #ffffff;
            font-weight: 800;
            background: linear-gradient(145deg, #2c8cff 0%, #0e63ee 54%, #064ad4 100%);
            box-shadow: 0 16px 32px rgba(0, 89, 255, 0.28);
        }

        .brand-name {
            color: #ffffff;
            font-size: 1.25rem;
            line-height: 1.1;
            font-weight: 800;
        }

        .brand-name span {
            color: #2e8bff;
        }

        .brand-subtitle {
            margin-top: 0.45rem;
            color: #c9d8ef;
            font-size: 0.82rem;
            line-height: 1.55;
        }

        .sidebar-section-label {
            color: #8da5c7;
            text-transform: uppercase;
            font-size: 0.72rem;
            font-weight: 800;
            margin: 0.55rem 0 0.45rem;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a {
            border-radius: 8px;
            color: #dceaff !important;
            min-height: 2.85rem;
            padding: 0.65rem 0.7rem;
            font-weight: 650;
            background: transparent;
            border: 1px solid transparent;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a * {
            color: inherit !important;
            fill: currentColor !important;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(152, 190, 245, 0.22);
        }

        [data-testid="stSidebar"] .st-key-nav_home_active [data-testid="stPageLink"] a,
        [data-testid="stSidebar"] [class*="st-key-nav_"][class*="_active"] [data-testid="stPageLink"] a {
            background: linear-gradient(135deg, #278aff 0%, #0f67f2 100%);
            box-shadow: 0 12px 24px rgba(13, 103, 242, 0.28);
            color: #ffffff !important;
        }

        .fallback-page-link {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 2.35rem;
            border-radius: 8px;
            padding: 0.65rem 0.8rem;
            color: #ffffff !important;
            text-decoration: none !important;
            font-weight: 800;
            background: linear-gradient(135deg, #2487ff, #0f66ee);
        }

        [data-testid="stSidebar"] .fallback-page-link {
            justify-content: flex-start;
            min-height: 2.85rem;
            background: transparent;
            color: #edf5ff !important;
            font-weight: 650;
        }

        .sidebar-info-card {
            border-radius: 8px;
            padding: 1rem 1.05rem;
            margin-top: 1.05rem;
            color: #d9e6f7;
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.035));
            border: 1px solid rgba(166, 198, 239, 0.12);
        }

        .sidebar-info-card p {
            margin: 0.7rem 0 0;
            color: #d2deef;
            font-size: 0.82rem;
            line-height: 1.55;
        }

        .sidebar-card-title {
            color: #30d968;
            font-size: 0.78rem;
            font-weight: 800;
        }

        .sidebar-card-muted {
            color: #9eb3cf !important;
        }

        .home-hero-copy {
            padding: 1.8rem 0 0.6rem;
        }

        .home-hero-copy h1 {
            margin: 0 0 1rem;
            font-size: clamp(2.5rem, 5.1vw, 4.4rem);
            line-height: 0.98;
            font-weight: 800;
        }

        .home-hero-copy h1 span {
            color: var(--itops-blue);
        }

        .home-hero-copy p {
            color: var(--itops-text-secondary);
            margin: 0;
            max-width: 40rem;
            font-size: clamp(1rem, 1.7vw, 1.24rem);
            line-height: 1.7;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        [data-testid="stNumberInput"] input {
            border-radius: 8px;
            border: 1px solid var(--itops-surface-border);
            background: var(--itops-input-bg);
            color: var(--itops-ink);
            box-shadow: 0 12px 36px rgba(37, 86, 153, 0.07);
        }

        [data-testid="stTextInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus,
        [data-testid="stNumberInput"] input:focus {
            border-color: var(--itops-blue);
            box-shadow: 0 0 0 3px rgba(18, 107, 255, 0.16);
        }

        .trust-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin-top: 1.1rem;
        }

        .trust-chip {
            display: inline-flex;
            align-items: center;
            min-height: 2.45rem;
            padding: 0 1.1rem;
            border-radius: 8px;
            color: var(--itops-ink);
            font-size: 0.92rem;
            font-weight: 700;
            background: var(--itops-surface);
            border: 1px solid var(--itops-surface-border);
            box-shadow: 0 8px 24px rgba(43, 88, 150, 0.06);
        }

        .hero-visual {
            position: relative;
            min-height: 330px;
            overflow: hidden;
            border-radius: 8px;
            background:
                radial-gradient(circle at 52% 38%, rgba(18, 107, 255, 0.15), transparent 32%),
                linear-gradient(135deg, rgba(255, 255, 255, 0.35), rgba(235, 243, 255, 0.12));
        }

        .hero-visual::before,
        .hero-visual::after {
            content: "";
            position: absolute;
            inset: auto;
            background: rgba(18, 107, 255, 0.09);
            transform: rotate(-38deg);
        }

        .hero-visual::before {
            width: 240px;
            height: 90px;
            right: -14px;
            top: 10px;
            border-radius: 8px;
        }

        .hero-visual::after {
            width: 230px;
            height: 150px;
            right: 58px;
            bottom: 28px;
            border-radius: 8px;
        }

        .dot-grid {
            position: absolute;
            width: 86px;
            height: 70px;
            opacity: 0.55;
            background-image: radial-gradient(#8fb8ff 1.8px, transparent 1.8px);
            background-size: 12px 12px;
        }

        .dot-grid-a { left: 20px; top: 50px; }
        .dot-grid-b { right: 26px; top: 88px; }

        .laptop {
            position: absolute;
            width: 260px;
            height: 176px;
            right: 120px;
            top: 72px;
            transform: rotate(7deg);
            filter: drop-shadow(0 28px 38px rgba(20, 74, 146, 0.22));
        }

        .laptop-screen {
            position: absolute;
            inset: 0 22px 38px;
            border-radius: 8px 8px 4px 4px;
            background: linear-gradient(145deg, #0c3270, #126cff);
            border: 8px solid #0a1a39;
            overflow: hidden;
        }

        .screen-grid {
            position: absolute;
            inset: 0;
            opacity: 0.22;
            background-image:
                linear-gradient(rgba(255, 255, 255, 0.42) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.42) 1px, transparent 1px);
            background-size: 34px 28px;
        }

        .chart-line,
        .chart-line-two {
            position: absolute;
            height: 3px;
            border-radius: 99px;
            background: #27d7ff;
            transform-origin: left center;
            z-index: 2;
        }

        .chart-line {
            width: 128px;
            left: 35px;
            top: 62px;
            transform: rotate(-15deg);
            box-shadow: 40px -18px 0 #27d7ff, 78px 16px 0 #27d7ff;
        }

        .chart-line-two {
            width: 80px;
            left: 80px;
            top: 88px;
            transform: rotate(24deg);
            opacity: 0.5;
        }

        .laptop-base {
            position: absolute;
            left: 0;
            right: 0;
            bottom: 0;
            height: 48px;
            border-radius: 4px 4px 18px 18px;
            background: linear-gradient(180deg, #dbe8ff, #9eb8e9);
            transform: perspective(160px) rotateX(48deg);
        }

        .hero-shield {
            position: absolute;
            width: 72px;
            height: 84px;
            top: 96px;
            left: 118px;
            display: grid;
            place-items: center;
            color: #36d6ff;
            font-weight: 900;
            background: linear-gradient(145deg, #126cff, #074bc8);
            clip-path: polygon(50% 0, 94% 16%, 86% 72%, 50% 100%, 14% 72%, 6% 16%);
            filter: drop-shadow(0 18px 20px rgba(18, 107, 255, 0.25));
            animation: itops-pulse 2.6s ease-in-out infinite;
        }

        .hero-globe {
            position: absolute;
            width: 82px;
            height: 82px;
            border-radius: 50%;
            left: 50px;
            bottom: 76px;
            background:
                linear-gradient(90deg, transparent 45%, rgba(255, 255, 255, 0.95) 46% 54%, transparent 55%),
                linear-gradient(transparent 45%, rgba(255, 255, 255, 0.95) 46% 54%, transparent 55%),
                radial-gradient(circle, #8eb8ff, #387bff);
            box-shadow: 0 16px 28px rgba(18, 107, 255, 0.18);
            animation: itops-pulse 3.4s ease-in-out infinite;
            animation-delay: 0.6s;
        }

        .hero-globe span {
            position: absolute;
            inset: 14px 24px;
            border: 3px solid rgba(255, 255, 255, 0.9);
            border-radius: 50%;
        }

        .server-stack {
            position: absolute;
            width: 118px;
            right: 16px;
            bottom: 72px;
            display: grid;
            gap: 8px;
            filter: drop-shadow(0 16px 24px rgba(18, 107, 255, 0.18));
        }

        .server-stack div {
            height: 48px;
            border-radius: 8px;
            background: linear-gradient(145deg, #dceaff, #8fb8ff);
            border: 1px solid rgba(31, 111, 244, 0.25);
            position: relative;
        }

        .server-stack div::before {
            content: "";
            position: absolute;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            left: 14px;
            top: 19px;
            background: #126bff;
        }

        .server-stack div::after {
            content: "";
            position: absolute;
            width: 46px;
            height: 5px;
            border-radius: 99px;
            right: 16px;
            top: 21px;
            background: rgba(9, 64, 158, 0.25);
        }

        .section-heading {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 1.7rem 0 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--itops-line);
        }

        .section-heading > div {
            display: inline-flex;
            gap: 0.8rem;
            align-items: center;
        }

        .section-heading h2 {
            margin: 0;
            font-size: 1.45rem;
            font-weight: 800;
        }

        .section-bolt {
            color: var(--itops-blue);
            font-weight: 900;
        }

        [class*="st-key-tool_card_"] {
            height: 100%;
            border-radius: 8px;
            padding: 1.05rem;
            background: var(--itops-surface);
            border: 1px solid var(--itops-surface-border);
            box-shadow: 0 12px 32px rgba(36, 79, 135, 0.06);
        }

        [class*="st-key-tool_card_"] > div {
            height: 100%;
            display: flex;
            flex-direction: column;
            transition: transform 200ms cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 200ms ease;
        }

        [class*="st-key-tool_card_"] > div:hover {
            transform: translateY(-4px);
            box-shadow: 0 18px 36px rgba(0, 0, 0, 0.28);
        }

        .tool-card-shell {
            position: relative;
            min-height: 15.1rem;
            animation: itops-fade-up 0.45s cubic-bezier(0.22, 0.61, 0.36, 1) both;
        }

        .tool-card-badge-new {
            position: absolute;
            top: 0.75rem;
            right: 0.75rem;
            padding: 0.15rem 0.5rem;
            border-radius: 99px;
            font-size: 0.62rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            color: #ffffff;
            background: linear-gradient(135deg, var(--itops-green), color-mix(in srgb, var(--itops-green), #000 15%));
        }

        @keyframes itops-fade-up {
            from {
                opacity: 0;
                transform: translateY(14px);
            }
            to {
                opacity: 1;
                transform: none;
            }
        }

        @keyframes itops-pulse {
            0%, 100% {
                transform: scale(1);
                opacity: 1;
            }
            50% {
                transform: scale(1.06);
                opacity: 0.88;
            }
        }

        .tool-card-icon {
            width: 3.55rem;
            height: 3.55rem;
            display: grid;
            place-items: center;
            border-radius: 8px;
            margin-bottom: 1rem;
            color: #ffffff;
            font-size: 0.84rem;
            font-weight: 900;
            background: linear-gradient(145deg, color-mix(in srgb, var(--tool-accent), #ffffff 8%), var(--tool-accent));
            box-shadow: 0 14px 24px color-mix(in srgb, var(--tool-accent), transparent 75%);
        }

        .tool-card-shell h3 {
            margin: 0 0 0.65rem;
            font-size: 1.02rem;
            line-height: 1.25;
            font-weight: 800;
        }

        .tool-card-shell p {
            margin: 0;
            color: var(--itops-text-secondary);
            font-size: 0.92rem;
            line-height: 1.55;
        }

        [class*="st-key-tool_card_"] [data-testid="stPageLink"] a {
            border-radius: 8px;
            justify-content: center;
            color: #ffffff !important;
            font-weight: 800;
            background: linear-gradient(135deg, #2487ff, #0f66ee);
            min-height: 2.35rem;
            border: 0;
        }

        [class*="st-key-tool_card_"] [data-testid="stPageLink"] a * {
            color: inherit !important;
            fill: currentColor !important;
        }

        .feature-strip {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0;
            margin: 1.6rem 0 1.2rem;
            border: 1px solid var(--itops-surface-border);
            border-radius: 8px;
            background: var(--itops-surface);
            overflow: hidden;
        }

        .feature-item {
            display: flex;
            gap: 0.9rem;
            padding: 1.15rem 1rem;
            border-right: 1px solid var(--itops-surface-border);
        }

        .feature-item:last-child {
            border-right: 0;
        }

        .feature-item strong {
            display: block;
            margin-bottom: 0.35rem;
            color: var(--itops-ink);
            font-size: 0.95rem;
        }

        .feature-item p {
            margin: 0;
            color: var(--itops-text-secondary);
            font-size: 0.82rem;
            line-height: 1.45;
        }

        .feature-icon {
            width: 2.8rem;
            height: 2.8rem;
            flex: 0 0 2.8rem;
            display: grid;
            place-items: center;
            border-radius: 8px;
            font-size: 0.74rem;
            font-weight: 900;
            border: 2px solid currentColor;
            background: var(--itops-surface-strong);
            transition: transform 180ms cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        .feature-item:hover .feature-icon {
            transform: scale(1.08) rotate(-3deg);
        }

        .feature-blue { color: var(--itops-blue); }
        .feature-purple { color: var(--itops-purple); }
        .feature-green { color: var(--itops-green); }
        .feature-orange { color: var(--itops-orange); }

        .important-notice {
            display: flex;
            gap: 1rem;
            align-items: center;
            padding: 1rem 1.15rem;
            border-radius: 8px;
            border: 1px solid #f0d08a;
            background: linear-gradient(135deg, rgba(255, 189, 24, 0.13), var(--itops-surface));
        }

        .important-notice strong {
            color: var(--itops-ink);
            font-size: 0.95rem;
        }

        .important-notice p {
            margin: 0.2rem 0 0;
            color: var(--itops-text-secondary);
            font-size: 0.9rem;
            line-height: 1.45;
        }

        .notice-icon {
            width: 2.5rem;
            height: 2.5rem;
            flex: 0 0 2.5rem;
            border-radius: 50%;
            display: grid;
            place-items: center;
            background: #f8b400;
            color: #ffffff;
            font-weight: 900;
        }

        .tool-page-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
            border-radius: 8px;
            border: 1px solid var(--itops-surface-border);
            background: var(--itops-surface);
            box-shadow: 0 12px 32px rgba(36, 79, 135, 0.05);
        }

        .tool-page-icon {
            width: 3.15rem;
            height: 3.15rem;
            display: grid;
            place-items: center;
            border-radius: 8px;
            background: linear-gradient(145deg, color-mix(in srgb, var(--tool-accent), #ffffff 8%), var(--tool-accent));
            color: #ffffff;
            font-weight: 900;
            font-size: 0.76rem;
        }

        .tool-page-header h1 {
            margin: 0;
            font-size: clamp(1.55rem, 3vw, 2.25rem);
            line-height: 1.05;
            font-weight: 800;
        }

        .tool-page-header p {
            margin: 0.35rem 0 0;
            color: var(--itops-text-secondary);
            line-height: 1.5;
        }

        [class*="st-key-tool_form_panel_"],
        [class*="st-key-tool_result_panel_"] {
            border: 1px solid var(--itops-surface-border);
            border-radius: 8px;
            background: var(--itops-surface);
            box-shadow: 0 12px 32px rgba(36, 79, 135, 0.045);
            padding: 1rem 1rem 1.1rem;
            margin: 1rem 0;
        }

        [class*="st-key-tool_form_panel_"] {
            background:
                linear-gradient(135deg, var(--itops-surface), color-mix(in srgb, var(--itops-surface), var(--itops-blue) 6%));
        }

        .tool-form-intro,
        .tool-section-heading {
            margin-bottom: 0.85rem;
        }

        .tool-form-intro h2,
        .tool-section-heading h2 {
            margin: 0.15rem 0 0.25rem;
            color: var(--itops-ink);
            font-size: clamp(1.05rem, 1.7vw, 1.35rem);
            font-weight: 800;
            line-height: 1.2;
        }

        .tool-form-intro p,
        .tool-section-heading p {
            margin: 0;
            max-width: 44rem;
            color: var(--itops-muted);
            font-size: 0.92rem;
            line-height: 1.55;
        }

        .tool-panel-eyebrow {
            color: var(--itops-blue);
            font-size: 0.72rem;
            font-weight: 900;
            letter-spacing: 0;
            text-transform: uppercase;
        }

        .tool-empty-state {
            display: flex;
            gap: 0.9rem;
            align-items: center;
            border: 1px dashed var(--itops-surface-border);
            border-radius: 8px;
            background: var(--itops-surface);
            padding: 0.95rem 1rem;
            margin: 1rem 0;
        }

        .tool-empty-mark {
            width: 2.45rem;
            height: 2.45rem;
            flex: 0 0 2.45rem;
            display: grid;
            place-items: center;
            border-radius: 8px;
            color: #ffffff;
            font-size: 0.72rem;
            font-weight: 900;
            background: linear-gradient(145deg, #278aff, #0f67f2);
        }

        .tool-empty-state strong,
        .tool-safe-note strong {
            color: var(--itops-ink);
            font-size: 0.95rem;
        }

        .tool-empty-state p,
        .tool-safe-note p {
            margin: 0.18rem 0 0;
            color: var(--itops-muted);
            font-size: 0.88rem;
            line-height: 1.45;
        }

        .tool-safe-note {
            border: 1px solid rgba(34, 186, 79, 0.28);
            border-radius: 8px;
            background: rgba(34, 186, 79, 0.08);
            padding: 0.85rem 1rem;
            margin: 0.8rem 0;
        }

        .tool-status-note {
            display: flex;
            gap: 0.85rem;
            align-items: flex-start;
            border-radius: 8px;
            padding: 0.9rem 1rem;
            margin: 0.85rem 0 1rem;
            border: 1px solid var(--itops-surface-border);
            background: var(--itops-surface);
        }

        .tool-status-mark {
            width: 2.2rem;
            height: 2.2rem;
            flex: 0 0 2.2rem;
            display: grid;
            place-items: center;
            border-radius: 8px;
            color: #ffffff;
            font-size: 0.72rem;
            font-weight: 900;
            background: var(--itops-blue);
        }

        .tool-status-note strong {
            color: var(--itops-ink);
            font-size: 0.95rem;
        }

        .tool-status-note p {
            margin: 0.18rem 0 0;
            color: var(--itops-text-secondary);
            font-size: 0.9rem;
            line-height: 1.55;
            overflow-wrap: anywhere;
        }

        .tool-status-note-ai,
        .tool-status-note-info {
            border-color: rgba(18, 107, 255, 0.22);
            /* Fixed blue, not var(--itops-blue) -- that token is the
               theme accent (coral/red in dark mode, matching odysseus),
               not a literal blue, and would clash with the badge icon's
               hardcoded blue gradient just below. */
            background: color-mix(in srgb, var(--itops-surface), #126bff 12%);
        }

        .tool-status-note-ai .tool-status-mark,
        .tool-status-note-info .tool-status-mark {
            background: linear-gradient(145deg, #278aff, #0f67f2);
        }

        .tool-status-note-success {
            border-color: rgba(34, 186, 79, 0.24);
            background: color-mix(in srgb, var(--itops-surface), var(--itops-green) 12%);
        }

        .tool-status-note-success .tool-status-mark {
            background: linear-gradient(145deg, #30d968, #19a946);
        }

        .tool-status-note-warning {
            border-color: rgba(255, 106, 19, 0.25);
            background: color-mix(in srgb, var(--itops-surface), var(--itops-orange) 12%);
        }

        .tool-status-note-warning .tool-status-mark {
            background: linear-gradient(145deg, #ff8a3d, #ff6a13);
        }

        .tool-status-note-neutral {
            border-color: var(--itops-surface-border);
            background: var(--itops-surface);
        }

        .tool-status-note-neutral .tool-status-mark {
            background: #7a8da8;
        }

        [class*="st-key-tool_download_panel_"] {
            border: 1px solid var(--itops-surface-border);
            border-radius: 8px;
            background: var(--itops-surface);
            padding: 1rem;
            margin-top: 1rem;
        }

        div[data-testid="stAlert"] {
            border-radius: 8px;
        }

        .roadmap-hero {
            display: flex;
            justify-content: space-between;
            gap: 1.25rem;
            align-items: flex-start;
            padding: 0.85rem 0 0.9rem;
            border-bottom: 1px solid var(--itops-line);
            margin-bottom: 0.85rem;
        }

        .roadmap-kicker {
            color: var(--itops-blue);
            font-size: 0.74rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .roadmap-hero h1 {
            margin: 0.16rem 0 0.38rem;
            font-size: clamp(2rem, 3.4vw, 3rem);
            line-height: 1;
            font-weight: 800;
        }

        .roadmap-hero p {
            max-width: 42rem;
            margin: 0;
            color: var(--itops-text-secondary);
            font-size: 0.98rem;
            line-height: 1.55;
        }

        .roadmap-tab-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.9rem;
            align-items: center;
            margin-top: 0.8rem;
        }

        .roadmap-tab-row span,
        .roadmap-tab-row a {
            color: var(--itops-muted);
            text-decoration: none !important;
            font-size: 0.9rem;
            font-weight: 800;
        }

        .roadmap-tab-row .roadmap-tab-active {
            color: var(--itops-blue);
        }

        .roadmap-actions {
            display: flex;
            gap: 0.7rem;
            align-items: center;
            flex-wrap: wrap;
            justify-content: flex-end;
            padding-top: 0.05rem;
        }

        .roadmap-actions a,
        .roadmap-footer-note a {
            min-height: 2.55rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            padding: 0 1rem;
            text-decoration: none !important;
            font-size: 0.88rem;
            font-weight: 900;
            white-space: nowrap;
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease, background 160ms ease;
        }

        .roadmap-submit-link {
            color: #ffffff !important;
            background: linear-gradient(135deg, #2487ff, #0f66ee);
            box-shadow: 0 12px 24px rgba(13, 103, 242, 0.2);
        }

        .roadmap-submit-link:hover,
        .roadmap-footer-note a:hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 28px rgba(13, 103, 242, 0.24);
        }

        .roadmap-secondary-link {
            color: var(--itops-ink) !important;
            background: var(--itops-surface);
            border: 1px solid var(--itops-surface-border);
        }

        .roadmap-secondary-link:hover {
            border-color: rgba(18, 107, 255, 0.38);
            background: #ffffff;
        }

        .roadmap-notice-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0.85rem 0 0.9rem;
        }

        .roadmap-notice {
            display: grid;
            grid-template-columns: 2rem minmax(0, 1fr);
            gap: 0.75rem;
            align-items: start;
            min-height: 4.2rem;
            padding: 0.85rem 0.95rem;
            border: 1px solid var(--itops-surface-border);
            border-radius: 8px;
            background: var(--itops-surface);
        }

        .roadmap-notice-mark {
            width: 2rem;
            height: 2rem;
            display: grid;
            place-items: center;
            border-radius: 8px;
            color: #ffffff;
            font-size: 0.72rem;
            font-weight: 900;
            background: var(--itops-blue);
        }

        .roadmap-notice strong {
            display: block;
            color: var(--itops-ink);
            font-size: 0.88rem;
            line-height: 1.25;
        }

        .roadmap-notice p {
            margin: 0.18rem 0 0;
            color: var(--itops-text-secondary);
            font-size: 0.82rem;
            line-height: 1.45;
        }

        .roadmap-notice-warning {
            border-color: rgba(255, 106, 19, 0.28);
            background: color-mix(in srgb, var(--itops-surface), var(--itops-orange) 12%);
        }

        .roadmap-notice-warning .roadmap-notice-mark {
            background: linear-gradient(145deg, #ff8a3d, #ff6a13);
        }

        .roadmap-notice-ai {
            border-color: rgba(18, 107, 255, 0.24);
            /* Fixed blue, not var(--itops-blue) -- see .tool-status-note-ai. */
            background: color-mix(in srgb, var(--itops-surface), #126bff 12%);
        }

        .roadmap-notice-ai .roadmap-notice-mark {
            background: linear-gradient(145deg, #278aff, #0f67f2);
        }

        .roadmap-notice-neutral {
            margin: 0.85rem 0 0.9rem;
            border-color: var(--itops-surface-border);
            background: var(--itops-surface);
        }

        .roadmap-notice-neutral .roadmap-notice-mark {
            background: #7a8da8;
        }

        .roadmap-section-label {
            margin: 0.1rem 0 0.55rem;
            color: var(--itops-ink);
            font-size: 0.92rem;
            font-weight: 900;
        }

        .roadmap-board-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0 0 0.95rem;
        }

        .roadmap-board-card {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            min-height: 3.15rem;
            padding: 0.8rem 0.95rem;
            border-radius: 8px;
            border: 1px solid var(--itops-surface-border);
            background: var(--itops-surface);
            box-shadow: 0 10px 24px rgba(36, 79, 135, 0.04);
            transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
        }

        .roadmap-board-card:hover {
            transform: translateY(-1px);
            border-color: rgba(18, 107, 255, 0.32);
            background: var(--itops-surface);
        }

        .roadmap-board-card span {
            color: var(--itops-ink);
            font-size: 0.92rem;
            font-weight: 800;
        }

        .roadmap-board-card strong {
            color: #667790;
            font-size: 0.88rem;
            font-weight: 900;
        }

        .roadmap-summary-line {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin: 0.45rem 0 0.85rem;
            color: var(--itops-muted);
            font-size: 0.88rem;
        }

        .roadmap-summary-line strong {
            color: var(--itops-ink);
        }

        .roadmap-columns-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.9rem;
            align-items: stretch;
            margin-bottom: 1.1rem;
        }

        .roadmap-column {
            height: 38rem;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            padding: 0;
            border: 1px solid var(--itops-surface-border);
            border-radius: 8px;
            background: var(--itops-surface);
            box-shadow: 0 12px 30px rgba(36, 79, 135, 0.035);
        }

        .roadmap-column-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex: 0 0 auto;
            min-height: 3.15rem;
            padding: 0.78rem 0.9rem;
            border-bottom: 1px solid #d7e2f5;
            background: rgba(251, 253, 255, 0.96);
        }

        .roadmap-column-title > .roadmap-status-dot {
            width: 0.52rem;
            height: 0.52rem;
            flex: 0 0 0.52rem;
            border-radius: 50%;
            background: #2e8bff;
        }

        .roadmap-column-name {
            margin: 0;
            padding: 0 !important;
            flex: 1;
            color: var(--itops-ink);
            font-size: 0.95rem;
            line-height: 1.25;
            font-weight: 900;
        }

        .roadmap-column-title strong {
            color: #667790;
            font-size: 0.82rem;
            font-weight: 900;
        }

        .roadmap-column-planned .roadmap-status-dot { background: #2e8bff; }
        .roadmap-column-progress .roadmap-status-dot { background: #8a61f2; }
        .roadmap-column-done .roadmap-status-dot { background: #22ba4f; }
        .roadmap-column-ai .roadmap-status-dot { background: #11aab8; }

        .roadmap-column-list {
            flex: 1;
            min-height: 0;
            overflow-y: auto;
            padding: 0 0.9rem;
            scrollbar-width: thin;
            scrollbar-color: #b5c8e4 transparent;
        }

        .roadmap-column-list::-webkit-scrollbar {
            width: 0.45rem;
        }

        .roadmap-column-list::-webkit-scrollbar-thumb {
            border-radius: 999px;
            background: #b5c8e4;
        }

        .roadmap-item-card {
            display: grid;
            grid-template-columns: 2.35rem minmax(0, 1fr);
            gap: 0.72rem;
            align-items: start;
            padding: 0.85rem 0;
            border-bottom: 1px solid #e1e9f7;
        }

        .roadmap-item-card:last-child {
            border-bottom: 0;
        }

        .roadmap-vote-pill {
            width: 2.35rem;
            min-height: 2.5rem;
            align-self: start;
            border: 1px solid var(--itops-surface-border);
            border-radius: 8px;
            display: grid;
            place-items: center;
            align-content: center;
            color: #3d4f68;
            background: var(--itops-surface);
            font-size: 0.75rem;
            font-weight: 850;
            line-height: 1.1;
        }

        .roadmap-vote-pill span {
            color: #667790;
            font-weight: 900;
        }

        .roadmap-item-body {
            min-width: 0;
        }

        .roadmap-card-title {
            margin: 0;
            padding: 0 !important;
            color: var(--itops-ink);
            font-size: 0.92rem;
            line-height: 1.32;
            font-weight: 900;
            overflow-wrap: anywhere;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .roadmap-card-title a {
            color: inherit !important;
            text-decoration: none !important;
        }

        .roadmap-card-title a:hover {
            color: var(--itops-blue) !important;
            text-decoration: underline !important;
        }

        .roadmap-card-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            align-items: center;
            margin-top: 0.5rem;
        }

        .roadmap-item-category,
        .roadmap-status-badge,
        .roadmap-source-badge {
            display: inline-flex;
            align-items: center;
            min-height: 1.25rem;
            border-radius: 8px;
            padding: 0 0.45rem;
            color: #667790;
            font-size: 0.68rem;
            line-height: 1.2;
            font-weight: 900;
            text-transform: uppercase;
        }

        .roadmap-item-category {
            padding-left: 0;
        }

        .roadmap-status-badge {
            color: #0d4fbd;
            background: rgba(18, 107, 255, 0.1);
        }

        .roadmap-source-badge {
            color: #23663b;
            background: rgba(34, 186, 79, 0.1);
        }

        .roadmap-source-github {
            color: #4b3bb0;
            background: rgba(109, 85, 233, 0.12);
        }

        .roadmap-item-body p {
            margin: 0.42rem 0 0;
            padding: 0 !important;
            color: var(--itops-text-secondary);
            font-size: 0.8rem;
            line-height: 1.45;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .roadmap-item-body small {
            display: block;
            margin-top: 0.38rem;
            color: #64758e;
            font-size: 0.72rem;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .roadmap-empty-column {
            margin: 1rem 0;
            padding: 1rem;
            border: 1px dashed var(--itops-surface-border);
            border-radius: 8px;
            background: var(--itops-surface);
        }

        .roadmap-empty-column strong {
            color: var(--itops-ink);
            font-size: 0.92rem;
        }

        .roadmap-empty-column p {
            margin: 0.25rem 0 0;
            color: var(--itops-muted);
            font-size: 0.84rem;
            line-height: 1.45;
        }

        .roadmap-footer-note {
            display: flex;
            gap: 0.8rem;
            align-items: center;
            justify-content: space-between;
            margin-top: 1rem;
            padding: 0.85rem 0.95rem;
            border: 1px solid rgba(18, 107, 255, 0.2);
            border-radius: 8px;
            /* Fixed blue, not var(--itops-blue) -- see .tool-status-note-ai. */
            background: color-mix(in srgb, var(--itops-surface), #126bff 12%);
        }

        .roadmap-footer-note strong {
            color: var(--itops-ink);
            font-size: 0.94rem;
            white-space: nowrap;
        }

        .roadmap-footer-note span {
            flex: 1;
            color: var(--itops-text-secondary);
            font-size: 0.88rem;
            line-height: 1.45;
        }

        .roadmap-footer-note a {
            color: #ffffff !important;
            background: linear-gradient(135deg, #2487ff, #0f66ee);
        }

        button[kind="primary"],
        button[kind="secondary"],
        .stDownloadButton button,
        .stFormSubmitButton button {
            border-radius: 8px !important;
            font-weight: 800 !important;
        }

        @media (max-width: 1100px) {
            .feature-strip {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .feature-item {
                border-right: 0;
                border-bottom: 1px solid var(--itops-surface-border);
            }

            .hero-visual {
                min-height: 280px;
            }

            .roadmap-board-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .roadmap-columns-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .roadmap-column {
                height: auto;
                min-height: 24rem;
                margin-bottom: 0.9rem;
            }

            .roadmap-column-list {
                overflow: visible;
            }
        }

        @media (max-width: 720px) {
            .block-container {
                padding: 1.2rem 1rem 2rem;
            }

            .home-hero-copy {
                padding-top: 0.3rem;
            }

            .hero-visual {
                min-height: 230px;
            }

            .laptop {
                right: 62px;
                transform: scale(0.74) rotate(7deg);
                transform-origin: top right;
            }

            .hero-shield {
                left: 72px;
                transform: scale(0.82);
            }

            .server-stack {
                right: 4px;
                transform: scale(0.76);
                transform-origin: bottom right;
            }

            .feature-strip {
                grid-template-columns: 1fr;
            }

            .important-notice,
            .tool-page-header,
            .tool-status-note {
                align-items: flex-start;
            }

            .roadmap-hero,
            .roadmap-summary-line,
            .roadmap-footer-note {
                display: block;
            }

            .roadmap-actions {
                justify-content: flex-start;
                margin-top: 1rem;
            }

            .roadmap-notice-grid {
                grid-template-columns: 1fr;
            }

            .roadmap-board-grid {
                grid-template-columns: 1fr;
            }

            .roadmap-columns-grid {
                grid-template-columns: 1fr;
            }

            .roadmap-column-title {
                padding-left: 3.75rem;
            }

            .roadmap-footer-note span {
                display: block;
                margin: 0.35rem 0 0.8rem;
            }
        }
        </style>
        """
    css = css.replace("__ITOPS_ROOT_VARS__", root_vars)
    st.markdown(css, unsafe_allow_html=True)
