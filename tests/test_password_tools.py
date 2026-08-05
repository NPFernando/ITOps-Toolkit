import string

from utils import password_tools


def test_generate_password_respects_length_and_charset():
    result = password_tools.generate_password(20, use_upper=False, use_digits=False, use_symbols=False)

    assert result["ok"] is True
    assert len(result["password"]) == 20
    assert all(c in string.ascii_lowercase for c in result["password"])
    assert result["pool_size"] == 26


def test_generate_password_exclude_ambiguous_removes_confusing_chars():
    result = password_tools.generate_password(password_tools.MAX_LENGTH, exclude_ambiguous=True)

    assert result["ok"] is True
    assert not any(c in password_tools.AMBIGUOUS_CHARS for c in result["password"])


def test_generate_password_rejects_out_of_range_length():
    too_short = password_tools.generate_password(password_tools.MIN_LENGTH - 1)
    too_long = password_tools.generate_password(password_tools.MAX_LENGTH + 1)

    assert too_short["ok"] is False
    assert too_long["ok"] is False


def test_generate_password_requires_at_least_one_charset():
    result = password_tools.generate_password(16, use_upper=False, use_lower=False, use_digits=False, use_symbols=False)

    assert result["ok"] is False
    assert "at least one" in result["error"]


def test_generate_password_entropy_scales_with_length_and_pool():
    small = password_tools.generate_password(10, use_upper=False, use_digits=False, use_symbols=False)
    large = password_tools.generate_password(20, use_upper=False, use_digits=False, use_symbols=False)

    assert large["entropy_bits"] == small["entropy_bits"] * 2


def test_generate_passphrase_word_count_and_separator():
    result = password_tools.generate_passphrase(5, separator="_", include_number=False)

    assert result["ok"] is True
    words = result["passphrase"].split("_")
    assert len(words) == 5
    assert all(word.istitle() for word in words)


def test_generate_passphrase_include_number_appends_digits():
    result = password_tools.generate_passphrase(3, include_number=True)

    last_segment = result["passphrase"].split("-")[-1]
    assert last_segment.isdigit()


def test_generate_passphrase_no_capitalize_keeps_lowercase():
    result = password_tools.generate_passphrase(3, capitalize=False, include_number=False)

    assert result["passphrase"] == result["passphrase"].lower()


def test_generate_passphrase_rejects_out_of_range_word_count():
    too_few = password_tools.generate_passphrase(password_tools.MIN_WORDS - 1)
    too_many = password_tools.generate_passphrase(password_tools.MAX_WORDS + 1)

    assert too_few["ok"] is False
    assert too_many["ok"] is False


def test_wordlist_has_no_duplicates():
    assert len(password_tools.WORDLIST) == len(set(password_tools.WORDLIST))
