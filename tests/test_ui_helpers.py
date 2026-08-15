from pathlib import Path

from utils import ui
from utils.ui import (
    POPULAR_TOOLS,
    PROFESSIONS,
    SHARED_FAVORITES_PARAM,
    SIDEBAR_CATEGORIES,
    TITLE_TO_SLUG,
    TOOLS,
    TOOL_BUNDLES,
    display_rows_frame,
    favorite_tools,
    favorites_share_link,
    filter_tools,
    guided_workflows,
    move_favorite,
    record_recent_visit,
    recent_or_popular_tools,
    related_tools,
    shared_favorite_tools,
    sort_tools,
    toggle_favorite,
)


def test_display_rows_frame_stringifies_mixed_values():
    frame = display_rows_frame(
        [
            {"field": "Status code", "value": 200},
            {"field": "Missing", "value": None},
        ]
    )

    assert frame["value"].tolist() == ["200", "None"]
    assert all(isinstance(value, str) for value in frame["value"].tolist())


def test_apply_app_shell_injects_css_before_rendering_sidebar(monkeypatch):
    """Regression: apply_app_shell() used to render the sidebar's custom HTML
    before injecting the stylesheet that styles it -- a leftover ordering
    from the removed Dark/Light toggle era (CSS injection has no
    session_state dependency on sidebar widgets anymore). This left a window
    where the sidebar's custom-styled HTML reached the browser before its
    stylesheet existed, producing a flash of unstyled content."""
    call_order = []

    monkeypatch.setattr(ui, "_inject_global_css", lambda mode: call_order.append("css"))
    monkeypatch.setattr(ui, "render_sidebar", lambda active_page: call_order.append("sidebar"))
    monkeypatch.setattr(ui, "record_recent_visit", lambda slug: None)
    monkeypatch.setattr(ui, "_sync_local_storage_mirror", lambda active_page: None)

    ui.apply_app_shell("Home")

    assert call_order == ["css", "sidebar"]


def test_render_status_note_escapes_description_and_normalizes_tone(monkeypatch):
    rendered = []

    def fake_markdown(value, unsafe_allow_html=False):
        rendered.append((value, unsafe_allow_html))

    monkeypatch.setattr(ui.st, "markdown", fake_markdown)

    ui.render_status_note("AI <summary>", "<script>alert(1)</script>\nline", tone="unknown")

    html, unsafe = rendered[0]
    assert unsafe is True
    assert "tool-status-note-info" in html
    assert 'role="status"' in html
    assert 'aria-live="polite"' in html
    assert "AI &lt;summary&gt;" in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;<br>line" in html
    assert "<script>" not in html


def test_render_status_note_warning_uses_alert_semantics(monkeypatch):
    rendered = []

    monkeypatch.setattr(ui.st, "markdown", lambda value, unsafe_allow_html=False: rendered.append((value, unsafe_allow_html)))

    ui.render_status_note("Warning", "Needs attention", tone="warning")

    html, unsafe = rendered[0]
    assert unsafe is True
    assert 'role="alert"' in html
    assert 'aria-live="assertive"' in html


def test_classify_failure_mode_distinguishes_transient_and_persistent():
    assert ui.classify_failure_mode("HTTP request timed out after 3 attempts.") == "transient"
    assert ui.classify_failure_mode("Domain does not exist.") == "persistent"


def test_classify_failure_mode_handles_phase4_adapter_error_taxonomy_messages():
    transient_cases = [
        "DNS lookup timed out after 3 attempts.",
        "GitHub issues timed out or could not connect after 3 attempts. Showing seed roadmap data.",
        "Connection failed after 3 attempts: connection reset",
    ]
    persistent_cases = [
        "GitHub repository URL is invalid. Showing seed roadmap data.",
        "Domain does not exist.",
        "Port must be between 1 and 65535.",
    ]

    for message in transient_cases:
        assert ui.classify_failure_mode(message) == "transient"

    for message in persistent_cases:
        assert ui.classify_failure_mode(message) == "persistent"


