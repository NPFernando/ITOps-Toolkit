from utils.file_integrity import MAX_FILE_SIZE_BYTES, find_matching_algorithm, hash_bytes


def test_hash_bytes_returns_all_algorithms():
    result = hash_bytes(b"hello world")

    assert result["ok"] is True
    assert result["size_bytes"] == 11
    assert set(result["digests"]) == {"md5", "sha1", "sha256", "sha512"}


def test_hash_bytes_is_deterministic():
    a = hash_bytes(b"hello world")
    b = hash_bytes(b"hello world")

    assert a["digests"] == b["digests"]


def test_hash_bytes_differs_for_different_content():
    a = hash_bytes(b"hello world")
    b = hash_bytes(b"hello world!")

    assert a["digests"] != b["digests"]


def test_hash_bytes_rejects_oversized_input():
    result = hash_bytes(b"x" * (MAX_FILE_SIZE_BYTES + 1))

    assert result["ok"] is False
    assert "larger than" in result["error"]


def test_find_matching_algorithm_matches_case_insensitively():
    digests = hash_bytes(b"hello world")["digests"]

    assert find_matching_algorithm(digests, digests["sha256"].upper()) == "sha256"


def test_find_matching_algorithm_strips_whitespace():
    digests = hash_bytes(b"hello world")["digests"]

    assert find_matching_algorithm(digests, f"  {digests['md5']}  \n") == "md5"


def test_find_matching_algorithm_returns_none_for_no_match():
    digests = hash_bytes(b"hello world")["digests"]

    assert find_matching_algorithm(digests, "not-a-real-hash") is None


def test_find_matching_algorithm_returns_none_for_empty_expected():
    digests = hash_bytes(b"hello world")["digests"]

    assert find_matching_algorithm(digests, "") is None
