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


def test_render_status_note_escapes_description_and_normalizes_tone(monkeypatch):
    rendered = []

    def fake_markdown(value, unsafe_allow_html=False):
        rendered.append((value, unsafe_allow_html))

    monkeypatch.setattr(ui.st, "markdown", fake_markdown)

    ui.render_status_note("AI <summary>", "<script>alert(1)</script>\nline", tone="unknown")

    html, unsafe = rendered[0]
    assert unsafe is True
    assert "tool-status-note-info" in html
    assert "AI &lt;summary&gt;" in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;<br>line" in html
    assert "<script>" not in html


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


def test_filter_tools_covers_every_declared_profession():
    for profession in PROFESSIONS:
        assert filter_tools(profession=profession), f"no tool tagged with {profession!r}"


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
    new_slugs = {tool.slug for tool in TOOLS if tool.is_new}

    assert new_slugs == {
        "subnet_calculator",
        "hash_generator",
        "mac_address_tool",
        "email_header_analyzer",
        "port_reference",
        "password_generator",
        "url_encoder_decoder",
        "regex_tester",
        "timestamp_converter",
        "text_diff_checker",
        "jwt_encoder",
        "cidr_aggregator",
        "user_agent_parser",
        "ipv6_compressor",
        "case_converter",
        "color_converter",
        "whois_lookup",
        "bulk_domain_health",
        "webhook_tester",
        "uptime_trend",
    }


def test_record_recent_visit_prepends_dedupes_and_caps(monkeypatch):
    monkeypatch.setattr(ui.st, "query_params", {})

    record_recent_visit("hash_generator")
    record_recent_visit("mac_address_tool")
    record_recent_visit("hash_generator")

    assert ui.st.query_params["recent"] == "hash_generator,mac_address_tool"


def test_record_recent_visit_caps_at_max_recent_tools(monkeypatch):
    monkeypatch.setattr(ui.st, "query_params", {})
    slugs = [tool.slug for tool in TOOLS[:6]]

    for slug in slugs:
        record_recent_visit(slug)

    stored = ui.st.query_params["recent"].split(",")
    assert len(stored) == ui.MAX_RECENT_TOOLS
    assert stored[0] == slugs[-1]


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
        ],
        "Security": ["ssl_certificate", "jwt_decoder", "hash_generator", "email_header_analyzer", "password_generator", "jwt_encoder"],
        "Web & Dev": [
            "http_status",
            "json_formatter",
            "base64_tool",
            "url_encoder_decoder",
            "regex_tester",
            "text_diff_checker",
            "user_agent_parser",
            "case_converter",
            "color_converter",
            "webhook_tester",
            "uptime_trend",
        ],
        "Ops & Automation": ["cron_explainer", "log_troubleshooting", "timestamp_converter"],
        "Reference": ["port_reference"],
    }


def test_every_tool_covered_exactly_once_across_categories():
    all_slugs = [tool.slug for category in SIDEBAR_CATEGORIES for tool in TOOLS if tool.category == category]

    assert sorted(all_slugs) == sorted(tool.slug for tool in TOOLS)
    assert len(all_slugs) == len(TOOLS)