def test_render_failure_note_hides_raw_sensitive_error(monkeypatch):
    rendered = []

    def fake_markdown(value, unsafe_allow_html=False):
        rendered.append((value, unsafe_allow_html))

    monkeypatch.setattr(ui.st, "markdown", fake_markdown)

    ui.render_failure_note(
        "HTTP check",
        "Connection failed after 3 attempts: https://internal.example.local/token=super-secret",
        remediation="Retry from a network with egress access.",
    )

    html, unsafe = rendered[0]
    assert unsafe is True
    assert "HTTP check temporarily unavailable" in html
    assert "super-secret" not in html
    assert "internal.example.local" not in html
    assert "Next step: Retry from a network with egress access." in html


def test_render_page_header_includes_tool_category_overline(monkeypatch):
    rendered = []

    def fake_markdown(value, unsafe_allow_html=False):
        rendered.append((value, unsafe_allow_html))

    monkeypatch.setattr(ui.st, "markdown", fake_markdown)

    tool = TOOLS[0]
    ui.render_page_header(tool.title, "desc")

    html, unsafe = rendered[0]
    assert unsafe is True
    assert 'class="tool-page-overline"' in html
    assert 'aria-labelledby="tool-page-title-' in html
    assert '<h1 id="tool-page-title-' in html
    assert f">{tool.category} Tool<" in html


def test_render_page_header_renders_generated_illustration_slot(monkeypatch):
    rendered = []

    monkeypatch.setattr(ui.st, "markdown", lambda value, unsafe_allow_html=False: rendered.append(value))

    tool = TOOLS[0]
    ui.render_page_header(tool.title, "desc")

    assert "tool-page-header-illustration" in rendered[0]
    assert "tool-page-header-with-illustration" in rendered[0]


def test_render_page_header_falls_back_when_illustration_asset_is_missing(monkeypatch):
    rendered = []

    monkeypatch.setattr(ui.st, "markdown", lambda value, unsafe_allow_html=False: rendered.append(value))

    tool = TOOLS[0]
    ui.render_page_header(tool.title, "desc", illustration="illustrations/exported/not-real.svg")

    assert "tool-page-header-illustration" not in rendered[0]
    assert "tool-page-header-with-illustration" not in rendered[0]


def test_render_empty_state_supports_optional_illustration(monkeypatch):
    rendered = []

    monkeypatch.setattr(ui.st, "markdown", lambda value, unsafe_allow_html=False: rendered.append(value))

    ui.render_empty_state("Ready", "Description", illustration="network")

    assert "tool-empty-illustration" in rendered[0]
    assert "tool-empty-illustration-image" in rendered[0]
    assert 'role="status"' in rendered[0]
    assert 'aria-live="polite"' in rendered[0]
    assert 'aria-label="Ready"' in rendered[0]


def test_render_empty_state_skips_unknown_illustration_key(monkeypatch):
    rendered = []

    monkeypatch.setattr(ui.st, "markdown", lambda value, unsafe_allow_html=False: rendered.append(value))

    ui.render_empty_state("Ready", "Description", illustration="does-not-exist")

    assert "tool-empty-illustration" not in rendered[0]


def test_render_form_intro_sets_group_semantics(monkeypatch):
    rendered = []

    monkeypatch.setattr(ui.st, "markdown", lambda value, unsafe_allow_html=False: rendered.append((value, unsafe_allow_html)))

    ui.render_form_intro("Enter input", "Description")

    html, unsafe = rendered[0]
    assert unsafe is True
    assert 'class="tool-form-intro"' in html
    assert 'role="group"' in html
    assert 'aria-labelledby="tool-form-intro-enter_input"' in html
    assert '<h2 id="tool-form-intro-enter_input">Enter input</h2>' in html


def test_tool_card_html_includes_category_badge_and_escapes_fields():
    tool = ui.ToolMeta(
        title="Title <x>",
        short_title="Title",
        description="Desc <y>",
        path="pages/1_test.py",
        icon="IT",
        accent="#123456",
        slug="test_tool",
        professions=("Support Engineer",),
        category="Ops & Automation",
    )

    html = ui._tool_card_html(tool)
    assert 'class="tool-card-category"' in html
    assert ">Ops &amp; Automation<" in html
    assert "Title &lt;x&gt;" in html
    assert "Desc &lt;y&gt;" in html


def test_tool_card_html_uses_generated_icon_when_mapped():
    mapped_tool = next(tool for tool in TOOLS if tool.slug == "dns_records")

    html = ui._tool_card_html(mapped_tool)

    assert "tool-card-icon-image" in html
    assert 'alt=""' in html
    assert 'role="presentation"' in html
    assert "data:image/svg+xml;base64," in html


