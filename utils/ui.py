"""Shared Streamlit UI shell and design helpers."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any, Iterable

import pandas as pd
import streamlit as st

from utils.project_links import github_repository_url


@dataclass(frozen=True)
class ToolMeta:
    title: str
    short_title: str
    description: str
    path: str
    icon: str
    accent: str
    slug: str


TOOLS: tuple[ToolMeta, ...] = (
    ToolMeta(
        title="Domain Health Checker",
        short_title="Domain Health Checker",
        description="Complete domain health check including DNS, SSL, HTTP, and security.",
        path="pages/1_Domain_Health_Checker.py",
        icon="GLB",
        accent="#1668f4",
        slug="domain_health",
    ),
    ToolMeta(
        title="DNS Record Checker",
        short_title="DNS Record Checker",
        description="Look up DNS records including A, MX, TXT, SPF, DMARC, and more.",
        path="pages/2_DNS_Record_Checker.py",
        icon="DNS",
        accent="#23b84d",
        slug="dns_records",
    ),
    ToolMeta(
        title="SSL Certificate Checker",
        short_title="SSL Certificate Checker",
        description="Check SSL certificate details, validity, issuer, subject, and expiration.",
        path="pages/3_SSL_Certificate_Checker.py",
        icon="LOCK",
        accent="#7047e8",
        slug="ssl_certificate",
    ),
    ToolMeta(
        title="HTTP Status Checker",
        short_title="HTTP Status Checker",
        description="Check website status, response time, redirects, and security headers.",
        path="pages/4_HTTP_Status_Checker.py",
        icon="HTTP",
        accent="#ff6b13",
        slug="http_status",
    ),
    ToolMeta(
        title="JSON Formatter",
        short_title="JSON Formatter",
        description="Format, validate, and minify your JSON instantly.",
        path="pages/5_JSON_Formatter.py",
        icon="{ }",
        accent="#11aab8",
        slug="json_formatter",
    ),
    ToolMeta(
        title="Base64 Tool",
        short_title="Base64 Tool",
        description="Encode and decode Base64 text safely in your browser session.",
        path="pages/6_Base64_Tool.py",
        icon="64",
        accent="#0f7ff0",
        slug="base64_tool",
    ),
    ToolMeta(
        title="JWT Decoder",
        short_title="JWT Decoder",
        description="Decode JWT headers and payloads locally without signature verification.",
        path="pages/7_JWT_Decoder.py",
        icon="JWT",
        accent="#3d5be9",
        slug="jwt_decoder",
    ),
    ToolMeta(
        title="Cron Explainer",
        short_title="Cron Explainer",
        description="Explain common 5-field cron expressions and preview upcoming runs.",
        path="pages/8_Cron_Explainer.py",
        icon="CLK",
        accent="#6f55e9",
        slug="cron_explainer",
    ),
    ToolMeta(
        title="Log Troubleshooting Assistant",
        short_title="Log Troubleshooting",
        description="Find common operational error patterns in pasted logs.",
        path="pages/9_Log_Troubleshooting_Assistant.py",
        icon="LOG",
        accent="#1d78f0",
        slug="log_troubleshooting",
    ),
)

POPULAR_TOOLS = TOOLS[:5]


def apply_app_shell(active_page: str) -> None:
    """Apply global theme CSS and render the shared sidebar shell."""
    _inject_global_css()
    render_sidebar(active_page)


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
            <div class="sidebar-section-label">Navigation</div>
            """,
            unsafe_allow_html=True,
        )
        _sidebar_link("Home", "app.py", active_page == "Home", ":material/home:")
        _sidebar_link(
            "Roadmap & Feedback",
            "pages/10_Roadmap_Feedback.py",
            active_page == "Roadmap & Feedback",
            ":material/route:",
        )
        for tool in TOOLS:
            _sidebar_link(tool.short_title, tool.path, active_page == tool.title, _material_icon_for(tool.slug))

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


