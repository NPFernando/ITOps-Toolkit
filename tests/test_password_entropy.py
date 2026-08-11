from __future__ import annotations

from utils.password_entropy import estimate_entropy


def test_estimate_entropy_lowercase_only():
    result = estimate_entropy("password")

    assert result["ok"] is True
    assert result["pool_size"] == 26
    assert result["strength_label"] == "Reasonable"


def test_estimate_entropy_diverse_password_scores_higher():
    weak = estimate_entropy("password")
    strong = estimate_entropy("Tr0ub4dor&3")

    assert strong["entropy_bits"] > weak["entropy_bits"]
    assert strong["pool_size"] == 94


def test_estimate_entropy_single_character():
    result = estimate_entropy("a")

    assert result["ok"] is True
    assert result["strength_label"] == "Very weak"


def test_estimate_entropy_whitespace_only_input():
    result = estimate_entropy("   ")

    assert result["ok"] is True
    assert result["pool_size"] == 32


def test_estimate_entropy_rejects_empty_input():
    result = estimate_entropy("")

    assert result["ok"] is False
    assert result["error"] == "Enter a password to check."


def test_estimate_entropy_rejects_oversized_input():
    result = estimate_entropy("a" * 129)

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_estimate_entropy_bucket_boundaries():
    # A 60-char lowercase-only password: 60 * log2(26) ~= 282 bits, well
    # into "Strong" territory -- sanity-checks the bucket thresholds don't
    # misfire for a long single-character-class password.
    result = estimate_entropy("a" * 60)

    assert result["strength_label"] in ("Strong", "Very strong")