def test_tool_card_html_falls_back_to_text_icon_when_asset_missing(monkeypatch):
    mapped_tool = next(tool for tool in TOOLS if tool.slug == "dns_records")
    monkeypatch.setattr(ui, "_svg_img_html", lambda *args, **kwargs: None)

    html = ui._tool_card_html(mapped_tool)

    assert "tool-card-icon-image" not in html
    assert f">{mapped_tool.icon}<" in html


def test_tool_card_html_uses_category_default_icon_when_slug_has_no_explicit_mapping():
    category_default_tool = next(tool for tool in TOOLS if tool.slug == "markdown_converter")

    html = ui._tool_card_html(category_default_tool)

    assert "tool-card-icon-image" in html
    assert "data:image/svg+xml;base64," in html


def test_tool_card_icon_asset_prefers_slug_specific_mapping_over_category_default():
    mapped_tool = next(tool for tool in TOOLS if tool.slug == "base64_tool")

    icon_asset = ui._tool_card_icon_asset(mapped_tool)

    assert icon_asset == "icons/exported/icon-workflow-encoding-tools-outline-24x24-v01.svg"


def test_tool_card_icon_asset_maps_wave2_weak_cue_tools():
    expected_assets = {
        "env_linter": "icons/exported/icon-workflow-env-guard-outline-24x24-v01.svg",
        "markdown_toc_generator": "icons/exported/icon-workflow-markdown-structure-outline-24x24-v01.svg",
        "id_generator": "icons/exported/icon-workflow-id-sequence-outline-24x24-v01.svg",
        "csp_builder": "icons/exported/icon-workflow-policy-controls-outline-24x24-v01.svg",
    }

    for slug, expected in expected_assets.items():
        tool = next(item for item in TOOLS if item.slug == slug)
        assert ui._tool_card_icon_asset(tool) == expected


def test_tool_card_icon_asset_maps_wave3_weak_cue_tools():
    expected_assets = {
        "unified_diff_generator": "icons/exported/icon-workflow-diff-patch-outline-24x24-v01.svg",
        "jwk_pem_converter": "icons/exported/icon-workflow-key-format-outline-24x24-v01.svg",
        "cert_chain_validator": "icons/exported/icon-workflow-cert-chain-outline-24x24-v01.svg",
        "wsl_path_converter": "icons/exported/icon-workflow-path-bridge-outline-24x24-v01.svg",
        "markdown_link_extractor": "icons/exported/icon-workflow-link-extract-outline-24x24-v01.svg",
        "health_diagnostics": "icons/exported/icon-workflow-health-diagnostics-outline-24x24-v01.svg",
    }

    for slug, expected in expected_assets.items():
        tool = next(item for item in TOOLS if item.slug == slug)
        assert ui._tool_card_icon_asset(tool) == expected


def test_tool_card_icon_asset_wave3_slug_specific_mapping_precedes_category_default():
    tool = next(item for item in TOOLS if item.slug == "unified_diff_generator")

    assert tool.category == "Web & Dev"
    assert ui._tool_card_icon_asset(tool) == "icons/exported/icon-workflow-diff-patch-outline-24x24-v01.svg"


def test_tool_card_html_uses_wave2_generated_icon_when_mapped():
    mapped_tool = next(tool for tool in TOOLS if tool.slug == "env_linter")

    html = ui._tool_card_html(mapped_tool)

    assert "tool-card-icon-image" in html
    assert "data:image/svg+xml;base64," in html


def test_tool_card_icon_asset_returns_none_for_unknown_slug_and_category():
    tool = ui.ToolMeta(
        title="Unknown Tool",
        short_title="Unknown",
        description="desc",
        path="pages/999_unknown.py",
        icon="??",
        accent="#123456",
        slug="unknown_tool",
        professions=("Support Engineer",),
        category="Unknown",
    )

    assert ui._tool_card_icon_asset(tool) is None


def test_roadmap_badge_icon_html_falls_back_when_asset_missing(monkeypatch):
    monkeypatch.setattr(ui, "_svg_img_html", lambda *args, **kwargs: None)

    html = ui.roadmap_badge_icon_html("status_planned", "•")

    assert "roadmap-badge-icon-fallback" in html