def render_tool_section(tools: Iterable[ToolMeta], query: str = "") -> None:
    """Render the home page tool card grid."""
    tools = tuple(tools)
    section_label = "Matching Tools" if query.strip() else "Popular Tools"
    st.markdown(
        f"""
        <div class="section-heading" id="all-tools">
            <div><span class="section-bolt">IT</span><h2>{escape(section_label)}</h2></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not tools:
        st.info("No tools match your search.")
        return

    cols = st.columns(min(len(tools), 5), gap="large")
    for index, tool in enumerate(tools):
        with cols[index % len(cols)]:
            with st.container(key=f"tool_card_{tool.slug}"):
                st.markdown(_tool_card_html(tool), unsafe_allow_html=True)
                _safe_page_link(tool.path, label="Open Tool", icon=":material/arrow_forward:", stretch_width=True)


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
    description_html = f"<p>{escape(description)}</p>" if description else ""
    st.markdown(
        f"""
        <div class="tool-section-heading">
            <div class="tool-panel-eyebrow">{escape(eyebrow)}</div>
            <h2>{escape(title)}</h2>
            {description_html}
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


def filter_tools(query: str) -> tuple[ToolMeta, ...]:
    value = query.strip().lower()
    if not value:
        return POPULAR_TOOLS
    return tuple(
        tool
        for tool in TOOLS
        if value in tool.title.lower()
        or value in tool.short_title.lower()
        or value in tool.description.lower()
        or value in tool.slug.replace("_", " ")
    )


def tool_by_title(title: str) -> ToolMeta | None:
    return next((tool for tool in TOOLS if tool.title == title), None)


def github_url() -> str | None:
    return github_repository_url()


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


def _tool_card_html(tool: ToolMeta) -> str:
    return f"""
    <div class="tool-card-shell" style="--tool-accent: {tool.accent};">
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
    }
    return icons.get(slug, ":material/build:")


def _key_slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_")


def _inject_global_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

        :root {
            --itops-blue: #126bff;
            --itops-blue-dark: #0a47c9;
            --itops-ink: #07142f;
            --itops-muted: #52637f;
            --itops-line: #d7e2f5;
            --itops-bg: #f6f9ff;
            --itops-panel: #fbfdff;
            --itops-sidebar: #071a33;
            --itops-sidebar-2: #0b2748;
            --itops-green: #22ba4f;
            --itops-purple: #6d55e9;
            --itops-orange: #ff6a13;
            --card-radius: 8px;
        }

        html,
        body {
            background: var(--itops-bg);
        }

        .stApp {
            background:
                radial-gradient(circle at 70% 0%, rgba(18, 107, 255, 0.12), transparent 30%),
                linear-gradient(180deg, #fbfdff 0%, var(--itops-bg) 48%, #eef5ff 100%);
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
            color: #4b5d7b;
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
            border: 1px solid #b9c9e5;
            background: #ffffff;
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
            color: #0d1b36;
            font-size: 0.92rem;
            font-weight: 700;
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid #cddaf0;
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
            background: rgba(255, 255, 255, 0.84);
            border: 1px solid #d4e0f2;
            box-shadow: 0 12px 32px rgba(36, 79, 135, 0.06);
        }

        [class*="st-key-tool_card_"] > div {
            height: 100%;
            display: flex;
            flex-direction: column;
        }

        .tool-card-shell {
            min-height: 15.1rem;
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
            color: #334765;
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
            border: 1px solid #d4e0f2;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.82);
            overflow: hidden;
        }

        .feature-item {
            display: flex;
            gap: 0.9rem;
            padding: 1.15rem 1rem;
            border-right: 1px solid #dbe5f5;
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
            color: #334765;
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
            background: #ffffff;
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
            background: linear-gradient(135deg, rgba(255, 189, 24, 0.13), rgba(255, 255, 255, 0.88));
        }

        .important-notice strong {
            color: var(--itops-ink);
            font-size: 0.95rem;
        }

        .important-notice p {
            margin: 0.2rem 0 0;
            color: #334765;
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
            border: 1px solid #d4e0f2;
            background: rgba(255, 255, 255, 0.82);
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
            color: #52637f;
            line-height: 1.5;
        }

        [class*="st-key-tool_form_panel_"],
        [class*="st-key-tool_result_panel_"] {
            border: 1px solid #d4e0f2;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.78);
            box-shadow: 0 12px 32px rgba(36, 79, 135, 0.045);
            padding: 1rem 1rem 1.1rem;
            margin: 1rem 0;
        }

        [class*="st-key-tool_form_panel_"] {
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(242, 247, 255, 0.84));
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
            color: #52637f;
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
            border: 1px dashed #bdd0ef;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.58);
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
            color: #52637f;
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
            border: 1px solid #cddaf0;
            background: rgba(255, 255, 255, 0.76);
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
            color: #334765;
            font-size: 0.9rem;
            line-height: 1.55;
            overflow-wrap: anywhere;
        }

        .tool-status-note-ai,
        .tool-status-note-info {
            border-color: rgba(18, 107, 255, 0.22);
            background: linear-gradient(135deg, rgba(231, 240, 255, 0.94), rgba(255, 255, 255, 0.84));
        }

        .tool-status-note-ai .tool-status-mark,
        .tool-status-note-info .tool-status-mark {
            background: linear-gradient(145deg, #278aff, #0f67f2);
        }

        .tool-status-note-success {
            border-color: rgba(34, 186, 79, 0.24);
            background: linear-gradient(135deg, rgba(231, 248, 238, 0.9), rgba(255, 255, 255, 0.84));
        }

        .tool-status-note-success .tool-status-mark {
            background: linear-gradient(145deg, #30d968, #19a946);
        }

        .tool-status-note-warning {
            border-color: rgba(255, 106, 19, 0.25);
            background: linear-gradient(135deg, rgba(255, 240, 231, 0.9), rgba(255, 255, 255, 0.86));
        }

        .tool-status-note-warning .tool-status-mark {
            background: linear-gradient(145deg, #ff8a3d, #ff6a13);
        }

        .tool-status-note-neutral {
            border-color: #d4e0f2;
            background: rgba(255, 255, 255, 0.7);
        }

        .tool-status-note-neutral .tool-status-mark {
            background: #7a8da8;
        }

        [class*="st-key-tool_download_panel_"] {
            border: 1px solid #d4e0f2;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.72);
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
            padding: 1.25rem 0 1rem;
            border-bottom: 1px solid var(--itops-line);
            margin-bottom: 1rem;
        }

        .roadmap-kicker {
            color: var(--itops-blue);
            font-size: 0.74rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .roadmap-hero h1 {
            margin: 0.2rem 0 0.45rem;
            font-size: clamp(2rem, 4vw, 3.45rem);
            line-height: 1;
            font-weight: 800;
        }

        .roadmap-hero p {
            max-width: 42rem;
            margin: 0;
            color: #4b5d7b;
            font-size: 1rem;
            line-height: 1.65;
        }

        .roadmap-tab-row {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            align-items: center;
            margin-top: 1rem;
        }

        .roadmap-tab-row span,
        .roadmap-tab-row a {
            color: #52637f;
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
            padding-top: 0.2rem;
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
        }

        .roadmap-submit-link {
            color: #ffffff !important;
            background: linear-gradient(135deg, #2487ff, #0f66ee);
            box-shadow: 0 12px 24px rgba(13, 103, 242, 0.2);
        }

        .roadmap-secondary-link {
            color: var(--itops-ink) !important;
            background: rgba(255, 255, 255, 0.85);
            border: 1px solid #cddaf0;
        }

        .roadmap-board-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.85rem;
            margin: 1rem 0 1.1rem;
        }

        .roadmap-board-card {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            min-height: 3.4rem;
            padding: 0.9rem 1rem;
            border-radius: 8px;
            border: 1px solid #cddaf0;
            background: rgba(255, 255, 255, 0.8);
            box-shadow: 0 10px 24px rgba(36, 79, 135, 0.04);
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
            margin: 0.6rem 0 1rem;
            color: #52637f;
            font-size: 0.88rem;
        }

        .roadmap-summary-line strong {
            color: var(--itops-ink);
        }

        .roadmap-column {
            min-height: 33rem;
            max-height: 42rem;
            overflow-y: auto;
            padding: 0.95rem;
            border: 1px solid #cddaf0;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.72);
        }

        .roadmap-column-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            position: sticky;
            top: 0;
            z-index: 2;
            margin: -0.95rem -0.95rem 0.8rem;
            padding: 0.95rem;
            border-bottom: 1px solid #d7e2f5;
            background: rgba(251, 253, 255, 0.96);
        }

        .roadmap-column-title span {
            width: 0.52rem;
            height: 0.52rem;
            flex: 0 0 0.52rem;
            border-radius: 50%;
            background: #2e8bff;
        }

        .roadmap-column-title h2 {
            margin: 0;
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

        .roadmap-column-planned .roadmap-column-title span { background: #2e8bff; }
        .roadmap-column-progress .roadmap-column-title span { background: #8a61f2; }
        .roadmap-column-done .roadmap-column-title span { background: #22ba4f; }
        .roadmap-column-ai .roadmap-column-title span { background: #11aab8; }

        .roadmap-item-card {
            display: grid;
            grid-template-columns: 2.5rem minmax(0, 1fr);
            gap: 0.85rem;
            padding: 0.85rem 0;
            border-bottom: 1px solid #e1e9f7;
        }

        .roadmap-item-card:last-child {
            border-bottom: 0;
        }

        .roadmap-vote-pill {
            min-height: 2.65rem;
            border: 1px solid #d4e0f2;
            border-radius: 8px;
            display: grid;
            place-items: center;
            align-content: center;
            color: #3d4f68;
            background: rgba(255, 255, 255, 0.78);
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

        .roadmap-item-body h3 {
            margin: 0;
            color: var(--itops-ink);
            font-size: 0.96rem;
            line-height: 1.35;
            font-weight: 900;
            overflow-wrap: anywhere;
        }

        .roadmap-card-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            align-items: center;
            margin-top: 0.35rem;
        }

        .roadmap-item-category,
        .roadmap-status-badge {
            display: inline-flex;
            align-items: center;
            min-height: 1.35rem;
            border-radius: 8px;
            padding: 0 0.45rem;
            color: #667790;
            font-size: 0.74rem;
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

        .roadmap-item-body p {
            margin: 0.5rem 0 0;
            color: #334765;
            font-size: 0.86rem;
            line-height: 1.5;
        }

        .roadmap-item-body small {
            display: block;
            margin-top: 0.45rem;
            color: #64758e;
            font-size: 0.78rem;
            line-height: 1.45;
        }

        .roadmap-empty-column {
            padding: 1rem;
            border: 1px dashed #bdd0ef;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.56);
        }

        .roadmap-empty-column strong {
            color: var(--itops-ink);
            font-size: 0.92rem;
        }

        .roadmap-empty-column p {
            margin: 0.25rem 0 0;
            color: #52637f;
            font-size: 0.84rem;
            line-height: 1.45;
        }

        .roadmap-footer-note {
            display: flex;
            gap: 0.8rem;
            align-items: center;
            justify-content: space-between;
            margin-top: 1.2rem;
            padding: 0.9rem 1rem;
            border: 1px solid rgba(18, 107, 255, 0.2);
            border-radius: 8px;
            background: linear-gradient(135deg, rgba(231, 240, 255, 0.94), rgba(255, 255, 255, 0.84));
        }

        .roadmap-footer-note strong {
            color: var(--itops-ink);
            font-size: 0.94rem;
            white-space: nowrap;
        }

        .roadmap-footer-note span {
            flex: 1;
            color: #334765;
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
                border-bottom: 1px solid #dbe5f5;
            }

            .hero-visual {
                min-height: 280px;
            }

            .roadmap-board-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .roadmap-column {
                min-height: 24rem;
                max-height: none;
                margin-bottom: 0.9rem;
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

            .roadmap-board-grid {
                grid-template-columns: 1fr;
            }

            .roadmap-footer-note span {
                display: block;
                margin: 0.35rem 0 0.8rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
