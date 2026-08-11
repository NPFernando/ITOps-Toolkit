from __future__ import annotations

from utils.text_stats import analyze_text


def test_analyze_text_basic_counts():
    result = analyze_text("The quick brown fox jumps over the lazy dog.")

    assert result["ok"] is True
    assert result["word_count"] == 9
    assert result["sentence_count"] == 1


def test_analyze_text_handles_contractions():
    result = analyze_text("Don't stop! Isn't this fun?")

    assert result["ok"] is True
    words = [w["word"] for w in result["top_words"]]
    assert "don't" in words
    assert "isn't" in words
    assert result["sentence_count"] == 2


def test_analyze_text_char_counts():
    result = analyze_text("ab cd")

    assert result["char_count"] == 5
    assert result["char_count_no_spaces"] == 4


def test_analyze_text_top_words_frequency_order():
    result = analyze_text("apple apple banana apple banana cherry")

    assert result["top_words"][0] == {"word": "apple", "count": 3}
    assert result["top_words"][1] == {"word": "banana", "count": 2}


def test_analyze_text_rejects_empty_input():
    result = analyze_text("")

    assert result["ok"] is False
    assert result["error"] == "Paste text to analyze."


def test_analyze_text_rejects_oversized_input():
    result = analyze_text("a" * 50_001)

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_analyze_text_ignores_numbers_and_punctuation_as_words():
    result = analyze_text("Order #12345 costs $99.99!")

    words = [w["word"] for w in result["top_words"]]
    assert "12345" not in words
    assert "order" in words
    assert "costs" in words