def test_roadmap_badge_icon_html_uses_mapped_svg_when_available(monkeypatch):
    monkeypatch.setattr(ui, "_svg_img_html", lambda *args, **kwargs: '<img class="roadmap-badge-icon-image" />')

    html = ui.roadmap_badge_icon_html("source_github", "GH")

    assert "roadmap-badge-icon-fallback" not in html
    assert 'class="roadmap-badge-icon"' in html
    assert "roadmap-badge-icon-image" in html


def test_home_hero_html_falls_back_to_css_visual_when_generated_asset_missing(monkeypatch):
    monkeypatch.setattr(ui, "_svg_img_html", lambda *args, **kwargs: None)

    html = ui._hero_visual_html()

    assert "hero-shield" in html


def test_title_to_slug_covers_every_tool():
    assert len(TITLE_TO_SLUG) == len(TOOLS)
    for tool in TOOLS:
        assert TITLE_TO_SLUG[tool.title] == tool.slug


def test_filter_tools_empty_query_and_profession_returns_everything():
    assert filter_tools() == TOOLS
    assert filter_tools("", "All") == TOOLS


def test_filter_tools_profession_narrows_results():
    results = filter_tools(profession="Network Engineer")

    assert results
    assert all("Network Engineer" in tool.professions for tool in results)
    assert len(results) < len(TOOLS)


def test_filter_tools_query_and_profession_combine_with_and():
    results = filter_tools(query="hash", profession="Network Engineer")

    assert results == ()


def test_filter_tools_unknown_profession_behaves_like_all():
    assert filter_tools(profession="Not A Real Profession") == TOOLS


def test_filter_tools_cache_treats_unknown_profession_like_all():
    assert filter_tools(query="jwt", profession="All") == filter_tools(query="jwt", profession="Nope")


def test_filter_tools_covers_every_declared_profession():
    for profession in PROFESSIONS:
        assert filter_tools(profession=profession), f"no tool tagged with {profession!r}"


def test_filter_tools_matches_on_alias():
    # "b64" appears in none of Base64 Tool's title/short_title/description/slug,
    # so without alias matching this search would return nothing.
    results = filter_tools(query="b64")

    assert results
    assert all(tool.slug == "base64_tool" for tool in results)


def test_filter_tools_matches_on_geoip_alias():
    # "geoip" is a common industry abbreviation that appears in none of IP
    # Geolocation Lookup's title/short_title/description/slug.
    results = filter_tools(query="geoip")

    assert results
    assert all(tool.slug == "ip_geolocation" for tool in results)


def test_guided_workflows_respect_search_and_profession_filters():
    all_workflows = guided_workflows()
    assert all_workflows

    jwt_only = guided_workflows(query="jwt")
    assert jwt_only
    assert all("jwt" in f"{wf.title} {wf.description}".lower() or "jwt" in " ".join(wf.slugs) for wf in jwt_only)

    network_engineer = guided_workflows(profession="Network Engineer")
    assert network_engineer
    assert any(workflow.title == "Domain incident triage" for workflow in network_engineer)


def test_render_guided_workflows_renders_heading_and_numbered_safe_step_links(monkeypatch):
    class _Ctx:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    rendered_markdown = []
    step_links = []
    workflow = ui.GuidedWorkflow(
        title="Domain <script>alert(1)</script>",
        description='Trace "DNS" & <HTTP> safely',
        slugs=("jwt_decoder", "base64_tool"),
        badge="Ops <Team>",
    )

    monkeypatch.setattr(ui, "GUIDED_WORKFLOWS", (workflow,))
    monkeypatch.setattr(ui.st, "columns", lambda n, gap=None: [_Ctx() for _ in range(n)])
    monkeypatch.setattr(ui.st, "container", lambda key=None: _Ctx())
    monkeypatch.setattr(
        ui.st,
        "markdown",
        lambda value, unsafe_allow_html=False: rendered_markdown.append((value, unsafe_allow_html)),
    )
    monkeypatch.setattr(
        ui,
        "_safe_page_link",
        lambda path, label, icon, stretch_width=False: step_links.append((path, label, icon, stretch_width)),
    )

    ui.render_guided_workflows()

    assert "Start Here Workflows" in rendered_markdown[0][0]
    card_html = rendered_markdown[1][0]
    assert "Domain <script>alert(1)</script>" not in card_html
    assert "Domain &lt;script&gt;alert(1)&lt;/script&gt;" in card_html
    assert "Ops &lt;Team&gt;" in card_html
    assert "Trace &quot;DNS&quot; &amp; &lt;HTTP&gt; safely" in card_html
    assert step_links == [
        ("pages/7_JWT_Decoder.py", "1. JWT Decoder", ":material/verified_user:", True),
        ("pages/6_Base64_Tool.py", "2. Base64 Tool", ":material/looks_6:", True),
    ]


