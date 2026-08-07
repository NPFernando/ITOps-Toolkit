from utils.bcrypt_tools import MAX_PASSWORD_BYTES, MAX_ROUNDS, MIN_ROUNDS, hash_password, verify_password


def test_hash_password_rejects_empty_input():
    result = hash_password("")

    assert result["ok"] is False
    assert "Enter a password" in result["error"]


def test_hash_password_rejects_out_of_range_rounds():
    assert hash_password("hello", rounds=MIN_ROUNDS - 1)["ok"] is False
    assert hash_password("hello", rounds=MAX_ROUNDS + 1)["ok"] is False


def test_hash_password_rejects_oversized_password():
    result = hash_password("x" * (MAX_PASSWORD_BYTES + 1), rounds=10)

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_hash_password_produces_verifiable_hash():
    result = hash_password("hello world", rounds=10)

    assert result["ok"] is True
    assert result["hash"].startswith("$2b$10$")


def test_verify_password_accepts_correct_value():
    hashed = hash_password("hello world", rounds=10)["hash"]

    result = verify_password("hello world", hashed)

    assert result["ok"] is True
    assert result["matches"] is True


def test_verify_password_rejects_wrong_value():
    hashed = hash_password("hello world", rounds=10)["hash"]

    result = verify_password("wrong", hashed)

    assert result["ok"] is True
    assert result["matches"] is False


def test_verify_password_rejects_empty_inputs():
    assert verify_password("", "$2b$10$abc")["ok"] is False
    assert verify_password("x", "")["ok"] is False


def test_verify_password_rejects_invalid_hash():
    result = verify_password("hello", "not-a-valid-hash")

    assert result["ok"] is False
    assert "Not a valid bcrypt hash" in result["error"]


def test_verify_password_rejects_oversized_password():
    result = verify_password("x" * (MAX_PASSWORD_BYTES + 1), "$2b$10$abc")

    assert result["ok"] is False
    assert "longer than" in result["error"]
