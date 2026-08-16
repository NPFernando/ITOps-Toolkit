from pathlib import Path

from utils import ui
from utils.ui import (
    POPULAR_TOOLS,
    PROFESSIONS,
    SIDEBAR_CATEGORIES,
    TITLE_TO_SLUG,
    TOOLS,
    display_rows_frame,
    favorite_tools,
    filter_tools,
    move_favorite,
    record_recent_visit,
    recent_or_popular_tools,
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
    assert 'role="status"' in html
    assert 'aria-live="polite"' in html
    assert 'aria-atomic="true"' in html
    assert 'tabindex="0"' in html
    assert 'aria-label="Info status: AI &lt;summary&gt;"' in html
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


def test_filter_tools_matches_on_alias():
    # "b64" appears in none of Base64 Tool's title/short_title/description/slug,
    # so without alias matching this search would return nothing.
    results = filter_tools(query="b64")

    assert results
    assert all(tool.slug == "base64_tool" for tool in results)


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
        "security_headers",
        "cve_lookup",
        "dns_propagation",
        "windows_event_reference",
        "dkim_lookup",
        "email_record_builder",
        "windows_error_reference",
        "config_format_converter",
        "m365_sku_decoder",
        "id_generator",
        "json_diff",
        "ip_geolocation",
        "file_integrity",
        "chmod_calculator",
        "base_converter",
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
        ],
        "Web & Dev": [
            "http_status",
            "url_encoder_decoder",
            "user_agent_parser",
            "webhook_tester",
            "uptime_trend",
            "config_format_converter",
            "id_generator",
            "json_diff",
            "base_converter",
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
        ],
        "Ops & Automation": ["cron_explainer", "log_troubleshooting", "timestamp_converter", "chmod_calculator", "cron_builder"],
        "Reference": [
            "port_reference",
            "windows_event_reference",
            "windows_error_reference",
            "m365_sku_decoder",
            "http_status_reference",
            "regex_cheat_sheet",
        ],
        "Ops & Automation": ["cron_explainer", "log_troubleshooting", "timestamp_converter", "chmod_calculator", "cron_builder"],
        "Reference": ["port_reference", "windows_event_reference", "windows_error_reference", "m365_sku_decoder", "http_status_reference"],
    }


def test_every_tool_covered_exactly_once_across_categories():
    all_slugs = [tool.slug for category in SIDEBAR_CATEGORIES for tool in TOOLS if tool.category == category]

    assert sorted(all_slugs) == sorted(tool.slug for tool in TOOLS)
    assert len(all_slugs) == len(TOOLS)