def test_safe_page_link_fallback_escapes_link_label_html(monkeypatch):
    rendered = []

    def raise_missing_page(*args, **kwargs):
        raise KeyError("missing page")

    monkeypatch.setattr(ui.st, "page_link", raise_missing_page)
    monkeypatch.setattr(ui.st, "markdown", lambda value, unsafe_allow_html=False: rendered.append((value, unsafe_allow_html)))

    ui._safe_page_link(
        "pages/7_JWT_Decoder.py",
        label='1. JWT <script>alert("x")</script>',
        icon=":material/verified_user:",
    )

    html, unsafe = rendered[0]
    assert unsafe is True
    assert 'class="fallback-page-link"' in html
    assert 'href="/JWT_Decoder"' in html
    assert "<script>" not in html
    assert '1. JWT &lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;' in html


def test_safe_page_link_fallback_maps_home_path_to_root(monkeypatch):
    rendered = []

    monkeypatch.setattr(ui.st, "page_link", lambda *args, **kwargs: (_ for _ in ()).throw(KeyError("missing page")))
    monkeypatch.setattr(ui.st, "markdown", lambda value, unsafe_allow_html=False: rendered.append((value, unsafe_allow_html)))

    ui._safe_page_link(
        "app.py",
        label="Home",
        icon=":material/home:",
    )

    html, unsafe = rendered[0]
    assert unsafe is True
    assert 'class="fallback-page-link"' in html
    assert 'href="/"' in html
    assert ">Home<" in html


def test_fallback_href_handles_numbered_and_plain_page_paths():
    assert ui._fallback_href("pages/7_JWT_Decoder.py") == "/JWT_Decoder"
    assert ui._fallback_href("pages/custom_page.py") == "/custom_page"
    assert ui._fallback_href("app.py") == "/"


# Live-external-lookup pages that should carry a caution warning= on
# render_page_header (fires a request against private/internal input a
# visitor might paste without thinking, e.g. an internal hostname or IP).
LIVE_LOOKUP_PAGES = (
    "pages/1_Domain_Health_Checker.py",
    "pages/2_DNS_Record_Checker.py",
    "pages/3_SSL_Certificate_Checker.py",
    "pages/4_HTTP_Status_Checker.py",
    "pages/13_MAC_Address_Tool.py",
    "pages/27_WHOIS_Lookup.py",
    "pages/28_Bulk_Domain_Health.py",
    "pages/29_Webhook_Tester.py",
    "pages/30_Uptime_Trend.py",
    "pages/31_Security_Headers_Checker.py",
    "pages/32_CVE_Lookup.py",
    "pages/33_DNS_Propagation_Checker.py",
    "pages/35_DKIM_Selector_Lookup.py",
    "pages/42_IP_Geolocation_Lookup.py",
)


def test_live_lookup_pages_have_a_caution_warning():
    # Regression guard: PR #71 added warning= to 9 of these pages, and a
    # follow-up added the 10th (MAC Address Tool). A silent removal of
    # warning= on any of them would otherwise go undetected.
    for rel_path in LIVE_LOOKUP_PAGES:
        source = Path(rel_path).read_text(encoding="utf-8")
        assert "warning=" in source, f"{rel_path}: missing warning= on render_page_header"


def test_recent_or_popular_tools_falls_back_to_popular_when_empty():
    assert recent_or_popular_tools([]) == POPULAR_TOOLS


def test_recent_or_popular_tools_skips_unknown_slugs_and_dedupes():
    slug = TOOLS[-1].slug
    result = recent_or_popular_tools(["not-a-real-slug", slug, slug])

    assert result[0] == TOOLS[-1]
    assert result.count(TOOLS[-1]) == 1


