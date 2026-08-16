"""Shared Streamlit UI shell and design helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from html import escape
from typing import Any, Callable, Iterable
from urllib.parse import urlencode

import pandas as pd
import streamlit as st

from utils.project_links import app_base_url, github_repository_url


MAX_RECENT_TOOLS = 5
PERSISTED_LIST_PARAMS: tuple[str, ...] = ("recent", "fav")
# Deliberately NOT in PERSISTED_LIST_PARAMS: "shared_fav" is a read-only,
# view-only param for opening someone else's shared favorites link. It must
# never be mirrored into localStorage or treated as the visitor's own
# persisted favorites -- that would silently overwrite a visitor's saved
# favorites just from opening a link someone sent them.
SHARED_FAVORITES_PARAM = "shared_fav"
ASSETS_ROOT = Path(__file__).resolve().parents[1] / "docs" / "assets"

HOME_HERO_ILLUSTRATION = "illustrations/exported/illustration-home-hero-ops-flow-light-1600x900-v01.svg"
TOOL_CARD_ICON_ASSETS: dict[str, str] = {
    "domain_health": "icons/exported/icon-workflow-dns-lookup-outline-24x24-v01.svg",
    "dns_records": "icons/exported/icon-workflow-dns-lookup-outline-24x24-v01.svg",
    "ssl_certificate": "icons/exported/icon-workflow-ssl-check-outline-24x24-v01.svg",
    "http_status": "icons/exported/icon-workflow-http-probe-outline-24x24-v01.svg",
    "webhook_tester": "icons/exported/icon-workflow-http-probe-outline-24x24-v01.svg",
    "uptime_trend": "icons/exported/icon-workflow-uptime-monitor-outline-24x24-v01.svg",
    "security_headers": "icons/exported/icon-workflow-incident-response-outline-24x24-v01.svg",
    "cve_lookup": "icons/exported/icon-workflow-incident-response-outline-24x24-v01.svg",
    "jwt_decoder": "icons/exported/icon-workflow-jwt-inspect-outline-24x24-v01.svg",
    "jwt_encoder": "icons/exported/icon-workflow-jwt-inspect-outline-24x24-v01.svg",
    "jwt_weak_secret": "icons/exported/icon-workflow-jwt-inspect-outline-24x24-v01.svg",
    "jwt_claims_reference": "icons/exported/icon-workflow-jwt-inspect-outline-24x24-v01.svg",
    "json_formatter": "icons/exported/icon-workflow-json-validate-outline-24x24-v01.svg",
    "json_diff": "icons/exported/icon-workflow-json-validate-outline-24x24-v01.svg",
    "json_path_query": "icons/exported/icon-workflow-json-validate-outline-24x24-v01.svg",
    "json_merge_patch": "icons/exported/icon-workflow-json-merge-patch-outline-24x24-v01.svg",
    "json_to_typescript": "icons/exported/icon-workflow-json-to-typescript-outline-24x24-v01.svg",
    "base64_tool": "icons/exported/icon-workflow-encoding-tools-outline-24x24-v01.svg",
    "base32_tools": "icons/exported/icon-workflow-encoding-tools-outline-24x24-v01.svg",
    "base58_tool": "icons/exported/icon-workflow-encoding-tools-outline-24x24-v01.svg",
    "base62_tool": "icons/exported/icon-workflow-base62-encoder-decoder-outline-24x24-v01.svg",
    "base62_encoder_decoder": "icons/exported/icon-workflow-base62-encoder-decoder-outline-24x24-v01.svg",
    "base_converter": "icons/exported/icon-workflow-encoding-tools-outline-24x24-v01.svg",
    "unified_diff_generator": "icons/exported/icon-workflow-unified-diff-generator-outline-24x24-v01.svg",
    "jwk_pem_converter": "icons/exported/icon-workflow-jwk-pem-converter-outline-24x24-v01.svg",
    "cert_chain_validator": "icons/exported/icon-workflow-cert-chain-validator-outline-24x24-v01.svg",
    "wsl_path_converter": "icons/exported/icon-workflow-wsl-path-converter-outline-24x24-v01.svg",
    "markdown_link_extractor": "icons/exported/icon-workflow-markdown-link-extractor-outline-24x24-v01.svg",
    "health_diagnostics": "icons/exported/icon-workflow-health-diagnostics-outline-24x24-v01.svg",
    "regex_tester": "icons/exported/icon-workflow-regex-match-outline-24x24-v01.svg",
    "regex_replace": "icons/exported/icon-workflow-regex-match-outline-24x24-v01.svg",
    "regex_cheat_sheet": "icons/exported/icon-workflow-regex-match-outline-24x24-v01.svg",
    "pattern_extractor": "icons/exported/icon-workflow-regex-match-outline-24x24-v01.svg",
    "cron_explainer": "icons/exported/icon-workflow-cron-schedule-outline-24x24-v01.svg",
    "cron_builder": "icons/exported/icon-workflow-cron-schedule-outline-24x24-v01.svg",
    "cron_overlap": "icons/exported/icon-workflow-cron-schedule-outline-24x24-v01.svg",
    "cron_overlap_checker": "icons/exported/icon-workflow-cron-schedule-outline-24x24-v01.svg",
    "hash_generator": "icons/exported/icon-workflow-hash-digest-outline-24x24-v01.svg",
    "file_integrity": "icons/exported/icon-workflow-hash-digest-outline-24x24-v01.svg",
    "bcrypt_tool": "icons/exported/icon-workflow-hash-digest-outline-24x24-v01.svg",
    "port_reference": "icons/exported/icon-workflow-port-scan-outline-24x24-v01.svg",
    "tls_scanner": "icons/exported/icon-workflow-port-scan-outline-24x24-v01.svg",
    "env_linter": "icons/exported/icon-workflow-env-guard-outline-24x24-v01.svg",
    "env_diff": "icons/exported/icon-workflow-env-guard-outline-24x24-v01.svg",
    "env_file_diff": "icons/exported/icon-workflow-env-guard-outline-24x24-v01.svg",
    "test_data_generator": "icons/exported/icon-workflow-test-data-fixture-outline-24x24-v01.svg",
    "markdown_toc_generator": "icons/exported/icon-workflow-markdown-toc-generator-outline-24x24-v01.svg",
    "markdown_table_formatter": "icons/exported/icon-workflow-markdown-table-formatter-outline-24x24-v01.svg",
    "id_generator": "icons/exported/icon-workflow-id-sequence-outline-24x24-v01.svg",
    "ulid_uuid_decoder": "icons/exported/icon-workflow-id-sequence-outline-24x24-v01.svg",
    "deterministic_uuid": "icons/exported/icon-workflow-id-sequence-outline-24x24-v01.svg",
    "csp_builder": "icons/exported/icon-workflow-csp-header-builder-outline-24x24-v01.svg",
    "csp_header_builder": "icons/exported/icon-workflow-csp-header-builder-outline-24x24-v01.svg",
    "robots_meta_builder": "icons/exported/icon-workflow-robots-meta-tag-builder-outline-24x24-v01.svg",
    "robots_meta_tag_builder": "icons/exported/icon-workflow-robots-meta-tag-builder-outline-24x24-v01.svg",
    "cache_control_tool": "icons/exported/icon-workflow-cache-control-tool-outline-24x24-v01.svg",
    "robots_validator": "icons/exported/icon-workflow-policy-controls-outline-24x24-v01.svg",
    "basic_auth_tool": "icons/exported/icon-workflow-auth-controls-outline-24x24-v01.svg",
    "keypair_generator": "icons/exported/icon-workflow-auth-controls-outline-24x24-v01.svg",
    "password_policy_checker": "icons/exported/icon-workflow-password-policy-outline-24x24-v01.svg",
    "password_entropy": "icons/exported/icon-workflow-auth-controls-outline-24x24-v01.svg",
    "business_hours": "icons/exported/icon-workflow-time-operations-outline-24x24-v01.svg",
    "world_clock": "icons/exported/icon-workflow-time-operations-outline-24x24-v01.svg",
    "log_duration": "icons/exported/icon-workflow-time-operations-outline-24x24-v01.svg",
    "date_calculator": "icons/exported/icon-workflow-time-operations-outline-24x24-v01.svg",
    "pii_redactor": "icons/exported/icon-workflow-data-sanitization-outline-24x24-v01.svg",
    "csv_cleaner": "icons/exported/icon-workflow-data-sanitization-outline-24x24-v01.svg",
    "whitespace_visualizer": "icons/exported/icon-workflow-data-sanitization-outline-24x24-v01.svg",
    "windows_event_reference": "icons/exported/icon-workflow-api-reference-outline-24x24-v01.svg",
    "windows_error_reference": "icons/exported/icon-workflow-api-reference-outline-24x24-v01.svg",
    "exit_code_reference": "icons/exported/icon-workflow-api-reference-outline-24x24-v01.svg",
    "timezone_abbreviation_reference": "icons/exported/icon-workflow-api-reference-outline-24x24-v01.svg",
    "http_methods_reference": "icons/exported/icon-workflow-http-methods-reference-outline-24x24-v01.svg",
    "sql_formatter": "icons/exported/icon-workflow-query-format-outline-24x24-v01.svg",
    "curl_builder": "icons/exported/icon-workflow-request-builder-outline-24x24-v01.svg",
    "encoding_detector": "icons/exported/icon-workflow-encoding-detect-outline-24x24-v01.svg",
    "url_parser": "icons/exported/icon-workflow-url-parse-outline-24x24-v01.svg",
    "gitignore_tester": "icons/exported/icon-workflow-gitignore-match-outline-24x24-v01.svg",
    "password_generator": "icons/exported/icon-workflow-password-generator-outline-24x24-v01.svg",
    "url_encoder_decoder": "icons/exported/icon-workflow-url-encoding-outline-24x24-v01.svg",
    "timestamp_converter": "icons/exported/icon-workflow-timestamp-convert-outline-24x24-v01.svg",
    "user_agent_parser": "icons/exported/icon-workflow-user-agent-parse-outline-24x24-v01.svg",
    "cidr_overlap": "icons/exported/icon-workflow-cidr-overlap-outline-24x24-v01.svg",
    "m365_sku_decoder": "icons/exported/icon-workflow-m365-sku-lookup-outline-24x24-v01.svg",
    "chmod_calculator": "icons/exported/icon-workflow-permission-bits-outline-24x24-v01.svg",
    "semver_tools": "icons/exported/icon-workflow-semver-compare-outline-24x24-v01.svg",
    "iso8601_duration": "icons/exported/icon-workflow-iso8601-duration-outline-24x24-v01.svg",
    "ssh_config_validator": "icons/exported/icon-workflow-ssh-config-validator-outline-24x24-v01.svg",
    "subnet_calculator": "icons/exported/icon-workflow-subnet-planning-outline-24x24-v01.svg",
    "ip_geolocation": "icons/exported/icon-workflow-ip-geolocation-outline-24x24-v01.svg",
    "totp_generator": "icons/exported/icon-workflow-totp-token-outline-24x24-v01.svg",
    "http_header_parser": "icons/exported/icon-workflow-http-header-parse-outline-24x24-v01.svg",
    "byte_size_converter": "icons/exported/icon-workflow-byte-size-convert-outline-24x24-v01.svg",
    "number_to_words": "icons/exported/icon-workflow-number-to-words-outline-24x24-v01.svg",
    "mac_address_tool": "icons/exported/icon-workflow-mac-address-outline-24x24-v01.svg",
    "email_header_analyzer": "icons/exported/icon-workflow-email-header-trace-outline-24x24-v01.svg",
    "text_diff_checker": "icons/exported/icon-workflow-text-diff-outline-24x24-v01.svg",
    "cidr_aggregator": "icons/exported/icon-workflow-cidr-aggregate-outline-24x24-v01.svg",
    "ipv6_compressor": "icons/exported/icon-workflow-ipv6-compress-outline-24x24-v01.svg",
    "outlook_safelinks_decoder": "icons/exported/icon-workflow-safe-link-unwrap-outline-24x24-v01.svg",
    "safelinks_decoder": "icons/exported/icon-workflow-safe-link-unwrap-outline-24x24-v01.svg",
    "m365_safelinks_decoder": "icons/exported/icon-workflow-safe-link-unwrap-outline-24x24-v01.svg",
    "docker_run_compose_converter": "icons/exported/icon-workflow-container-compose-outline-24x24-v01.svg",
    "docker_run_to_compose": "icons/exported/icon-workflow-container-compose-outline-24x24-v01.svg",
    "docker_compose_converter": "icons/exported/icon-workflow-container-compose-outline-24x24-v01.svg",
    "nato_phonetic_converter": "icons/exported/icon-workflow-phonetic-spellout-outline-24x24-v01.svg",
    "nato_alphabet_converter": "icons/exported/icon-workflow-phonetic-spellout-outline-24x24-v01.svg",
    "wifi_qr_generator": "icons/exported/icon-workflow-wifi-qr-share-outline-24x24-v01.svg",
    "wifi_qr_code_generator": "icons/exported/icon-workflow-wifi-qr-share-outline-24x24-v01.svg",
    "hmac_generator": "icons/exported/icon-workflow-hash-digest-outline-24x24-v01.svg",
    "ipv6_ula_generator": "icons/exported/icon-workflow-ipv6-compress-outline-24x24-v01.svg",
    "random_mac_generator": "icons/exported/icon-workflow-mac-address-outline-24x24-v01.svg",
    "random_mac_address_generator": "icons/exported/icon-workflow-mac-address-outline-24x24-v01.svg",
    "list_converter": "icons/exported/icon-workflow-list-transform-outline-24x24-v01.svg",
    "email_normalizer": "icons/exported/icon-workflow-email-normalize-outline-24x24-v01.svg",
    "email_address_normalizer": "icons/exported/icon-workflow-email-normalize-outline-24x24-v01.svg",
    "ipv4_format_converter": "icons/exported/icon-workflow-ipv4-format-outline-24x24-v01.svg",
    "ipv4_address_format_converter": "icons/exported/icon-workflow-ipv4-format-outline-24x24-v01.svg",
    "ipv4_range_expander": "icons/exported/icon-workflow-subnet-planning-outline-24x24-v01.svg",
    # Phase 37 / wave-30 target slugs with explicit per-tool artwork.
    "csr_generator": "icons/exported/icon-workflow-csr-generator-outline-24x24-v01.svg",
    "caa_record_builder": "icons/exported/icon-workflow-caa-record-builder-outline-24x24-v01.svg",
    "git_command_cheat_sheet": "icons/exported/icon-workflow-git-command-cheat-sheet-outline-24x24-v01.svg",
    "bip39_mnemonic_generator_validator": "icons/exported/icon-workflow-bip39-mnemonic-generator-validator-outline-24x24-v01.svg",
    # Phase 38 / wave-31 target slugs with explicit per-tool artwork.
    "lorem_ipsum_generator": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "text_to_binary_hex_octal_converter": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    # Backward-compatible aliases for earlier provisional/page-level slug names.
    "bip39_mnemonic_validator": "icons/exported/icon-workflow-bip39-mnemonic-generator-validator-outline-24x24-v01.svg",
    "bip39_mnemonic": "icons/exported/icon-workflow-bip39-mnemonic-generator-validator-outline-24x24-v01.svg",
    "text_radix_converter": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    # Phase 39/40/41/42/43/44/45/46/47/48/49/50 placeholder slug aliases mapped to current real tool pages.
    "157_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "158_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "157_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "158_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "159_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "160_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "159_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "160_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "165_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "166_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "165_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "166_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "167_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "168_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "167_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "168_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "169_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "170_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "169_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "170_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "171_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "172_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "171_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "172_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "173_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "174_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "173_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "174_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "175_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "176_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "175_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "176_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "177_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "178_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "177_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "178_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "179_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "180_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "179_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "180_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "181_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "182_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "181_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "182_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "183_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "184_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "183_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "184_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "185_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "186_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "185_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "186_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "187_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "188_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "187_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "188_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "189_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "190_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "189_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "190_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "191_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "192_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "191_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "192_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "193_tool_slug_pending_roadmap": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "194_tool_slug_pending_roadmap": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "193_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-lorem-ipsum-generator-outline-24x24-v01.svg",
    "194_<tool_slug_pending_roadmap>": "icons/exported/icon-workflow-text-to-binary-hex-octal-converter-outline-24x24-v01.svg",
    "csv_column_selector": "icons/exported/icon-workflow-csv-column-selector-outline-24x24-v01.svg",
    "line_numberer": "icons/exported/icon-workflow-line-numberer-outline-24x24-v01.svg",
    "column_aligner": "icons/exported/icon-workflow-column-aligner-outline-24x24-v01.svg",
    "css_gradient_generator": "icons/exported/icon-workflow-css-gradient-generator-outline-24x24-v01.svg",
}
CATEGORY_TOOL_CARD_ICON_ASSETS: dict[str, str] = {
    "Network": "icons/exported/icon-workflow-dns-lookup-outline-24x24-v01.svg",
    "Security": "icons/exported/icon-workflow-incident-response-outline-24x24-v01.svg",
    "Web & Dev": "icons/exported/icon-workflow-http-probe-outline-24x24-v01.svg",
    "Data & Text": "icons/exported/icon-workflow-json-validate-outline-24x24-v01.svg",
    "Ops & Automation": "icons/exported/icon-workflow-automation-runbook-outline-24x24-v01.svg",
    "Reference": "icons/exported/icon-workflow-reference-catalog-outline-24x24-v01.svg",
}
TOOL_HEADER_ILLUSTRATION_BY_CATEGORY: dict[str, str] = {
    "Network": "illustrations/exported/illustration-tool-network-header-flow-light-1600x900-v01.svg",
    "Security": "illustrations/exported/illustration-tool-security-header-shield-light-1600x900-v01.svg",
    "Web & Dev": "illustrations/exported/illustration-tool-web-dev-header-http-light-1600x900-v01.svg",
    "Data & Text": "illustrations/exported/illustration-tool-data-text-header-parse-light-1600x900-v01.svg",
    "Ops & Automation": "illustrations/exported/illustration-tool-ops-automation-header-pipeline-light-1600x900-v01.svg",
    "Reference": "illustrations/exported/illustration-tool-reference-header-catalog-light-1600x900-v01.svg",
}
EMPTY_STATE_ILLUSTRATIONS: dict[str, str] = {
    "ready": "illustrations/exported/illustration-empty-state-ready-checklist-light-1200x675-v01.svg",
    "network": "illustrations/exported/illustration-empty-state-ready-network-light-1200x675-v01.svg",
    "security": "illustrations/exported/illustration-empty-state-ready-shield-light-1200x675-v01.svg",
}
ROADMAP_BADGE_ICONS: dict[str, str] = {
    "status_planned": "icons/exported/icon-roadmap-planned-badge-24x24-v01.svg",
    "status_progress": "icons/exported/icon-roadmap-progress-badge-24x24-v01.svg",
    "status_done": "icons/exported/icon-roadmap-done-badge-24x24-v01.svg",
    "status_ai": "icons/exported/icon-roadmap-ai-badge-24x24-v01.svg",
    "source_seed": "icons/exported/icon-roadmap-seed-badge-24x24-v01.svg",
    "source_github": "icons/exported/icon-roadmap-github-badge-24x24-v01.svg",
}
TRANSIENT_FAILURE_HINTS: tuple[str, ...] = (
    "timeout",
    "timed out",
    "temporar",
    "unavailable",
    "rate limit",
    "429",
    "503",
    "502",
    "connection",
    "refused",
    "reset",
    "dns lookup timed out",
    "nameserver",
    "eai_again",
)
PERSISTENT_FAILURE_HINTS: tuple[str, ...] = (
    "invalid",
    "does not exist",
    "nxdomain",
    "no answer",
    "expired",
    "hostname mismatch",
    "port must be",
    "certificate verification failed",
)


@lru_cache(maxsize=256)
def _svg_data_uri(relative_path: str) -> str | None:
    asset_path = ASSETS_ROOT / relative_path
    if not asset_path.exists() or asset_path.suffix.lower() != ".svg":
        return None
    return "data:image/svg+xml;base64," + base64.b64encode(asset_path.read_bytes()).decode("ascii")


def _svg_img_html(relative_path: str, alt: str, class_name: str, decorative: bool = False) -> str | None:
    uri = _svg_data_uri(relative_path)
    if not uri:
        return None
    alt_text = "" if decorative else escape(alt)
    decorative_attrs = ' aria-hidden="true" role="presentation"' if decorative else ""
    return (
        f'<img class="{escape(class_name)}" src="{uri}" alt="{alt_text}"{decorative_attrs} loading="lazy" decoding="async">'
    )


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
    aliases: tuple[str, ...] = ()


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
    "Data & Text",
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
        category="Data & Text",
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
        category="Data & Text",
        aliases=("b64",),
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
        category="Data & Text",
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
        category="Data & Text",
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
    ),
    ToolMeta(
        title="CIDR Aggregator",
        short_title="CIDR Aggregator",
        description="Summarize a list of IPs or CIDR blocks into the minimal set of covering supernets.",
        path="pages/22_CIDR_Aggregator.py",
        icon="AGG",
        accent="#0e7490",
        slug="cidr_aggregator",
        professions=("Network Engineer", "Sysadmin / DevOps", "Cloud Engineer"),
        category="Network",
    ),
    ToolMeta(
        title="User-Agent Parser",
        short_title="User-Agent Parser",
        description="Break a User-Agent header down into likely browser, OS, and device details.",
        path="pages/23_User_Agent_Parser.py",
        icon="UAP",
        accent="#c026d3",
        slug="user_agent_parser",
        professions=("Support Engineer", "Web Developer", "Helpdesk / L1"),
        category="Web & Dev",
    ),
    ToolMeta(
        title="IPv6 Compressor",
        short_title="IPv6 Compressor",
        description="Convert an IPv6 address between its compressed (::) and fully expanded form.",
        path="pages/24_IPv6_Compressor.py",
        icon="V6",
        accent="#0369a1",
        slug="ipv6_compressor",
        professions=("Network Engineer", "Sysadmin / DevOps"),
        category="Network",
    ),
    ToolMeta(
        title="Case Converter",
        short_title="Case Converter",
        description="Convert text between slug-case, snake_case, camelCase, PascalCase, and Title Case.",
        path="pages/25_Case_Converter.py",
        icon="Aa",
        accent="#ca8a04",
        slug="case_converter",
        professions=("Web Developer", "Automation Engineer"),
        category="Data & Text",
    ),
    ToolMeta(
        title="Color Converter",
        short_title="Color Converter",
        description="Convert colors between HEX, RGB, and HSL, with a live swatch preview.",
        path="pages/26_Color_Converter.py",
        icon="RGB",
        accent="#db2777",
        slug="color_converter",
        professions=("Web Developer", "Automation Engineer"),
        category="Data & Text",
    ),
    ToolMeta(
        title="WHOIS Lookup",
        short_title="WHOIS Lookup",
        description="Look up domain registration details (registrar, key dates, name servers) via RDAP.",
        path="pages/27_WHOIS_Lookup.py",
        icon="WHO",
        accent="#0d9488",
        slug="whois_lookup",
        professions=("Network Engineer", "Security Engineer", "Sysadmin / DevOps", "Web Developer"),
        category="Network",
    ),
    ToolMeta(
        title="Bulk Domain Health",
        short_title="Bulk Domain Health",
        description="Run the Domain Health Checker's core checks across a list of public domains at once.",
        path="pages/28_Bulk_Domain_Health.py",
        icon="CSV",
        accent="#1668f4",
        slug="bulk_domain_health",
        professions=("Network Engineer", "Security Engineer", "Sysadmin / DevOps", "Web Developer"),
        category="Network",
    ),
    ToolMeta(
        title="Webhook Tester",
        short_title="Webhook Tester",
        description="Send a one-off HTTP request with a custom method, headers, and body.",
        path="pages/29_Webhook_Tester.py",
        icon="HTP",
        accent="#ff6b13",
        slug="webhook_tester",
        professions=("Web Developer", "Automation Engineer", "Sysadmin / DevOps"),
        category="Web & Dev",
    ),
    ToolMeta(
        title="Uptime Trend",
        short_title="Uptime Trend",
        description="Run a short, one-off series of checks against a URL and see the latency trend for this session only.",
        path="pages/30_Uptime_Trend.py",
        icon="UPT",
        accent="#0e9f6e",
        slug="uptime_trend",
        professions=("Sysadmin / DevOps", "Support Engineer", "Web Developer"),
        category="Web & Dev",
    ),
    ToolMeta(
        title="Security Headers Checker",
        short_title="Security Headers",
        description="Grade a URL's response security headers (HSTS, CSP, and more), similar to securityheaders.com.",
        path="pages/31_Security_Headers_Checker.py",
        icon="SHC",
        accent="#e63946",
        slug="security_headers",
        professions=("Sysadmin / DevOps", "Web Developer", "Security Engineer"),
        category="Security",
    ),
    ToolMeta(
        title="CVE Lookup",
        short_title="CVE Lookup",
        description="Search the NIST National Vulnerability Database by CVE ID or keyword.",
        path="pages/32_CVE_Lookup.py",
        icon="CVE",
        accent="#c1121f",
        slug="cve_lookup",
        professions=("Security Engineer", "Sysadmin / DevOps", "Support Engineer"),
        category="Security",
    ),
    ToolMeta(
        title="DNS Propagation Checker",
        short_title="DNS Propagation",
        description="Query the same DNS record across several public resolvers to catch propagation lag or mismatches.",
        path="pages/33_DNS_Propagation_Checker.py",
        icon="DPC",
        accent="#0077b6",
        slug="dns_propagation",
        professions=("Sysadmin / DevOps", "Network Engineer", "Support Engineer"),
        category="Network",
    ),
    ToolMeta(
        title="Windows Event Reference",
        short_title="Windows Events",
        description="Look up common Windows Event Log IDs by number, log, source, severity, or keyword.",
        path="pages/34_Windows_Event_Reference.py",
        icon="WEV",
        accent="#5c6bc0",
        slug="windows_event_reference",
        professions=("Sysadmin / DevOps", "Support Engineer", "Helpdesk / L1"),
        category="Reference",
    ),
    ToolMeta(
        title="DKIM Selector Lookup",
        short_title="DKIM Lookup",
        description="Look up a DKIM TXT record for a domain and selector, and parse its public key/algorithm fields.",
        path="pages/35_DKIM_Selector_Lookup.py",
        icon="DKM",
        accent="#2a9d8f",
        slug="dkim_lookup",
        professions=("Sysadmin / DevOps", "Security Engineer", "Support Engineer"),
        category="Network",
    ),
    ToolMeta(
        title="Email Record Builder",
        short_title="Email Records",
        description="Build SPF, DMARC, and DKIM TXT record strings from simple inputs -- the reverse of the existing checks.",
        path="pages/36_Email_Record_Builder.py",
        icon="ERB",
        accent="#f4a261",
        slug="email_record_builder",
        professions=("Sysadmin / DevOps", "Security Engineer", "Support Engineer"),
        category="Network",
    ),
    ToolMeta(
        title="Windows Error Reference",
        short_title="Windows Errors",
        description="Look up Windows/Win32 error codes (decimal or hex) -- Win32, service control, RPC, HRESULT, and NTSTATUS.",
        path="pages/37_Windows_Error_Reference.py",
        icon="WER",
        accent="#8d99ae",
        slug="windows_error_reference",
        professions=("Sysadmin / DevOps", "Support Engineer", "Helpdesk / L1"),
        category="Reference",
    ),
    ToolMeta(
        title="Config Format Converter",
        short_title="Config Converter",
        description="Convert a config snippet between JSON, YAML, TOML, and XML.",
        path="pages/38_Config_Format_Converter.py",
        icon="CFC",
        accent="#457b9d",
        slug="config_format_converter",
        professions=("Sysadmin / DevOps", "Web Developer", "Automation Engineer"),
        category="Data & Text",
    ),
    ToolMeta(
        title="M365 SKU Decoder",
        short_title="M365 SKU Decoder",
        description="Convert Microsoft 365 license SKU strings and GUIDs to readable product names.",
        path="pages/39_M365_SKU_Decoder.py",
        icon="M365",
        accent="#0078d4",
        slug="m365_sku_decoder",
        professions=("Sysadmin / DevOps", "Support Engineer", "Helpdesk / L1"),
        category="Reference",
    ),
    ToolMeta(
        title="ID Generator",
        short_title="ID Generator",
        description="Generate UUIDs (v4) or ULIDs in bulk.",
        path="pages/40_ID_Generator.py",
        icon="UID",
        accent="#6d597a",
        slug="id_generator",
        professions=("Web Developer", "Automation Engineer", "Sysadmin / DevOps"),
        category="Data & Text",
    ),
    ToolMeta(
        title="JSON Diff Viewer",
        short_title="JSON Diff",
        description="Structurally compare two JSON documents by key/path, not by line.",
        path="pages/41_JSON_Diff_Viewer.py",
        icon="JDF",
        accent="#118ab2",
        slug="json_diff",
        professions=("Web Developer", "Automation Engineer", "Sysadmin / DevOps"),
        category="Data & Text",
    ),
    ToolMeta(
        title="IP Geolocation Lookup",
        short_title="IP Geolocation",
        description="Resolve an IP address to approximate geography, ASN, and ISP/org info.",
        path="pages/42_IP_Geolocation_Lookup.py",
        icon="GEO",
        accent="#2a9d8f",
        slug="ip_geolocation",
        professions=("Sysadmin / DevOps", "Security Engineer", "Support Engineer"),
        category="Network",
    ),
    ToolMeta(
        title="File Integrity Comparator",
        short_title="File Integrity",
        description="Compare two files, or check one file against an expected hash, to confirm a download wasn't corrupted or tampered with.",
        path="pages/43_File_Integrity_Comparator.py",
        icon="FIC",
        accent="#e76f51",
        slug="file_integrity",
        professions=("Sysadmin / DevOps", "Security Engineer", "Support Engineer"),
        category="Security",
    ),
    ToolMeta(
        title="chmod Calculator",
        short_title="chmod Calculator",
        description="Convert between symbolic (rwxr-xr-x) and octal (755) Unix file permission notation.",
        path="pages/44_Chmod_Calculator.py",
        icon="CHM",
        accent="#5c6bc0",
        slug="chmod_calculator",
        professions=("Sysadmin / DevOps", "Automation Engineer"),
        category="Ops & Automation",
    ),
    ToolMeta(
        title="Integer Base Converter",
        short_title="Base Converter",
        description="Convert a number between binary, octal, decimal, and hexadecimal, live as you type.",
        path="pages/45_Integer_Base_Converter.py",
        icon="BAS",
        accent="#264653",
        slug="base_converter",
        professions=("Web Developer", "Automation Engineer", "Sysadmin / DevOps"),
        category="Data & Text",
    ),
    ToolMeta(
        title="Cron Expression Builder",
        short_title="Cron Builder",
        description="Build a 5-field cron expression from simple controls -- the reverse of Cron Explainer.",
        path="pages/46_Cron_Expression_Builder.py",
        icon="CRB",
        accent="#0e9f6e",
        slug="cron_builder",
        professions=("Sysadmin / DevOps", "Automation Engineer"),
        category="Ops & Automation",
    ),
    ToolMeta(
        title="HTTP Status Reference",
        short_title="HTTP Status Reference",
        description="Look up HTTP status codes by number, category, or keyword.",
        path="pages/47_HTTP_Status_Reference.py",
        icon="STS",
        accent="#e63946",
        slug="http_status_reference",
        professions=("Web Developer", "Sysadmin / DevOps", "Support Engineer"),
        category="Reference",
    ),
    ToolMeta(
        title="TOTP Generator",
        short_title="TOTP Generator",
        description="Generate and validate time-based one-time passcodes (TOTP) from a shared secret.",
        path="pages/48_TOTP_Generator.py",
        icon="OTP",
        accent="#7209b7",
        slug="totp_generator",
        professions=("Security Engineer", "Sysadmin / DevOps", "Support Engineer"),
        category="Security",
    ),
    ToolMeta(
        title="RSA/SSH Key Pair Generator",
        short_title="Key Pair Generator",
        description="Generate a disposable RSA or Ed25519 key pair for test/throwaway use.",
        path="pages/49_RSA_SSH_Key_Pair_Generator.py",
        icon="KEY",
        accent="#ffb703",
        slug="keypair_generator",
        professions=("Sysadmin / DevOps", "Security Engineer", "Automation Engineer"),
        category="Security",
    ),
    ToolMeta(
        title="QR Code Generator",
        short_title="QR Code Generator",
        description="Generate a QR code for a URL, plain text, or Wi-Fi credentials.",
        path="pages/50_QR_Code_Generator.py",
        icon="QRC",
        accent="#219ebc",
        slug="qr_code_generator",
        professions=("Support Engineer", "Helpdesk / L1", "Sysadmin / DevOps"),
        category="Data & Text",
    ),
    ToolMeta(
        title="Bcrypt Tool",
        short_title="Bcrypt Tool",
        description="Hash a value with bcrypt, or verify a value against an existing bcrypt hash.",
        path="pages/51_Bcrypt_Tool.py",
        icon="BCR",
        accent="#023047",
        slug="bcrypt_tool",
        professions=("Web Developer", "Security Engineer", "Sysadmin / DevOps"),
        category="Security",
    ),
    ToolMeta(
        title="SQL Formatter",
        short_title="SQL Formatter",
        description="Reformat a pasted SQL query with consistent indentation and keyword casing.",
        path="pages/52_SQL_Formatter.py",
        icon="SQL",
        accent="#8338ec",
        slug="sql_formatter",
        professions=("Sysadmin / DevOps", "Web Developer", "Automation Engineer"),
        category="Data & Text",
    ),
    ToolMeta(
        title="ULID/UUID Decoder",
        short_title="ULID/UUID Decoder",
        description="Decode a ULID or UUID's embedded creation timestamp -- the reverse of ID Generator.",
        path="pages/53_ULID_UUID_Decoder.py",
        icon="UID",
        accent="#00b4d8",
        slug="ulid_uuid_decoder",
        professions=("Web Developer", "Automation Engineer", "Sysadmin / DevOps"),
        category="Data & Text",
    ),
    ToolMeta(
        title="curl Command Builder",
        short_title="curl Builder",
        description="Build a copy-pasteable curl command from a method, URL, headers, and body -- the reverse of Webhook Tester.",
        path="pages/54_Curl_Command_Builder.py",
        icon="CURL",
        accent="#fb8500",
        slug="curl_builder",
        professions=("Web Developer", "Automation Engineer", "Sysadmin / DevOps"),
        category="Web & Dev",
    ),
    ToolMeta(
        title="Regex Cheat Sheet",
        short_title="Regex Cheat Sheet",
        description="Common regex patterns to start from -- email, IPv4/IPv6, URL, phone number, UUID, hex color, and more.",
        path="pages/55_Regex_Cheat_Sheet.py",
        icon=".*",
        accent="#0891b2",
        slug="regex_cheat_sheet",
        professions=("Automation Engineer", "Web Developer", "Support Engineer"),
        category="Reference",
    ),
    ToolMeta(
        title=".env File Linter",
        short_title=".env Linter",
        description="Flag duplicate keys, unquoted values with spaces, unterminated quotes, and other common .env mistakes.",
        path="pages/56_Env_File_Linter.py",
        icon="ENV",
        accent="#2a9d8f",
        slug="env_linter",
        professions=("Sysadmin / DevOps", "Web Developer", "Automation Engineer"),
        category="Data & Text",
    ),
    ToolMeta(
        title="TLS Protocol Scanner",
        short_title="TLS Scanner",
        description="Connect to a host and report which TLS protocol versions it accepts -- a lightweight SSL Labs-style check.",
        path="pages/57_TLS_Protocol_Scanner.py",
        icon="TLS",
        accent="#e63946",
        slug="tls_scanner",
        professions=("Security Engineer", "Sysadmin / DevOps", "Network Engineer"),
        category="Security",
    ),
    ToolMeta(
        title="Business Hours Calculator",
        short_title="Business Hours",
        description="Compute elapsed business hours between two timestamps, excluding weekends and holidays -- for SLA and ticket-response math.",
        path="pages/58_Business_Hours_Calculator.py",
        icon="SLA",
        accent="#f4a261",
        slug="business_hours",
        professions=("Sysadmin / DevOps", "Support Engineer", "Automation Engineer"),
        category="Ops & Automation",
    ),
    ToolMeta(
        title="CSV Diff Viewer",
        short_title="CSV Diff Viewer",
        description="Structurally compare two CSVs by a key column -- added, removed, and changed rows, not a line-by-line diff.",
        path="pages/59_CSV_Diff_Viewer.py",
        icon="CSV",
        accent="#06d6a0",
        slug="csv_diff",
        professions=("Automation Engineer", "Web Developer", "Sysadmin / DevOps"),
        category="Data & Text",
        is_new=True,
    ),
    ToolMeta(
        title="Markdown/HTML Converter",
        short_title="Markdown/HTML",
        description="Convert text between Markdown and HTML.",
        path="pages/60_Markdown_HTML_Converter.py",
        icon="MD",
        accent="#3a86ff",
        slug="markdown_converter",
        professions=("Web Developer", "Automation Engineer", "Support Engineer"),
        category="Data & Text",
        is_new=True,
    ),
    ToolMeta(
        title="Text Encoding Detector",
        short_title="Encoding Detector",
        description="Upload a text file to detect its character encoding, preview the decoded content, and convert it to UTF-8.",
        path="pages/61_Text_Encoding_Detector.py",
        icon="ENC",
        accent="#118ab2",
        slug="encoding_detector",
        professions=("Sysadmin / DevOps", "Web Developer", "Automation Engineer"),
        category="Data & Text",
        is_new=True,
    ),
    ToolMeta(
        title="robots.txt / Sitemap Validator",
        short_title="robots.txt Validator",
        description="Fetch a domain's robots.txt, validate its directive syntax, and check that its referenced sitemaps are reachable and well-formed.",
        path="pages/62_Robots_Sitemap_Validator.py",
        icon="BOT",
        accent="#ef476f",
        slug="robots_validator",
        professions=("Web Developer", "Sysadmin / DevOps", "Automation Engineer"),
        category="Web & Dev",
        is_new=True,
    ),
    ToolMeta(
        title="JWT Weak-Secret Checker",
        short_title="JWT Weak-Secret",
        description="Test a JWT's HMAC signature against a small built-in list of common weak secrets.",
        path="pages/63_JWT_Weak_Secret_Checker.py",
        icon="JWT",
        accent="#ffd166",
        slug="jwt_weak_secret",
        professions=("Security Engineer", "Web Developer", "Sysadmin / DevOps"),
        category="Security",
        is_new=True,
    ),
    ToolMeta(
        title="Log Timestamp Duration Calculator",
        short_title="Log Duration",
        description="Compute the elapsed duration between two log timestamps -- auto-detects ISO 8601, Apache/nginx access log, and syslog formats.",
        path="pages/64_Log_Timestamp_Duration_Calculator.py",
        icon="LOG",
        accent="#8338ec",
        slug="log_duration",
        professions=("Sysadmin / DevOps", "Support Engineer", "Automation Engineer"),
        category="Ops & Automation",
    ),
    ToolMeta(
        title="URL Parser",
        short_title="URL Parser",
        description="Break a URL down into its scheme, host, port, path, query parameters, and fragment.",
        path="pages/65_URL_Parser.py",
        icon="URL",
        accent="#4361ee",
        slug="url_parser",
        professions=("Web Developer", "Automation Engineer", "Sysadmin / DevOps"),
        category="Web & Dev",
    ),
    ToolMeta(
        title="Base32 Encoder/Decoder",
        short_title="Base32 Tool",
        description="Encode and decode Base32 (RFC 4648) text -- the encoding TOTP secrets use.",
        path="pages/66_Base32_Encoder_Decoder.py",
        icon="B32",
        accent="#f77f00",
        slug="base32_tools",
        professions=("Sysadmin / DevOps", "Web Developer", "Security Engineer"),
        category="Data & Text",
    ),
    ToolMeta(
        title="HTTP Header Parser",
        short_title="Header Parser",
        description="Paste raw HTTP request or response headers and see them parsed and explained -- no network call.",
        path="pages/67_HTTP_Header_Parser.py",
        icon="HDR",
        accent="#00a878",
        slug="http_header_parser",
        professions=("Web Developer", "Sysadmin / DevOps", "Support Engineer"),
        category="Web & Dev",
    ),
    ToolMeta(
        title="CIDR Overlap Checker",
        short_title="CIDR Overlap",
        description="Check whether any of a list of IPs or CIDR blocks overlap -- a pre-flight check before allocating a new subnet.",
        path="pages/68_CIDR_Overlap_Checker.py",
        icon="OVL",
        accent="#d62828",
        slug="cidr_overlap",
        professions=("Network Engineer", "Sysadmin / DevOps", "Cloud Engineer"),
        category="Network",
    ),
    ToolMeta(
        title="CSR Decoder",
        short_title="CSR Decoder",
        description="Decode a PEM-encoded Certificate Signing Request -- subject, SAN entries, public key info, and signature validity.",
        path="pages/69_CSR_Decoder.py",
        icon="CSR",
        accent="#fca311",
        slug="csr_decoder",
        professions=("Security Engineer", "Sysadmin / DevOps", "Web Developer"),
        category="Security",
    ),
    ToolMeta(
        title="PEM Bundle Splitter",
        short_title="PEM Splitter",
        description="Paste a multi-certificate PEM bundle and see each certificate's subject, issuer, and expiration separately.",
        path="pages/70_PEM_Bundle_Splitter.py",
        icon="PEM",
        accent="#2ec4b6",
        slug="pem_bundle_splitter",
        professions=("Security Engineer", "Sysadmin / DevOps", "Web Developer"),
        category="Security",
    ),
    ToolMeta(
        title="Whitespace Visualizer",
        short_title="Whitespace Visualizer",
        description="Find non-breaking spaces, zero-width characters, and other invisible characters that commonly cause silent copy-paste bugs.",
        path="pages/71_Whitespace_Visualizer.py",
        icon="WSV",
        accent="#e07a5f",
        slug="whitespace_visualizer",
        professions=("Sysadmin / DevOps", "Web Developer", "Automation Engineer"),
        category="Data & Text",
    ),
    ToolMeta(
        title="Date Calculator",
        short_title="Date Calculator",
        description="Add or subtract days/weeks/months from a date, or compute the number of calendar days between two dates.",
        path="pages/72_Date_Calculator.py",
        icon="DATE",
        accent="#6a4c93",
        slug="date_calculator",
        professions=("Sysadmin / DevOps", "Support Engineer", "Automation Engineer"),
        category="Ops & Automation",
    ),
    ToolMeta(
        title="XML Formatter",
        short_title="XML Formatter",
        description="Pretty-print, minify, or validate arbitrary XML.",
        path="pages/73_XML_Formatter.py",
        icon="XML",
        accent="#1565c0",
        slug="xml_formatter",
        professions=("Web Developer", "Automation Engineer", "Sysadmin / DevOps"),
        category="Data & Text",
    ),
    ToolMeta(
        title="HTML Entity Encoder/Decoder",
        short_title="HTML Entity Tool",
        description="Encode text to HTML entities, or decode HTML entities (including numeric character references) back to plain text.",
        path="pages/74_HTML_Entity_Encoder_Decoder.py",
        icon="HTM",
        accent="#ff7f11",
        slug="html_entity_tools",
        professions=("Web Developer", "Automation Engineer", "Support Engineer"),
        category="Web & Dev",
    ),
    ToolMeta(
        title="Deterministic UUID Generator",
        short_title="Deterministic UUID",
        description="Generate a namespace-based UUID (v3 MD5 or v5 SHA-1) -- the same namespace and name always produce the same UUID.",
        path="pages/75_Deterministic_UUID_Generator.py",
        icon="DUID",
        accent="#3f37c9",
        slug="deterministic_uuid",
        professions=("Web Developer", "Automation Engineer", "Sysadmin / DevOps"),
        category="Data & Text",
    ),
    ToolMeta(
        title="Luhn Checksum Validator",
        short_title="Luhn Validator",
        description="Validate a credit card number, IMEI, or other Luhn-checksummed number, and see the check digit for its payload.",
        path="pages/76_Luhn_Checksum_Validator.py",
        icon="LUHN",
        accent="#f15bb5",
        slug="luhn_validator",
        professions=("Support Engineer", "Web Developer", "Sysadmin / DevOps"),
        category="Security",
    ),
    ToolMeta(
        title="Text Statistics",
        short_title="Text Statistics",
        description="Paste text to see word, character, and sentence counts, plus the most frequent words.",
        path="pages/77_Text_Statistics.py",
        icon="TXT",
        accent="#ee9b00",
        slug="text_stats",
        professions=("Support Engineer", "Automation Engineer", "Web Developer"),
        category="Data & Text",
    ),
    ToolMeta(
        title="CSV to Markdown Table",
        short_title="CSV to Markdown",
        description="Paste CSV or TSV and get a Markdown table, ready to paste into a README, PR description, or wiki page.",
        path="pages/78_CSV_to_Markdown_Table.py",
        icon="MDT",
        accent="#4895ef",
        slug="csv_to_markdown",
        professions=("Automation Engineer", "Web Developer", "Sysadmin / DevOps"),
        category="Data & Text",
    ),
    ToolMeta(
        title="SSH Key Fingerprint",
        short_title="SSH Fingerprint",
        description="Paste a public SSH key (or a known_hosts line) to see its MD5 and SHA256 fingerprints, matching ssh-keygen -lf's output.",
        path="pages/79_SSH_Key_Fingerprint.py",
        icon="FP",
        accent="#2d6a4f",
        slug="ssh_fingerprint",
        professions=("Security Engineer", "Sysadmin / DevOps", "Web Developer"),
        category="Security",
    ),
    ToolMeta(
        title="YAML Formatter",
        short_title="YAML Formatter",
        description="Paste YAML and get it consistently re-indented, or flagged with a clear error if it's not valid YAML.",
        path="pages/80_YAML_Formatter.py",
        icon="YML",
        accent="#8ac926",
        slug="yaml_formatter",
        professions=("Sysadmin / DevOps", "Web Developer", "Automation Engineer"),
        category="Data & Text",
        is_new=True,
    ),
    ToolMeta(
        title="Byte Size Converter",
        short_title="Byte Size Converter",
        description="Convert a byte count to human-readable units (KB/MB/GB/TB), or the reverse.",
        path="pages/81_Byte_Size_Converter.py",
        icon="B",
        accent="#1982c4",
        slug="byte_size_converter",
        professions=("Sysadmin / DevOps", "Cloud Engineer", "Support Engineer"),
        category="Ops & Automation",
        is_new=True,
    ),
    ToolMeta(
        title="Line Ending Converter",
        short_title="Line Ending Converter",
        description="Convert pasted text between CRLF (Windows), LF (Unix/Mac), and CR (classic Mac) line endings.",
        path="pages/82_Line_Ending_Converter.py",
        icon="LE",
        accent="#9d4edd",
        slug="line_ending_converter",
        professions=("Web Developer", "Sysadmin / DevOps", "Automation Engineer"),
        category="Web & Dev",
        is_new=True,
    ),
    ToolMeta(
        title="Regex Find & Replace",
        short_title="Regex Find/Replace",
        description="Paste text and a regex pattern with a replacement, and see the substituted output.",
        path="pages/83_Regex_Find_Replace.py",
        icon="R/R",
        accent="#ff595e",
        slug="regex_replace",
        professions=("Automation Engineer", "Web Developer", "Sysadmin / DevOps"),
        category="Data & Text",
        is_new=True,
    ),
    ToolMeta(
        title="Password Strength Checker",
        short_title="Password Strength",
        description="Paste a password to see an estimated entropy and rough strength category.",
        path="pages/84_Password_Strength_Checker.py",
        icon="PWS",
        accent="#fee440",
        slug="password_entropy",
        professions=("Security Engineer", "Support Engineer", "Sysadmin / DevOps"),
        category="Security",
        is_new=True,
    ),
    ToolMeta(
        title="Text Pattern Extractor",
        short_title="Pattern Extractor",
        description="Paste text and a regex pattern, and get back only the matching lines -- like grep -E over pasted text.",
        path="pages/85_Text_Pattern_Extractor.py",
        icon="GREP",
        accent="#00bbf9",
        slug="pattern_extractor",
        professions=("Automation Engineer", "Sysadmin / DevOps", "Support Engineer"),
        category="Ops & Automation",
        is_new=True,
    ),
    ToolMeta(
        title="ULID/UUID Decoder",
        short_title="ULID/UUID Decoder",
        description="Decode a ULID or UUID's embedded creation timestamp -- the reverse of ID Generator.",
        path="pages/53_ULID_UUID_Decoder.py",
        icon="UID",
        accent="#00b4d8",
        slug="ulid_uuid_decoder",
        professions=("Web Developer", "Automation Engineer", "Sysadmin / DevOps"),
        category="Data & Text",
        is_new=True,
    ),
    ToolMeta(
        title="curl Command Builder",
        short_title="curl Builder",
        description="Build a copy-pasteable curl command from a method, URL, headers, and body -- the reverse of Webhook Tester.",
        path="pages/54_Curl_Command_Builder.py",
        icon="CURL",
        accent="#fb8500",
        slug="curl_builder",
        professions=("Web Developer", "Automation Engineer", "Sysadmin / DevOps"),
        category="Web & Dev",
        is_new=True,
    ),
    ToolMeta(
        title="Regex Cheat Sheet",
        short_title="Regex Cheat Sheet",
        description="Common regex patterns to start from -- email, IPv4/IPv6, URL, phone number, UUID, hex color, and more.",
        path="pages/55_Regex_Cheat_Sheet.py",
        icon=".*",
        accent="#0891b2",
        slug="regex_cheat_sheet",
        professions=("Automation Engineer", "Web Developer", "Support Engineer"),
        category="Reference",
        is_new=True,
    ),
    ToolMeta(
        title="Bcrypt Tool",
        short_title="Bcrypt Tool",
        description="Hash a value with bcrypt, or verify a value against an existing bcrypt hash.",
        path="pages/51_Bcrypt_Tool.py",
        icon="BCR",
        accent="#023047",
        slug="bcrypt_tool",
        professions=("Web Developer", "Security Engineer", "Sysadmin / DevOps"),
        category="Security",
        is_new=True,
    ),
    ToolMeta(
        title="chmod Calculator",
        short_title="chmod Calculator",
        description="Convert between symbolic (rwxr-xr-x) and octal (755) Unix file permission notation.",
        path="pages/44_Chmod_Calculator.py",
        icon="CHM",
        accent="#5c6bc0",
        slug="chmod_calculator",
        professions=("Sysadmin / DevOps", "Automation Engineer"),
        category="Ops & Automation",
        is_new=True,
    ),
    ToolMeta(
        title="Config Format Converter",
        short_title="Config Converter",
        description="Convert a config snippet between JSON, YAML, TOML, and XML.",
        path="pages/38_Config_Format_Converter.py",
        icon="CFC",
        accent="#457b9d",
        slug="config_format_converter",
        professions=("Sysadmin / DevOps", "Web Developer", "Automation Engineer"),
        category="Web & Dev",
        is_new=True,
    ),
    ToolMeta(
        title="Cron Expression Builder",
        short_title="Cron Builder",
        description="Build a 5-field cron expression from simple controls -- the reverse of Cron Explainer.",
        path="pages/46_Cron_Expression_Builder.py",
        icon="CRB",
        accent="#0e9f6e",
        slug="cron_builder",
        professions=("Sysadmin / DevOps", "Automation Engineer"),
        category="Ops & Automation",
        is_new=True,
    ),
    ToolMeta(
        title="CVE Lookup",
        short_title="CVE Lookup",
        description="Search the NIST National Vulnerability Database by CVE ID or keyword.",
        path="pages/32_CVE_Lookup.py",
        icon="CVE",
        accent="#c1121f",
        slug="cve_lookup",
        professions=("Security Engineer", "Sysadmin / DevOps", "Support Engineer"),
        category="Security",
        is_new=True,
    ),
    ToolMeta(
        title="DNS Propagation Checker",
        short_title="DNS Propagation",
        description="Query the same DNS record across several public resolvers to catch propagation lag or mismatches.",
        path="pages/33_DNS_Propagation_Checker.py",
        icon="DPC",
        accent="#0077b6",
        slug="dns_propagation",
        professions=("Sysadmin / DevOps", "Network Engineer", "Support Engineer"),
        category="Network",
        is_new=True,
    ),
    ToolMeta(
        title="Windows Event Reference",
        short_title="Windows Events",
        description="Look up common Windows Event Log IDs by number, log, source, severity, or keyword.",
        path="pages/34_Windows_Event_Reference.py",
        icon="WEV",
        accent="#5c6bc0",
        slug="windows_event_reference",
        professions=("Sysadmin / DevOps", "Support Engineer", "Helpdesk / L1"),
        category="Reference",
        is_new=True,
    ),
    ToolMeta(
        title="DKIM Selector Lookup",
        short_title="DKIM Lookup",
        description="Look up a DKIM TXT record for a domain and selector, and parse its public key/algorithm fields.",
        path="pages/35_DKIM_Selector_Lookup.py",
        icon="DKM",
        accent="#2a9d8f",
        slug="dkim_lookup",
        professions=("Sysadmin / DevOps", "Security Engineer", "Support Engineer"),
        category="Network",
        is_new=True,
    ),
    ToolMeta(
        title="Email Record Builder",
        short_title="Email Records",
        description="Build SPF, DMARC, and DKIM TXT record strings from simple inputs -- the reverse of the existing checks.",
        path="pages/36_Email_Record_Builder.py",
        icon="ERB",
        accent="#f4a261",
        slug="email_record_builder",
        professions=("Sysadmin / DevOps", "Security Engineer", "Support Engineer"),
        category="Network",
        is_new=True,
    ),
    ToolMeta(
        title="Windows Error Reference",
        short_title="Windows Errors",
        description="Look up Windows/Win32 error codes (decimal or hex) -- Win32, service control, RPC, HRESULT, and NTSTATUS.",
        path="pages/37_Windows_Error_Reference.py",
        icon="WER",
        accent="#8d99ae",
        slug="windows_error_reference",
        professions=("Sysadmin / DevOps", "Support Engineer", "Helpdesk / L1"),
        category="Reference",
        is_new=True,
    ),
    ToolMeta(
        title="Config Format Converter",
        short_title="Config Converter",
        description="Convert a config snippet between JSON, YAML, TOML, and XML.",
        path="pages/38_Config_Format_Converter.py",
        icon="CFC",
        accent="#457b9d",
        slug="config_format_converter",
        professions=("Sysadmin / DevOps", "Web Developer", "Automation Engineer"),
        category="Web & Dev",
        is_new=True,
    ),
    ToolMeta(
        title="M365 SKU Decoder",
        short_title="M365 SKU Decoder",
        description="Convert Microsoft 365 license SKU strings and GUIDs to readable product names.",
        path="pages/39_M365_SKU_Decoder.py",
        icon="M365",
        accent="#0078d4",
        slug="m365_sku_decoder",
        professions=("Sysadmin / DevOps", "Support Engineer", "Helpdesk / L1"),
        category="Reference",
        is_new=True,
    ),
    ToolMeta(
        title="ID Generator",
        short_title="ID Generator",
        description="Generate UUIDs (v4) or ULIDs in bulk.",
        path="pages/40_ID_Generator.py",
        icon="UID",
        accent="#6d597a",
        slug="id_generator",
        professions=("Web Developer", "Automation Engineer", "Sysadmin / DevOps"),
        category="Web & Dev",
        is_new=True,
    ),
    ToolMeta(
        title="JSON Diff Viewer",
        short_title="JSON Diff",
        description="Structurally compare two JSON documents by key/path, not by line.",
        path="pages/41_JSON_Diff_Viewer.py",
        icon="JDF",
        accent="#118ab2",
        slug="json_diff",
        professions=("Web Developer", "Automation Engineer", "Sysadmin / DevOps"),
        category="Web & Dev",
        is_new=True,
    ),
    ToolMeta(
        title="IP Geolocation Lookup",
        short_title="IP Geolocation",
        description="Resolve an IP address to approximate geography, ASN, and ISP/org info.",
        path="pages/42_IP_Geolocation_Lookup.py",
        icon="GEO",
        accent="#2a9d8f",
        slug="ip_geolocation",
        professions=("Sysadmin / DevOps", "Security Engineer", "Support Engineer"),
        category="Network",
        is_new=True,
    ),
    ToolMeta(
        title="File Integrity Comparator",
        short_title="File Integrity",
        description="Compare two files, or check one file against an expected hash, to confirm a download wasn't corrupted or tampered with.",
        path="pages/43_File_Integrity_Comparator.py",
        icon="FIC",
        accent="#e76f51",
        slug="file_integrity",
        professions=("Sysadmin / DevOps", "Security Engineer", "Support Engineer"),
        category="Security",
        is_new=True,
    ),
)

# Curated, not usage-derived -- this app deliberately has no usage tracking
# (Public Safe, no signup). Originally a frozen TOOLS[:5] slice pinned to the
# first tools ever shipped; refreshed to include a couple of broadly-useful
# later additions so this row doesn't read as permanently stuck on session-1
# tools now that the catalog has grown to 51.
_POPULAR_SLUGS = ("domain_health", "dns_records", "ssl_certificate", "security_headers", "cve_lookup")
_tools_by_slug = {tool.slug: tool for tool in TOOLS}
POPULAR_TOOLS = tuple(_tools_by_slug[slug] for slug in _POPULAR_SLUGS)
del _tools_by_slug
TITLE_TO_SLUG: dict[str, str] = {tool.title: tool.slug for tool in TOOLS}

# Curated "what would you naturally run next" pairings for a real troubleshooting
# flow (e.g. DNS -> SSL -> HTTP), not derived from category -- category groups
# tools by domain, not by which ones chain together in practice. Intentionally
# hand-picked rather than exhaustive: a tool with no obvious next step (e.g. a
# pure text converter with no natural chain) is simply absent, and
# render_related_tools() renders nothing for an absent slug rather than a
# forced, meaningless section.
TOOL_BUNDLES: dict[str, tuple[str, ...]] = {
    "domain_health": ("dns_records", "ssl_certificate", "whois_lookup"),
    "dns_records": ("domain_health", "whois_lookup", "dns_propagation"),
    "dns_propagation": ("dns_records", "domain_health"),
    "ssl_certificate": ("domain_health", "dns_records", "http_status"),
    "http_status": ("domain_health", "ssl_certificate", "uptime_trend", "security_headers"),
    "uptime_trend": ("http_status", "domain_health"),
    "security_headers": ("http_status", "ssl_certificate"),
    "cve_lookup": ("security_headers", "ssl_certificate"),
    "whois_lookup": ("dns_records", "domain_health", "ssl_certificate"),
    "bulk_domain_health": ("domain_health", "dns_records", "ssl_certificate"),
    "mac_address_tool": ("subnet_calculator", "cidr_aggregator", "ipv6_compressor"),
    "ip_geolocation": ("whois_lookup", "dns_records", "http_status"),
    "subnet_calculator": ("cidr_aggregator", "ipv6_compressor", "mac_address_tool", "cidr_overlap"),
    "cidr_aggregator": ("subnet_calculator", "ipv6_compressor", "cidr_overlap"),
    "ipv6_compressor": ("subnet_calculator", "cidr_aggregator"),
    "port_reference": ("subnet_calculator", "mac_address_tool"),
    "windows_event_reference": ("log_troubleshooting", "port_reference"),
    "email_header_analyzer": ("dns_records", "domain_health", "dkim_lookup"),
    "dkim_lookup": ("email_header_analyzer", "domain_health", "email_record_builder"),
    "email_record_builder": ("dkim_lookup", "dns_records"),
    "password_generator": ("hash_generator",),
    "hash_generator": ("password_generator", "jwt_decoder", "file_integrity"),
    "file_integrity": ("hash_generator", "cve_lookup"),
    "jwt_decoder": ("jwt_encoder", "hash_generator"),
    "jwt_encoder": ("jwt_decoder", "hash_generator"),
    "json_formatter": ("base64_tool", "regex_tester", "config_format_converter"),
    "config_format_converter": ("json_formatter", "text_diff_checker"),
    "base64_tool": ("json_formatter", "url_encoder_decoder"),
    "url_encoder_decoder": ("base64_tool", "json_formatter"),
    "regex_tester": ("text_diff_checker", "json_formatter", "regex_cheat_sheet"),
    "text_diff_checker": ("regex_tester", "case_converter"),
    "case_converter": ("text_diff_checker", "url_encoder_decoder"),
    "timestamp_converter": ("cron_explainer",),
    "cron_explainer": ("timestamp_converter", "log_troubleshooting", "cron_builder"),
    "cron_builder": ("cron_explainer", "timestamp_converter"),
    "log_troubleshooting": ("cron_explainer", "webhook_tester", "windows_event_reference"),
    "chmod_calculator": ("cron_explainer", "log_troubleshooting"),
    "webhook_tester": ("http_status", "log_troubleshooting"),
    "user_agent_parser": ("http_status", "email_header_analyzer"),
    "ulid_uuid_decoder": ("id_generator", "timestamp_converter"),
    "curl_builder": ("webhook_tester", "url_encoder_decoder"),
    "regex_cheat_sheet": ("regex_tester",),
}


def related_tools(slug: str) -> tuple[ToolMeta, ...]:
    """Return the curated "next tool" suggestions for a tool slug. Empty if none defined."""
    return tuple(_resolve_slugs(TOOL_BUNDLES.get(slug, ())))


def render_related_tools(slug: str) -> None:
    """Render a compact "Related tools" row of suggestions, if any are curated for ``slug``."""
    tools = related_tools(slug)
    if not tools:
        return
    st.markdown('<div class="related-tools-label">Related tools</div>', unsafe_allow_html=True)
    cols = st.columns(len(tools), gap="small")
    for col, tool in zip(cols, tools, strict=True):
        with col:
            _safe_page_link(tool.path, label=tool.short_title, icon=":material/arrow_forward:", stretch_width=True)


def apply_app_shell(active_page: str) -> None:
    """Apply global theme CSS and render the shared sidebar shell."""
    render_sidebar(active_page)
    _inject_global_css("dark")
    slug = TITLE_TO_SLUG.get(active_page)
    if slug is not None:
        record_recent_visit(slug)
    _sync_local_storage_mirror(active_page)
    render_command_palette()


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


def move_favorite(slug: str, offset: int) -> None:
    """Shift ``slug`` earlier (offset=-1) or later (offset=+1) in the favorites order.

    A no-op if ``slug`` isn't favorited or the move would go out of bounds
    (callers should disable the button in that case rather than rely on this).
    """
    stored = _get_persisted_slugs("fav")
    if slug not in stored:
        return
    index = stored.index(slug)
    target = index + offset
    if not 0 <= target < len(stored):
        return
    stored[index], stored[target] = stored[target], stored[index]
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


def render_command_palette() -> None:
    """Render a global Ctrl+K / Cmd+K command palette overlay.

    New UI pattern for this codebase (no existing modal/overlay precedent) --
    built the same way _sync_local_storage_mirror() reaches the top-level
    document: a same-origin sandboxed st.iframe whose script operates on
    window.top.document/window.top.location. Because a fresh iframe (and JS
    realm) is injected on every Streamlit rerun, but window.top.document
    persists across reruns, both the overlay DOM node and the keydown
    listener are created exactly once via a dedup guard
    (window.top.__itopsPaletteReady); every subsequent rerun just refreshes
    the tool list data on window.top.__itopsPaletteTools and returns.

    NOT verified in a real browser -- this sandboxed dev environment has no
    browser to visually confirm the overlay renders/filters/navigates
    correctly. Built by directly reading the installed Streamlit frontend
    bundle's iframe sandbox attributes and mirroring the one proven
    same-origin-iframe precedent in this file (_sync_local_storage_mirror
    above). Manually smoke-test after deploy.
    """
    entries = [{"title": tool.title, "description": tool.description, "href": _fallback_href(tool.path)} for tool in TOOLS]
    st.iframe(
        f"""
        <script>
        (function() {{
            var TOOLS = {json.dumps(entries)};
            window.top.__itopsPaletteTools = TOOLS;

            if (window.top.__itopsPaletteReady) {{
                return;
            }}
            window.top.__itopsPaletteReady = true;

            var doc = window.top.document;

            var overlay = doc.createElement("div");
            overlay.id = "itops-cmdk-overlay";
            overlay.style.cssText = "position:fixed;inset:0;z-index:99999;display:none;" +
                "background:rgba(10,12,16,0.6);align-items:flex-start;justify-content:center;padding-top:12vh;";

            var panel = doc.createElement("div");
            panel.style.cssText = "background:#12161c;border:1px solid rgba(255,255,255,0.14);border-radius:12px;" +
                "width:min(560px,90vw);max-height:60vh;overflow:hidden;display:flex;flex-direction:column;" +
                "box-shadow:0 20px 60px rgba(0,0,0,0.5);font-family:inherit;";

            var input = doc.createElement("input");
            input.type = "text";
            input.placeholder = "Search tools... (Esc to close)";
            input.style.cssText = "border:none;outline:none;padding:16px;font-size:16px;background:transparent;" +
                "color:#e8ecf1;border-bottom:1px solid rgba(255,255,255,0.1);width:100%;box-sizing:border-box;";

            var list = doc.createElement("div");
            list.style.cssText = "overflow-y:auto;padding:8px;";

            panel.appendChild(input);
            panel.appendChild(list);
            overlay.appendChild(panel);
            doc.body.appendChild(overlay);

            function navigateTo(href) {{
                window.top.location.href = href;
            }}

            function matchingTools(query) {{
                var needle = query.trim().toLowerCase();
                var tools = window.top.__itopsPaletteTools || [];
                return tools.filter(function(t) {{
                    return !needle ||
                        t.title.toLowerCase().indexOf(needle) !== -1 ||
                        t.description.toLowerCase().indexOf(needle) !== -1;
                }}).slice(0, 8);
            }}

            function renderResults(query) {{
                var matches = matchingTools(query);
                list.innerHTML = "";
                if (matches.length === 0) {{
                    var empty = doc.createElement("div");
                    empty.style.cssText = "padding:16px;color:#8b95a3;font-size:14px;";
                    empty.textContent = "No tools matched.";
                    list.appendChild(empty);
                    return;
                }}
                matches.forEach(function(tool, index) {{
                    var row = doc.createElement("div");
                    row.style.cssText = "padding:10px 12px;border-radius:8px;cursor:pointer;" +
                        (index === 0 ? "background:rgba(255,255,255,0.08);" : "");
                    var title = doc.createElement("div");
                    title.style.cssText = "color:#e8ecf1;font-size:14px;font-weight:600;";
                    title.textContent = tool.title;
                    var desc = doc.createElement("div");
                    desc.style.cssText = "color:#8b95a3;font-size:12px;margin-top:2px;";
                    desc.textContent = tool.description;
                    row.appendChild(title);
                    row.appendChild(desc);
                    row.addEventListener("mouseenter", function() {{
                        Array.prototype.forEach.call(list.children, function(child) {{ child.style.background = ""; }});
                        row.style.background = "rgba(255,255,255,0.08)";
                    }});
                    row.addEventListener("click", function() {{ navigateTo(tool.href); }});
                    list.appendChild(row);
                }});
            }}

            function openPalette() {{
                overlay.style.display = "flex";
                input.value = "";
                renderResults("");
                setTimeout(function() {{ input.focus(); }}, 0);
            }}

            function closePalette() {{
                overlay.style.display = "none";
                input.value = "";
            }}

            input.addEventListener("input", function() {{ renderResults(input.value); }});

            input.addEventListener("keydown", function(evt) {{
                if (evt.key === "Escape") {{
                    evt.preventDefault();
                    closePalette();
                }} else if (evt.key === "Enter") {{
                    evt.preventDefault();
                    var matches = matchingTools(input.value);
                    if (matches.length > 0) {{
                        navigateTo(matches[0].href);
                    }}
                }}
            }});

            overlay.addEventListener("click", function(evt) {{
                if (evt.target === overlay) {{
                    closePalette();
                }}
            }});

            doc.addEventListener("keydown", function(evt) {{
                var isMac = navigator.platform.toUpperCase().indexOf("MAC") !== -1;
                var modifierPressed = isMac ? evt.metaKey : evt.ctrlKey;
                if (modifierPressed && evt.key.toLowerCase() === "k") {{
                    evt.preventDefault();
                    if (overlay.style.display === "flex") {{
                        closePalette();
                    }} else {{
                        openPalette();
                    }}
                }}
            }});
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
    show_reorder: bool = False,
) -> None:
    """Render a home page tool card grid.

    ``heading`` overrides the default label ("Matching Tools" when ``query``
    is set, otherwise "Popular Tools") -- used for e.g. the personalized
    "Recently Used" row. ``section_id`` sets the heading div's HTML id; pass
    None when rendering more than one section on the same page so IDs stay
    unique. ``key_prefix`` must also be unique per section on a page since
    the same tool can appear in more than one grid (e.g. recents + all
    tools) and Streamlit container keys must be unique. ``show_reorder``
    adds move-earlier/move-later buttons -- pass True only for the
    visitor's own Favorites grid, never for a read-only grid like Shared
    Favorites or Recently Used.
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
        render_status_note(
            "No matching tools",
            "Try different keywords, clear filters, or switch to Quick access to browse curated tools.",
            tone="neutral",
        )
        return

    favorite_slugs = set(_get_persisted_slugs("fav"))
    cols = st.columns(min(len(tools), 5), gap="large")
    for index, tool in enumerate(tools):
        with cols[index % len(cols)]:
            with st.container(key=f"tool_card_{key_prefix}_{tool.slug}"):
                delay_ms = min(index, 9) * 45
                st.markdown(_tool_card_html(tool, delay_ms=delay_ms), unsafe_allow_html=True)
                if show_reorder:
                    back_col, link_col, fwd_col, fav_col = st.columns([1, 4, 1, 1])
                    with back_col:
                        if st.button(
                            "",
                            icon=":material/arrow_back:",
                            key=f"fav_move_back_{key_prefix}_{tool.slug}",
                            help="Move earlier",
                            disabled=index == 0,
                        ):
                            move_favorite(tool.slug, -1)
                            st.rerun()
                    with fwd_col:
                        if st.button(
                            "",
                            icon=":material/arrow_forward_ios:",
                            key=f"fav_move_fwd_{key_prefix}_{tool.slug}",
                            help="Move later",
                            disabled=index == len(tools) - 1,
                        ):
                            move_favorite(tool.slug, 1)
                            st.rerun()
                else:
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
        <div class="important-notice" role="note" aria-label="Public-safe usage notice">
            <div class="notice-icon" aria-hidden="true">i</div>
            <div><strong>Important Notice</strong><p>Do not paste passwords, private keys, tokens, or any sensitive customer data. This toolkit is for educational and troubleshooting purposes only.</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(
    title: str,
    description: str,
    warning: str | None = None,
    illustration: str | None = None,
) -> None:
    """Render a compact page header for tool pages."""
    tool = tool_by_title(title)
    icon = tool.icon if tool else "IT"
    accent = tool.accent if tool else "#1668f4"
    overline = f"{tool.category} Tool" if tool else "Tool"
    icon_text = _icon_text_color(accent)
    illustration_path = (
        TOOL_HEADER_ILLUSTRATION_BY_CATEGORY.get(illustration, illustration)
        if illustration
        else (TOOL_HEADER_ILLUSTRATION_BY_CATEGORY.get(tool.category) if tool else None)
    )
    illustration_html = (
        _svg_img_html(
            illustration_path,
            f"{tool.category if tool else 'Tool'} illustration",
            "tool-page-header-illustration-image",
            decorative=True,
        )
        if illustration_path
        else None
    )
    layout_class = " tool-page-header-with-illustration" if illustration_html else ""
    header_id = f"tool-page-title-{_key_slug(title)}"
    illustration_slot = (
        f'<div class="tool-page-header-illustration" aria-hidden="true">{illustration_html}</div>'
        if illustration_html
        else ""
    )
    st.markdown(
        f"""
        <section class="tool-page-header{layout_class}" style="--tool-accent: {accent}; --tool-icon-text: {icon_text};" aria-labelledby="{header_id}">
            <div class="tool-page-header-main">
                <div class="tool-page-icon">{escape(icon)}</div>
                <div>
                    <p class="tool-page-overline">{escape(overline)}</p>
                    <h1 id="{header_id}">{escape(title)}</h1>
                    <p>{escape(description)}</p>
                </div>
            </div>
            {illustration_slot}
        </section>
        """,
        unsafe_allow_html=True,
    )
    if warning:
        st.warning(warning)


def tool_form_panel(key: str):
    return st.container(key=f"tool_form_panel_{_key_slug(key)}")


@contextmanager
def tool_result_panel(key: str, related_to: str | None = None):
    """Result panel container. Pass ``related_to=<tool slug>`` to append a curated
    "Related tools" row after the panel's own content, if any bundle is defined."""
    with st.container(key=f"tool_result_panel_{_key_slug(key)}"):
        yield
        if related_to:
            render_related_tools(related_to)


@contextmanager
def tool_download_panel(key: str, related_to: str | None = None):
    """Download panel container. Accepts ``related_to`` the same way tool_result_panel does."""
    with st.container(key=f"tool_download_panel_{_key_slug(key)}"):
        yield
        if related_to:
            render_related_tools(related_to)


def display_rows_frame(rows: Iterable[dict[str, Any]]) -> pd.DataFrame:
    """Build a Streamlit-safe dataframe for mixed-value display rows.

    Convention across this app's pages: static reference pages use st.table
    (fixed content, no need for the sort/resize/scroll affordances); pages
    showing results from a live lookup use st.dataframe (usually via this
    helper), since those can be wider or more variable in row count.
    """
    return pd.DataFrame(
        {key: str(value) for key, value in row.items()}
        for row in rows
    )


def render_form_intro(title: str, description: str) -> None:
    intro_id = f"tool-form-intro-{_key_slug(title)}"
    st.markdown(
        f"""
        <div class="tool-form-intro" role="group" aria-labelledby="{intro_id}">
            <div class="tool-panel-eyebrow">Input</div>
            <h2 id="{intro_id}">{escape(title)}</h2>
            <p>{escape(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_control_heading(label: str) -> None:
    st.markdown(f'<div class="tool-panel-eyebrow">{escape(label)}</div>', unsafe_allow_html=True)


def render_section_heading(
    title: str,
    description: str | None = None,
    eyebrow: str = "Results",
    heading_level: str = "h2",
) -> None:
    # description_html sits on the same line as </h2> above, not alone on its
    # own line, because when it's "" (no description) a whitespace-only line
    # there is a blank line per CommonMark -- which ends this raw HTML block
    # early and drops everything after it to a literal-text code block
    # instead of rendering as HTML. See _tool_card_html for the same fix.
    description_html = f"<p>{escape(description)}</p>" if description else ""
    heading_tag = "h3" if heading_level == "h3" else "h2"
    heading_class = f"tool-section-heading-level-{heading_tag}"
    heading_level_value = "3" if heading_tag == "h3" else "2"
    st.markdown(
        f"""
        <div class="tool-section-heading {heading_class}" data-heading-level="{heading_level_value}">
            <div class="tool-panel-eyebrow">{escape(eyebrow)}</div>
            <{heading_tag}>{escape(title)}</{heading_tag}>{description_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(title: str, description: str, illustration: str | None = None) -> None:
    asset = EMPTY_STATE_ILLUSTRATIONS.get(illustration or "")
    illustration_html = (
        _svg_img_html(asset, "Empty state illustration", "tool-empty-illustration-image", decorative=True)
        if asset
        else None
    )
    illustration_slot = (
        f'<div class="tool-empty-illustration" aria-hidden="true">{illustration_html}</div>'
        if illustration_html
        else ""
    )
    st.markdown(
        f"""
        <div class="tool-empty-state" role="status" aria-live="polite" aria-label="{escape(title)}">
            <div class="tool-empty-mark">IT</div>
            {illustration_slot}
            <div>
                <strong>{escape(title)}</strong>
                <p>{escape(description)}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def run_validated_lookup(
    key: str,
    validate: Callable[[], str | None],
    call: Callable[[], Any],
    spinner_text: str = "Working...",
) -> None:
    """Validate, then run a live-lookup ``call`` under a spinner, storing the
    outcome in ``st.session_state``.

    Call this inside ``if submitted:`` right after a form's submit flag
    resolves. Rendering must read the result back from
    ``st.session_state[f"{key}_result"]`` / ``st.session_state[f"{key}_validation_error"]``
    (not off the transient submit flag), since the sidebar's quick-search box,
    favorite-star buttons, and any other widget outside the page's st.form
    trigger reruns of their own -- on those reruns the submit flag is False
    again, which would otherwise collapse the whole results section.

    ``validate`` returns an error message, or ``None`` if the input is valid.
    ``call`` performs the actual (usually network-bound) lookup and is only
    invoked -- under ``st.spinner(spinner_text)`` -- when validation passes.
    """
    error = validate()
    if error is not None:
        st.session_state[f"{key}_validation_error"] = error
        st.session_state[f"{key}_result"] = None
        return
    st.session_state[f"{key}_validation_error"] = None
    with st.spinner(spinner_text):
        st.session_state[f"{key}_result"] = call()


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
    role = "alert" if normalized_tone == "warning" else "status"
    aria_live = "assertive" if normalized_tone == "warning" else "polite"
    aria_label = f"{normalized_tone.capitalize()} status: {title}"
    st.markdown(
        f"""
        <div class="tool-status-note tool-status-note-{normalized_tone}" role="{role}" aria-live="{aria_live}" aria-atomic="true" aria-label="{escape(aria_label)}" tabindex="0">
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
            or any(value in alias.lower() for alias in tool.aliases)
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


def recent_tool_slugs() -> tuple[str, ...]:
    """Return persisted recent-tool slugs (already deduped and capped)."""
    return tuple(_get_persisted_slugs("recent"))


def favorites_share_link(tools: Iterable[ToolMeta]) -> str:
    """Build an absolute, read-only link that opens someone else's favorites as a shared list."""
    slugs = ",".join(tool.slug for tool in tools)
    query = urlencode({SHARED_FAVORITES_PARAM: slugs})
    return f"{app_base_url()}/?{query}"


def shared_favorite_tools() -> tuple[ToolMeta, ...]:
    """Return the tools named by a visited ``shared_fav`` link, in order. Read-only, view-only."""
    raw = st.query_params.get(SHARED_FAVORITES_PARAM, "")
    return tuple(_resolve_slugs(slug for slug in raw.split(",") if slug))


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
    new_badge = '<span class="tool-card-badge-new">NEW</span>' if tool.is_new else ""
    return f"""
    <div class="tool-card-shell" style="--tool-accent: {tool.accent}; animation-delay: {delay_ms}ms;">
        {new_badge}
        <div class="tool-card-icon">{escape(tool.icon)}</div>
        <h3>{escape(tool.title)}</h3>
        <p>{escape(tool.description)}</p>
    </div>
    """


def _hero_visual_html() -> str:
    generated_hero = _svg_img_html(
        HOME_HERO_ILLUSTRATION,
        "ITOps dashboard hero illustration",
        "hero-visual-image",
        decorative=True,
    )
    if generated_hero:
        return f'<div class="hero-visual hero-visual-generated" aria-hidden="true">{generated_hero}</div>'
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


def roadmap_badge_icon_html(icon_key: str, fallback: str) -> str:
    icon_path = ROADMAP_BADGE_ICONS.get(icon_key)
    icon_html = _svg_img_html(icon_path, "", "roadmap-badge-icon-image", decorative=True) if icon_path else None
    if icon_html:
        return f'<span class="roadmap-badge-icon" aria-hidden="true">{icon_html}</span>'
    return f'<span class="roadmap-badge-icon roadmap-badge-icon-fallback" aria-hidden="true">{escape(fallback)}</span>'


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
        "cidr_aggregator": ":material/merge_type:",
        "user_agent_parser": ":material/devices:",
        "ipv6_compressor": ":material/compress:",
        "case_converter": ":material/text_fields:",
        "color_converter": ":material/palette:",
        "whois_lookup": ":material/badge:",
        "bulk_domain_health": ":material/upload_file:",
        "webhook_tester": ":material/webhook:",
        "uptime_trend": ":material/show_chart:",
        "security_headers": ":material/shield:",
        "cve_lookup": ":material/bug_report:",
        "dns_propagation": ":material/travel_explore:",
        "windows_event_reference": ":material/event_note:",
        "dkim_lookup": ":material/key:",
        "email_record_builder": ":material/build:",
        "windows_error_reference": ":material/error_outline:",
        "config_format_converter": ":material/sync_alt:",
        "m365_sku_decoder": ":material/badge:",
        "id_generator": ":material/fingerprint:",
        "json_diff": ":material/compare_arrows:",
        "ip_geolocation": ":material/location_on:",
        "file_integrity": ":material/verified:",
    }
    return icons.get(slug, ":material/build:")


def _key_slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_")


# Matches the shared palette reused across cloudscope, odysseus, and
# hermes-workspace. This app ships dark-only -- a Light palette existed
# behind a toggle but Streamlit's native widget chrome (buttons, selects,
# sliders, alerts) is read once from .streamlit/config.toml at server
# start and never followed the in-app toggle, so "Light mode" never
# looked fully correct and was dropped rather than fixed.
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
    },
}


def _inject_global_css(mode: str) -> None:
    # NOTE: the CSS below is a plain (non f-string) template with a single
    # literal placeholder substituted via str.replace(). It is deliberately
    # NOT an f-string/`.format()` call, since the block contains thousands of
    # literal `{`/`}` CSS rule braces that would otherwise need escaping.
    tokens = _THEME_TOKENS[mode]
    root_vars = "\n            ".join(f"--itops-{name}: {value};" for name, value in tokens.items())
    css = """
        <style>

        :root {
            __ITOPS_ROOT_VARS__
            --card-radius: 8px;
            --shell-gap-xs: 0.45rem;
            --shell-gap-sm: 0.7rem;
            --shell-gap-md: 1rem;
            --shell-gap-lg: 1.4rem;
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }
        }

        /* Nothing in this stylesheet suppresses the browser's default focus
           ring, but several links (fallback-page-link, roadmap-submit-link,
           roadmap-secondary-link) sit on colored/gradient backgrounds where a
           default outline can be low-contrast. This gives every link and
           button in the app a consistent, visible keyboard-focus outline. */
        .stApp a:focus-visible,
        .stApp button:focus-visible {
            outline: 2px solid var(--itops-blue);
            outline-offset: 2px;
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
            transition: background-color 220ms ease, color 220ms ease, background-image 260ms ease;
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
            border-radius: var(--card-radius) !important;
            color: #ffffff !important;
            background: linear-gradient(135deg, var(--itops-blue), var(--itops-blue-dark)) !important;
            box-shadow: 0 12px 26px color-mix(in srgb, var(--itops-blue) 26%, transparent) !important;
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
            transition: background-color 220ms ease, background-image 260ms ease, border-color 220ms ease;
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
            border-radius: var(--card-radius) !important;
        }

        [data-testid="stSkeleton"],
        [data-testid="stSkeleton"] > div,
        [class*="Skeleton"] {
            border-radius: var(--card-radius) !important;
            background-color: var(--itops-surface-strong) !important;
            background-image: linear-gradient(
                90deg,
                var(--itops-surface-strong) 0%,
                var(--itops-surface) 50%,
                var(--itops-surface-strong) 100%
            ) !important;
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
            /* Deliberately its own shape/palette, not var(--card-radius) or a
               theme token -- this is the sidebar's static brand logo tile,
               which (like the rest of the sidebar chrome) stays fixed
               regardless of theme, distinct from the app's content cards. */
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
            margin: 0.9rem 0 0.45rem;
            letter-spacing: 0.04em;
        }

        [data-testid="stSidebar"] [data-testid="stTextInputRootElement"] {
            border-radius: var(--card-radius);
            border: 1px solid rgba(152, 190, 245, 0.24);
            background: rgba(255, 255, 255, 0.06);
        }

        [data-testid="stSidebar"] [data-testid="stTextInputRootElement"]:focus-within {
            border-color: rgba(173, 205, 255, 0.58);
            box-shadow: 0 0 0 3px rgba(18, 107, 255, 0.18);
        }

        [data-testid="stSidebar"] [data-testid="stTextInputRootElement"] input {
            color: #edf5ff !important;
        }

        [data-testid="stSidebar"] .stExpander {
            border: 1px solid rgba(152, 190, 245, 0.16);
            border-radius: var(--card-radius);
            background: rgba(255, 255, 255, 0.03);
            margin: 0 0 0.55rem;
        }

        [data-testid="stSidebar"] .stExpander [data-testid="stExpanderToggleIcon"] svg {
            opacity: 0.88;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a {
            border-radius: var(--card-radius);
            color: #dceaff !important;
            min-height: 2.65rem;
            padding: 0.58rem 0.68rem;
            font-weight: 650;
            background: transparent;
            border: 1px solid transparent;
            line-height: 1.28;
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
            background: linear-gradient(135deg, var(--itops-blue) 0%, var(--itops-blue-dark) 100%);
            box-shadow: 0 12px 24px color-mix(in srgb, var(--itops-blue) 28%, transparent);
            color: #ffffff !important;
        }

        .fallback-page-link {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 2.35rem;
            border-radius: var(--card-radius);
            padding: 0.65rem 0.8rem;
            color: #ffffff !important;
            text-decoration: none !important;
            font-weight: 800;
            background: linear-gradient(135deg, var(--itops-blue), var(--itops-blue-dark));
        }

        [data-testid="stSidebar"] .fallback-page-link {
            justify-content: flex-start;
            min-height: 2.85rem;
            background: transparent;
            color: #edf5ff !important;
            font-weight: 650;
        }

        .sidebar-info-card {
            border-radius: var(--card-radius);
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
            border-radius: var(--card-radius);
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

        [data-testid="stPills"] [role="radiogroup"] {
            gap: 0.45rem;
        }

        [data-testid="stPills"] [role="radio"] {
            min-height: 2.35rem;
            border-radius: var(--card-radius);
            font-weight: 750;
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
            border-radius: var(--card-radius);
            color: var(--itops-ink);
            font-size: 0.92rem;
            font-weight: 700;
            background: var(--itops-surface);
            border: 1px solid var(--itops-surface-border);
            box-shadow: 0 8px 24px rgba(43, 88, 150, 0.06);
        }

        /* .hero-visual and everything nested inside it (.laptop-*, .dot-grid,
           .chart-line, .hero-shield, .hero-globe, .server-stack, etc.) is a
           static decorative illustration. Its hardcoded blues/whites are an
           intentional fixed brand graphic, not a missed var(--itops-*) token
           -- same "fixed, not a token" rationale as the AI-badge spots
           elsewhere in this file, just not previously called out here. */
        .hero-visual {
            position: relative;
            min-height: 330px;
            overflow: hidden;
            border-radius: var(--card-radius);
            background:
                radial-gradient(circle at 52% 38%, rgba(18, 107, 255, 0.15), transparent 32%),
                linear-gradient(135deg, rgba(255, 255, 255, 0.35), rgba(235, 243, 255, 0.12));
        }

        .hero-visual-generated {
            display: grid;
            place-items: center;
            padding: 0.35rem;
            background: var(--itops-surface);
            border: 1px solid var(--itops-surface-border);
        }

        .hero-visual-generated::before,
        .hero-visual-generated::after {
            display: none;
        }

        .hero-visual-image {
            width: 100%;
            height: auto;
            display: block;
            border-radius: var(--card-radius);
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
            border-radius: var(--card-radius);
        }

        .hero-visual::after {
            width: 230px;
            height: 150px;
            right: 58px;
            bottom: 28px;
            border-radius: var(--card-radius);
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
            border-radius: var(--card-radius);
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
            margin: 1.95rem 0 1.05rem;
            padding-top: 1.1rem;
            border-top: 1px solid var(--itops-line);
        }

        .section-heading > div {
            display: inline-flex;
            gap: 0.8rem;
            align-items: center;
        }

        .section-heading h2 {
            margin: 0;
            font-size: clamp(1.28rem, 2.2vw, 1.55rem);
            font-weight: 800;
            line-height: 1.14;
        }

        .section-bolt {
            color: var(--itops-blue);
            font-weight: 900;
        }

        [class*="st-key-tool_card_"] {
            height: 100%;
            border-radius: var(--card-radius);
            padding: 1.05rem;
            background: var(--itops-surface);
            border: 1px solid var(--itops-surface-border);
            box-shadow: 0 12px 32px rgba(36, 79, 135, 0.06);
            position: relative;
        }

        [class*="st-key-tool_card_"]::before {
            content: "";
            position: absolute;
            inset: 0 0 auto;
            height: 3px;
            border-radius: var(--card-radius) var(--card-radius) 0 0;
            background: linear-gradient(90deg, var(--itops-blue), color-mix(in srgb, var(--itops-blue), #ffffff 14%));
            opacity: 0.72;
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
            border-radius: var(--card-radius);
            margin-bottom: 1rem;
            /* Not always white -- several accents fail WCAG AA with white
               icon text, see _icon_text_color() in utils/ui.py. */
            color: var(--tool-icon-text, #ffffff);
            font-size: 0.84rem;
            font-weight: 900;
            background: linear-gradient(145deg, color-mix(in srgb, var(--tool-accent), #ffffff 8%), var(--tool-accent));
            box-shadow: 0 14px 24px color-mix(in srgb, var(--tool-accent), transparent 75%);
        }

        .tool-card-icon-image {
            width: 1.5rem;
            height: 1.5rem;
            display: block;
        }

        .tool-card-shell h3 {
            margin: 0.18rem 0 0.58rem;
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

        .tool-card-category {
            margin: 0;
            color: var(--itops-blue);
            font-size: 0.7rem;
            font-weight: 900;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            line-height: 1.2;
        }

        [class*="st-key-tool_card_"] [data-testid="stPageLink"] a {
            border-radius: var(--card-radius);
            justify-content: center;
            color: #ffffff !important;
            font-weight: 800;
            background: linear-gradient(135deg, var(--itops-blue), var(--itops-blue-dark));
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
            border-radius: var(--card-radius);
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
            border-radius: var(--card-radius);
            font-size: 0.74rem;
            font-weight: 900;
            border: 2px solid currentColor;
            background: #ffffff;
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
            border-radius: var(--card-radius);
            border: 1px solid color-mix(in srgb, var(--itops-orange), transparent 30%);
            background: linear-gradient(135deg, color-mix(in srgb, var(--itops-orange), transparent 87%), var(--itops-surface));
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
            background: var(--itops-orange);
            /* White text measured 1.95:1 against --itops-orange -- below
               WCAG AA's 4.5:1. Dark ink clears it (9.75:1). */
            color: #0c1116;
            font-weight: 900;
        }

        .tool-page-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
            border-radius: var(--card-radius);
            border: 1px solid var(--itops-surface-border);
            background: var(--itops-surface);
            box-shadow: 0 12px 32px rgba(36, 79, 135, 0.05);
        }

        .tool-page-header-main {
            display: flex;
            align-items: center;
            gap: var(--shell-gap-md);
            min-width: 0;
        }

        .tool-page-header-with-illustration {
            justify-content: space-between;
        }

        .tool-page-icon {
            width: 3.15rem;
            height: 3.15rem;
            display: grid;
            place-items: center;
            border-radius: var(--card-radius);
            background: linear-gradient(145deg, color-mix(in srgb, var(--tool-accent), #ffffff 8%), var(--tool-accent));
            /* Not always white -- several accents fail WCAG AA with white
               icon text, see _icon_text_color() in utils/ui.py. */
            color: var(--tool-icon-text, #ffffff);
            font-weight: 900;
            font-size: 0.76rem;
        }

        .tool-page-header-illustration {
            width: min(26vw, 260px);
            flex: 0 0 min(26vw, 260px);
        }

        .tool-page-header-illustration-image {
            width: 100%;
            height: auto;
            display: block;
            border-radius: var(--card-radius);
            border: 1px solid var(--itops-surface-border);
            background: var(--itops-surface);
        }

        .tool-page-header h1 {
            margin: 0;
            font-size: clamp(1.55rem, 3vw, 2.25rem);
            line-height: 1.05;
            font-weight: 800;
        }

        .tool-page-overline {
            margin: 0 0 var(--shell-gap-xs);
            color: var(--itops-blue);
            font-size: 0.72rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            line-height: 1;
        }

        .tool-page-header p {
            margin: 0.35rem 0 0;
            color: var(--itops-text-secondary);
            line-height: 1.5;
        }

        [class*="st-key-tool_form_panel_"],
        [class*="st-key-tool_result_panel_"] {
            border: 1px solid var(--itops-surface-border);
            border-radius: var(--card-radius);
            background: var(--itops-surface);
            box-shadow: 0 12px 32px rgba(36, 79, 135, 0.045);
            padding: 1.05rem 1.05rem 1.15rem;
            margin: 1.1rem 0;
        }

        [class*="st-key-tool_form_panel_"] {
            background:
                linear-gradient(135deg, var(--itops-surface), color-mix(in srgb, var(--itops-surface), var(--itops-blue) 6%));
        }

        .tool-form-intro,
        .tool-section-heading {
            margin-bottom: 0.95rem;
            padding-bottom: 0.72rem;
            border-bottom: 1px solid color-mix(in srgb, var(--itops-line), transparent 48%);
        }

        .tool-form-intro h2,
        .tool-section-heading h2 {
            margin: 0.15rem 0 0.25rem;
            color: var(--itops-ink);
            font-size: clamp(1.05rem, 1.7vw, 1.35rem);
            font-weight: 800;
            line-height: 1.2;
        }

        .tool-section-heading h3 {
            margin: 0.15rem 0 0.22rem;
            color: var(--itops-ink);
            font-size: clamp(0.98rem, 1.45vw, 1.18rem);
            font-weight: 760;
            line-height: 1.24;
        }

        .tool-section-heading[data-heading-level="3"] {
            margin-top: 0.15rem;
            padding-left: 0.2rem;
            border-left: 2px solid color-mix(in srgb, var(--itops-blue), transparent 72%);
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
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .related-tools-label {
            color: var(--itops-muted);
            font-size: 0.72rem;
            font-weight: 900;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin: 1.4rem 0 0.5rem;
        }

        .tool-empty-state {
            display: flex;
            gap: 0.9rem;
            align-items: center;
            border: 1px dashed var(--itops-surface-border);
            border-radius: var(--card-radius);
            background: var(--itops-surface);
            padding: 0.95rem 1rem;
            margin: 1rem 0;
        }

        .tool-empty-illustration {
            width: 3.25rem;
            height: 2.45rem;
            flex: 0 0 3.25rem;
            border-radius: var(--card-radius);
            overflow: hidden;
            border: 1px solid var(--itops-surface-border);
            background: var(--itops-surface);
        }

        .tool-empty-illustration-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }

        .tool-empty-mark {
            width: 2.45rem;
            height: 2.45rem;
            flex: 0 0 2.45rem;
            display: grid;
            place-items: center;
            border-radius: var(--card-radius);
            color: #ffffff;
            font-size: 0.72rem;
            font-weight: 900;
            background: linear-gradient(145deg, var(--itops-blue), color-mix(in srgb, var(--itops-blue-dark), white 2%));
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
            border: 1px solid color-mix(in srgb, var(--itops-green), transparent 72%);
            border-radius: var(--card-radius);
            background: color-mix(in srgb, var(--itops-green), transparent 92%);
            padding: 0.85rem 1rem;
            margin: 0.8rem 0;
        }

        .tool-status-note {
            display: flex;
            gap: 0.85rem;
            align-items: flex-start;
            border-radius: var(--card-radius);
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
            border-radius: var(--card-radius);
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

        /* Every .tool-status-note-{tone} pairs a themed note background
           (var(--itops-*), so it stays correct across the palette) with a
           .tool-status-mark icon gradient using its own fixed, richer vivid
           hex stops for a glossy-icon look -- not the flatter token colors.
           The ai/info variant is the one exception that must stay fixed
           end-to-end: var(--itops-blue) is the theme accent (coral/red in
           dark mode, matching odysseus), not a literal blue, and using it
           here would both look wrong for an "info" note and clash with the
           icon's hardcoded blue gradient. Mirrored in .roadmap-notice-*
           below -- keep both in sync if this changes. */
        .tool-status-note-ai,
        .tool-status-note-info {
            border-color: rgba(18, 107, 255, 0.22);
            background: color-mix(in srgb, var(--itops-surface), #126bff 12%);
        }

        .tool-status-note-ai .tool-status-mark,
        .tool-status-note-info .tool-status-mark {
            /* #278aff measured 3.41:1 against white icon text -- below WCAG
               AA's 4.5:1. Darkened to #2174d6 (4.63:1), same hue; the other
               stop (#0f67f2, 4.95:1) already cleared. */
            background: linear-gradient(145deg, #2174d6, #0f67f2);
        }

        .tool-status-note-success {
            border-color: color-mix(in srgb, var(--itops-green), transparent 76%);
            background: color-mix(in srgb, var(--itops-surface), var(--itops-green) 12%);
        }

        .tool-status-note-success .tool-status-mark {
            /* White text measured 1.87:1/3.09:1 against these two stops --
               below WCAG AA's 4.5:1. Dark ink clears both (10.16:1/6.15:1). */
            color: #0c1116;
            background: linear-gradient(145deg, #30d968, #19a946);
        }

        .tool-status-note-warning {
            border-color: color-mix(in srgb, var(--itops-orange), transparent 75%);
            background: color-mix(in srgb, var(--itops-surface), var(--itops-orange) 12%);
        }

        .tool-status-note-warning .tool-status-mark {
            /* White text measured 2.35:1/2.87:1 against these two stops --
               below WCAG AA's 4.5:1. Dark ink clears both (8.09:1/6.61:1). */
            color: #0c1116;
            background: linear-gradient(145deg, #ff8a3d, #ff6a13);
        }

        .tool-status-note-neutral {
            border-color: var(--itops-surface-border);
            background: var(--itops-surface);
        }

        .tool-status-note-neutral .tool-status-mark {
            /* No neutral theme token exists -- this is its own fixed
               gray-blue, not derived from any var(--itops-*) accent. */
            background: #7a8da8;
        }

        [class*="st-key-tool_download_panel_"] {
            border: 1px solid var(--itops-surface-border);
            border-radius: var(--card-radius);
            background: var(--itops-surface);
            padding: 1rem;
            margin-top: 1rem;
        }

        div[data-testid="stAlert"] {
            border-radius: var(--card-radius);
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
            border-radius: var(--card-radius);
            padding: 0 1rem;
            text-decoration: none !important;
            font-size: 0.88rem;
            font-weight: 900;
            white-space: nowrap;
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease, background 160ms ease;
        }

        .roadmap-submit-link {
            color: #ffffff !important;
            background: linear-gradient(135deg, var(--itops-blue), var(--itops-blue-dark));
            box-shadow: 0 12px 24px color-mix(in srgb, var(--itops-blue) 20%, transparent);
        }

        .roadmap-submit-link:hover,
        .roadmap-footer-note a:hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 28px color-mix(in srgb, var(--itops-blue) 24%, transparent);
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
            border-radius: var(--card-radius);
            background: var(--itops-surface);
        }

        .roadmap-notice-mark {
            width: 2rem;
            height: 2rem;
            display: grid;
            place-items: center;
            border-radius: var(--card-radius);
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
            border-color: color-mix(in srgb, var(--itops-orange), transparent 72%);
            background: color-mix(in srgb, var(--itops-surface), var(--itops-orange) 12%);
        }

        .roadmap-notice-warning .roadmap-notice-mark {
            /* See .tool-status-note-warning .tool-status-mark -- same fix. */
            color: #0c1116;
            background: linear-gradient(145deg, #ff8a3d, #ff6a13);
        }

        .roadmap-notice-ai {
            border-color: rgba(18, 107, 255, 0.24);
            /* Fixed blue, not var(--itops-blue) -- see .tool-status-note-ai. */
            background: color-mix(in srgb, var(--itops-surface), #126bff 12%);
        }

        .roadmap-notice-ai .roadmap-notice-mark {
            /* See .tool-status-note-ai .tool-status-mark -- same fix. */
            background: linear-gradient(145deg, #2174d6, #0f67f2);
        }

        .roadmap-notice-neutral {
            margin: 0.85rem 0 0.9rem;
            border-color: var(--itops-surface-border);
            background: var(--itops-surface);
        }

        .roadmap-notice-neutral .roadmap-notice-mark {
            /* No neutral theme token exists -- see .tool-status-note-neutral. */
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
            border-radius: var(--card-radius);
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
            /* #667790 measured 3.07:1 against the dark bg -- below WCAG AA's
               4.5:1 minimum for normal text. --itops-muted (4.59:1) clears it. */
            color: var(--itops-muted);
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
            border-radius: var(--card-radius);
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
            border-bottom: 1px solid var(--itops-surface-border);
            background: var(--itops-surface-strong);
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
            /* #667790 measured 3.07:1 against the dark bg -- below WCAG AA's
               4.5:1 minimum for normal text. --itops-muted (4.59:1) clears it. */
            color: var(--itops-muted);
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
            scrollbar-color: var(--itops-surface-border) transparent;
        }

        .roadmap-column-list::-webkit-scrollbar {
            width: 0.45rem;
        }

        .roadmap-column-list::-webkit-scrollbar-thumb {
            border-radius: 999px;
            background: var(--itops-surface-border);
        }

        .roadmap-item-card {
            display: grid;
            grid-template-columns: 2.35rem minmax(0, 1fr);
            gap: 0.72rem;
            align-items: start;
            padding: 0.85rem 0 0.85rem 0.6rem;
            border-bottom: 1px solid var(--itops-surface-border);
            border-left: 3px solid transparent;
        }

        .roadmap-item-card:last-child {
            border-bottom: 0;
        }

        /* Matches the column-header status-dot colors just above, so each
           card carries the same status accent as the column it sits in. */
        .roadmap-item-planned { border-left-color: #2e8bff; }
        .roadmap-item-progress { border-left-color: #8a61f2; }
        .roadmap-item-done { border-left-color: #22ba4f; }
        .roadmap-item-ai { border-left-color: #11aab8; }

        .roadmap-vote-pill {
            width: 2.35rem;
            min-height: 2.5rem;
            align-self: start;
            border: 1px solid var(--itops-surface-border);
            border-radius: var(--card-radius);
            display: grid;
            place-items: center;
            align-content: center;
            /* #3d4f68 measured 1.68:1 against the dark bg -- far below WCAG AA's
               4.5:1 minimum for normal text. --itops-muted (4.59:1) clears it. */
            color: var(--itops-muted);
            background: var(--itops-surface);
            font-size: 0.75rem;
            font-weight: 850;
            line-height: 1.1;
        }

        .roadmap-vote-pill span {
            /* #667790 measured 3.07:1 against the dark bg -- below WCAG AA's
               4.5:1 minimum for normal text. --itops-muted (4.59:1) clears it. */
            color: var(--itops-muted);
            font-weight: 900;
        }

        .roadmap-item-body {
            min-width: 0;
        }

        .roadmap-card-title {
            margin: 0;
            padding: 0 !important;
            color: var(--itops-ink);
            font-size: 0.95rem;
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
            gap: 0.26rem;
            min-height: 1.25rem;
            border-radius: var(--card-radius);
            padding: 0 0.45rem;
            /* #667790 measured 3.07:1 against the dark bg -- below WCAG AA's
               4.5:1 minimum for normal text. --itops-muted (4.59:1) clears it. */
            color: var(--itops-muted);
            font-size: 0.68rem;
            line-height: 1.2;
            font-weight: 900;
            text-transform: uppercase;
        }

        .roadmap-badge-icon {
            width: 0.82rem;
            height: 0.82rem;
            display: inline-grid;
            place-items: center;
            flex: 0 0 0.82rem;
        }

        .roadmap-badge-icon-image {
            width: 100%;
            height: 100%;
            display: block;
        }

        .roadmap-badge-icon-fallback {
            font-size: 0.58rem;
            font-weight: 900;
            line-height: 1;
        }

        .roadmap-item-category {
            padding-left: 0;
        }

        .roadmap-status-badge {
            color: var(--itops-blue);
            background: color-mix(in srgb, var(--itops-blue), transparent 90%);
        }

        .roadmap-source-badge {
            color: var(--itops-green);
            background: color-mix(in srgb, var(--itops-green), transparent 90%);
        }

        .roadmap-source-github {
            color: var(--itops-purple);
            background: color-mix(in srgb, var(--itops-purple), transparent 88%);
        }

        .roadmap-item-body p {
            margin: 0.42rem 0 0;
            padding: 0 !important;
            color: var(--itops-text-secondary);
            font-size: 0.84rem;
            line-height: 1.45;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .roadmap-item-body small {
            margin-top: 0.38rem;
            /* #64758e measured 2.98:1 against the dark bg -- below WCAG AA's
               4.5:1 minimum for normal text. --itops-muted (4.59:1) clears it. */
            color: var(--itops-muted);
            font-size: 0.75rem;
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
            border-radius: var(--card-radius);
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
            border-radius: var(--card-radius);
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
            background: linear-gradient(135deg, var(--itops-blue), var(--itops-blue-dark));
        }

        button[kind="primary"],
        button[kind="secondary"],
        .stDownloadButton button,
        .stFormSubmitButton button {
            border-radius: var(--card-radius) !important;
            font-weight: 800 !important;
        }

        .stDownloadButton button {
            white-space: normal !important;
            line-height: 1.3 !important;
            text-wrap: balance;
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

            .tool-page-header-with-illustration {
                flex-direction: column;
                align-items: stretch;
            }

            .tool-page-header-main {
                width: 100%;
            }

            .tool-page-header-illustration {
                width: 100%;
                flex-basis: auto;
                margin-top: 0.75rem;
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
                padding-left: 0.9rem;
            }

            .roadmap-footer-note span {
                display: block;
                margin: 0.35rem 0 0.8rem;
            }

            /* Multi-metric rows (4-6 st.metric columns) rely entirely on
               Streamlit's native column-stacking below this breakpoint --
               without this, a stacked 4-6-metric row reads as an ungrouped
               wall of numbers with no visual relationship to each other. */
            [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {
                background: var(--itops-surface);
                border: 1px solid var(--itops-surface-border);
                border-radius: var(--card-radius);
                padding: 0.75rem 1rem;
                margin: 0.5rem 0;
            }
        }
        </style>
        """
    css = css.replace("__ITOPS_ROOT_VARS__", root_vars)
    st.markdown(css, unsafe_allow_html=True)
