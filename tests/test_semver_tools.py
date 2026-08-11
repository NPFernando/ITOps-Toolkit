from __future__ import annotations

from utils.semver_tools import compare_versions, parse_semver, sort_versions


def test_parse_basic_version():
    result = parse_semver("1.2.3")

    assert result["ok"] is True
    assert (result["major"], result["minor"], result["patch"]) == (1, 2, 3)
    assert result["prerelease"] is None
    assert result["buildmetadata"] is None


def test_parse_prerelease_and_build_metadata():
    result = parse_semver("1.2.3-beta.1+build.5")

    assert result["ok"] is True
    assert result["prerelease"] == "beta.1"
    assert result["buildmetadata"] == "build.5"


def test_parse_rejects_leading_zero():
    result = parse_semver("1.02.3")

    assert result["ok"] is False


def test_parse_rejects_incomplete_version():
    result = parse_semver("1.2")

    assert result["ok"] is False
    assert "not a valid SemVer" in result["error"]


def test_parse_rejects_empty_input():
    result = parse_semver("")

    assert result["ok"] is False
    assert result["error"] == "Enter a version string."


def test_compare_major_minor_patch():
    assert compare_versions(parse_semver("2.0.0"), parse_semver("1.9.9")) == 1
    assert compare_versions(parse_semver("1.2.3"), parse_semver("1.2.4")) == -1
    assert compare_versions(parse_semver("1.2.3"), parse_semver("1.2.3")) == 0


def test_compare_prerelease_has_lower_precedence_than_release():
    assert compare_versions(parse_semver("1.0.0-alpha"), parse_semver("1.0.0")) == -1


def test_compare_numeric_prerelease_identifiers_numerically():
    # "1.0.0-alpha.2" > "1.0.0-alpha.10" would be wrong under lexical (string)
    # comparison -- SemVer requires numeric identifiers compare numerically.
    assert compare_versions(parse_semver("1.0.0-alpha.2"), parse_semver("1.0.0-alpha.10")) == -1


def test_compare_numeric_identifier_lower_than_alphanumeric():
    assert compare_versions(parse_semver("1.0.0-1"), parse_semver("1.0.0-alpha")) == -1


def test_sort_versions_matches_semver_spec_example():
    # The exact precedence-order example published at semver.org.
    versions = ["1.0.0", "1.0.0-rc.1", "1.0.0-beta.11", "1.0.0-beta.2", "1.0.0-beta", "1.0.0-alpha.beta", "1.0.0-alpha.1", "1.0.0-alpha"]

    result = sort_versions(versions)

    assert result["ok"] is True
    assert result["sorted"] == [
        "1.0.0-alpha",
        "1.0.0-alpha.1",
        "1.0.0-alpha.beta",
        "1.0.0-beta",
        "1.0.0-beta.2",
        "1.0.0-beta.11",
        "1.0.0-rc.1",
        "1.0.0",
    ]


def test_sort_versions_descending():
    result = sort_versions(["1.0.0", "2.0.0", "1.5.0"], descending=True)

    assert result["ok"] is True
    assert result["sorted"] == ["2.0.0", "1.5.0", "1.0.0"]


def test_sort_versions_rejects_empty_list():
    result = sort_versions([])

    assert result["ok"] is False


def test_sort_versions_rejects_invalid_entry():
    result = sort_versions(["1.0.0", "not-a-version"])

    assert result["ok"] is False
    assert "not-a-version" in result["error"]