def test_recent_or_popular_tools_pads_to_five_with_popular_tools_in_order():
    slug = TOOLS[-1].slug
    result = recent_or_popular_tools([slug])

    assert len(result) == 5
    assert result[0] == TOOLS[-1]
    assert result[1:] == tuple(t for t in POPULAR_TOOLS if t.slug != slug)[:4]


def test_recent_or_popular_tools_no_padding_when_five_valid_recents():
    slugs = [tool.slug for tool in TOOLS[:5]][::-1]
    result = recent_or_popular_tools(slugs)

    assert [tool.slug for tool in result] == slugs


def test_sort_tools_az_and_za_sort_by_title_case_insensitively():
    subset = (TOOLS[3], TOOLS[0], TOOLS[1])

    az = sort_tools(subset, "az")
    za = sort_tools(subset, "za")

    assert [t.title for t in az] == sorted((t.title for t in subset), key=str.lower)
    assert [t.title for t in za] == sorted((t.title for t in subset), key=str.lower, reverse=True)


def test_sort_tools_default_and_unknown_mode_preserve_order():
    subset = (TOOLS[3], TOOLS[0], TOOLS[1])

    assert sort_tools(subset, "default") == subset
    assert sort_tools(subset, "not-a-real-mode") == subset


def test_expected_tools_are_tagged_new():
    # Re-scoped from all 42 non-original tools down to the last ~8 actually
    # shipped, so the "Newest Tools" home page section regains real signal
    # instead of rendering an uncapped ~9-row section.
    new_slugs = {tool.slug for tool in TOOLS if tool.is_new}

    assert new_slugs == {
        "base62_tool",
        "unified_diff_generator",
        "jwk_pem_converter",
        "cert_chain_validator",
        "wsl_path_converter",
        "markdown_link_extractor",
    }


def test_record_recent_visit_prepends_dedupes_and_caps(monkeypatch):
    monkeypatch.setattr(ui.st, "query_params", {})

    record_recent_visit("hash_generator")
    record_recent_visit("mac_address_tool")
    record_recent_visit("hash_generator")

    assert ui.st.query_params["recent"] == "hash_generator,mac_address_tool"


def test_record_recent_visit_noops_when_slug_already_most_recent(monkeypatch):
    class _TrackedParams(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_calls = 0
            self.pop_calls = 0

        def __setitem__(self, key, value):
            self.set_calls += 1
            return super().__setitem__(key, value)

        def pop(self, key, default=None):
            self.pop_calls += 1
            return super().pop(key, default)

    params = _TrackedParams({"recent": "hash_generator,mac_address_tool"})
    monkeypatch.setattr(ui.st, "query_params", params)

    record_recent_visit("hash_generator")

    assert params["recent"] == "hash_generator,mac_address_tool"
    assert params.set_calls == 0
    assert params.pop_calls == 0


def test_record_recent_visit_caps_at_max_recent_tools(monkeypatch):
    monkeypatch.setattr(ui.st, "query_params", {})
    slugs = [tool.slug for tool in TOOLS[:6]]

    for slug in slugs:
        record_recent_visit(slug)

    stored = ui.st.query_params["recent"].split(",")
    assert len(stored) == ui.MAX_RECENT_TOOLS
    assert stored[0] == slugs[-1]


def test_get_persisted_slugs_dedupes_empties_and_caps_recent(monkeypatch):
    monkeypatch.setattr(ui.st, "query_params", {"recent": "a,,b,a,c,d,e,f"})

    assert ui._get_persisted_slugs("recent") == ["a", "b", "c", "d", "e"]


def test_toggle_favorite_adds_and_removes(monkeypatch):
    monkeypatch.setattr(ui.st, "query_params", {})
    slug = TOOLS[0].slug

    toggle_favorite(slug)
    assert ui.st.query_params.get("fav") == slug

    toggle_favorite(slug)
    assert "fav" not in ui.st.query_params


def test_move_favorite_swaps_with_neighbor(monkeypatch):
    a, b, c = TOOLS[0].slug, TOOLS[1].slug, TOOLS[2].slug
    monkeypatch.setattr(ui.st, "query_params", {"fav": f"{a},{b},{c}"})

    move_favorite(b, -1)
    assert ui.st.query_params["fav"] == f"{b},{a},{c}"

    move_favorite(b, 1)
    assert ui.st.query_params["fav"] == f"{a},{b},{c}"


def test_move_favorite_out_of_bounds_is_a_noop(monkeypatch):
    a, b = TOOLS[0].slug, TOOLS[1].slug
    monkeypatch.setattr(ui.st, "query_params", {"fav": f"{a},{b}"})

    move_favorite(a, -1)
    assert ui.st.query_params["fav"] == f"{a},{b}"

    move_favorite(b, 1)
    assert ui.st.query_params["fav"] == f"{a},{b}"


def test_move_favorite_ignores_slug_not_in_favorites(monkeypatch):
    a = TOOLS[0].slug
    monkeypatch.setattr(ui.st, "query_params", {"fav": a})

    move_favorite(TOOLS[1].slug, 1)
    assert ui.st.query_params["fav"] == a


def test_favorite_tools_reads_query_params_and_skips_unknown(monkeypatch):
    slug = TOOLS[2].slug
    monkeypatch.setattr(ui.st, "query_params", {"fav": f"not-a-real-slug,{slug}"})

    assert favorite_tools() == (TOOLS[2],)


def test_favorites_share_link_encodes_slugs_and_uses_shared_param():
    link = favorites_share_link([TOOLS[0], TOOLS[2]])

    assert link.startswith(ui.app_base_url())
    assert f"{SHARED_FAVORITES_PARAM}={TOOLS[0].slug}%2C{TOOLS[2].slug}" in link


def test_shared_favorite_tools_reads_shared_param_and_skips_unknown(monkeypatch):
    slug = TOOLS[3].slug
    monkeypatch.setattr(ui.st, "query_params", {SHARED_FAVORITES_PARAM: f"not-a-real-slug,{slug}"})

    assert shared_favorite_tools() == (TOOLS[3],)


def test_shared_favorites_param_is_excluded_from_local_storage_mirror():
    # Sharing a favorites link must never overwrite the visitor's own saved
    # favorites -- confirm the mirror only ever touches "recent"/"fav".
    assert SHARED_FAVORITES_PARAM not in ui.PERSISTED_LIST_PARAMS


def test_request_rerun_uses_fragment_scope_when_available(monkeypatch):
    calls = []

    def fake_rerun(*args, **kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(ui.st, "rerun", fake_rerun)

    ui._request_rerun(prefer_fragment_rerun=True)

    assert calls == [{"scope": "fragment"}]


def test_request_rerun_falls_back_to_full_app_when_fragment_scope_unsupported(monkeypatch):
    calls = []

    def fake_rerun(*args, **kwargs):
        calls.append(kwargs)
        if kwargs.get("scope") == "fragment":
            raise RuntimeError("fragment scope unavailable")

    monkeypatch.setattr(ui.st, "rerun", fake_rerun)

    ui._request_rerun(prefer_fragment_rerun=True)

    assert calls == [{"scope": "fragment"}, {}]


def test_related_tools_resolves_bundle_slugs_in_order():
    tools = related_tools("ssl_certificate")

    assert [t.slug for t in tools] == list(TOOL_BUNDLES["ssl_certificate"])


def test_related_tools_returns_empty_for_unbundled_slug():
    assert related_tools("not-a-real-slug") == ()


def test_all_tool_bundles_reference_known_slugs_and_never_self_reference():
    known_slugs = {tool.slug for tool in TOOLS}
    for slug, related in TOOL_BUNDLES.items():
        assert slug in known_slugs, f"{slug!r} is not a known tool slug"
        for related_slug in related:
            assert related_slug in known_slugs, f"{slug!r} bundles unknown slug {related_slug!r}"
            assert related_slug != slug, f"{slug!r} lists itself as a related tool"


def test_every_tool_has_a_valid_sidebar_category():
    for tool in TOOLS:
        assert tool.category in SIDEBAR_CATEGORIES, f"{tool.slug} has unknown category {tool.category!r}"


def test_sidebar_category_partition_matches_expected_grouping():
    by_category: dict[str, list[str]] = {category: [] for category in SIDEBAR_CATEGORIES}
    for tool in TOOLS:
        by_category[tool.category].append(tool.slug)

    assert by_category == {
        "Network": [
            "domain_health",
            "dns_records",
            "subnet_calculator",
            "mac_address_tool",
            "cidr_aggregator",
            "ipv6_compressor",
            "whois_lookup",
            "bulk_domain_health",
            "dns_propagation",
            "dkim_lookup",
            "email_record_builder",
            "ip_geolocation",
            "cidr_overlap",
            "caa_record_builder",
        ],
        "Security": [
            "ssl_certificate",
            "jwt_decoder",
            "hash_generator",
            "email_header_analyzer",
            "password_generator",
            "jwt_encoder",
            "security_headers",
            "cve_lookup",
            "file_integrity",
            "totp_generator",
            "keypair_generator",
            "bcrypt_tool",
            "tls_scanner",
            "jwt_weak_secret",
            "csr_decoder",
            "pem_bundle_splitter",
            "luhn_validator",
            "ssh_fingerprint",
            "password_entropy",
            "iban_validator",
            "csp_builder",
            "pii_redactor",
            "password_policy_checker",
            "ssh_config_validator",
            "csr_generator",
            "jwk_pem_converter",
            "cert_chain_validator",
        ],
        "Web & Dev": [
            "http_status",
            "url_encoder_decoder",
            "user_agent_parser",
            "webhook_tester",
            "uptime_trend",
            "curl_builder",
            "robots_validator",
            "url_parser",
            "http_header_parser",
            "html_entity_tools",
            "line_ending_converter",
            "user_agent_builder",
            "basic_auth_tool",
            "json_to_typescript",
            "css_gradient_generator",
            "robots_meta_builder",
            "cache_control_tool",
            "unified_diff_generator",
            "markdown_link_extractor",
        ],
        "Data & Text": [
            "json_formatter",
            "base64_tool",
            "regex_tester",
            "text_diff_checker",
            "case_converter",
            "color_converter",
            "config_format_converter",
            "id_generator",
            "json_diff",
            "base_converter",
            "qr_code_generator",
            "sql_formatter",
            "ulid_uuid_decoder",
            "env_linter",
            "csv_diff",
            "markdown_converter",
            "encoding_detector",
            "base32_tools",
            "whitespace_visualizer",
            "xml_formatter",
            "deterministic_uuid",
            "text_stats",
            "csv_to_markdown",
            "yaml_formatter",
            "regex_replace",
            "csv_json_converter",
            "json_path_query",
            "base58_tool",
            "markdown_toc_generator",
            "number_to_words",
            "markdown_table_formatter",
            "csv_column_selector",
            "line_numberer",
            "test_data_generator",
            "json_merge_patch",
            "base62_tool",
        ],
        "Ops & Automation": [
            "cron_explainer",
            "log_troubleshooting",
            "timestamp_converter",
            "chmod_calculator",
            "cron_builder",
            "business_hours",
            "log_duration",
            "date_calculator",
            "byte_size_converter",
            "pattern_extractor",
            "line_sorter",
            "semver_tools",
            "world_clock",
            "csv_cleaner",
            "gitignore_tester",
            "env_diff",
            "cron_overlap",
            "iso8601_duration",
            "column_aligner",
            "wsl_path_converter",
            "health_diagnostics",
        ],
        "Reference": [
            "port_reference",
            "windows_event_reference",
            "windows_error_reference",
            "m365_sku_decoder",
            "http_status_reference",
            "regex_cheat_sheet",
            "exit_code_reference",
            "timezone_abbreviation_reference",
            "jwt_claims_reference",
            "http_methods_reference",
        ],
    }


def test_every_tool_covered_exactly_once_across_categories():
    all_slugs = [tool.slug for category in SIDEBAR_CATEGORIES for tool in TOOLS if tool.category == category]

    assert sorted(all_slugs) == sorted(tool.slug for tool in TOOLS)
    assert len(all_slugs) == len(TOOLS)


def test_no_sidebar_category_dominates_the_tool_count():
    # Regression guard: "Web & Dev" grew to 17/51 tools (33%) before being
    # rebalanced into two categories. The exact-partition test above catches
    # a *wrong* category on a known tool, but says nothing about a future
    # addition silently recreating an oversized bucket -- this is a generic
    # backstop that doesn't need updating every time a tool is added.
    counts: dict[str, int] = {category: 0 for category in SIDEBAR_CATEGORIES}
    for tool in TOOLS:
        counts[tool.category] += 1

    max_share = max(counts.values()) / len(TOOLS)
    assert max_share <= 0.3, f"a sidebar category holds {max_share:.0%} of all tools: {counts}"
