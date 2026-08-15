import pyotp

from utils.totp_tools import MAX_CODE_LENGTH, MAX_SECRET_LENGTH, current_code, generate_secret, verify_code


def test_generate_secret_is_valid_base32():
    secret = generate_secret()

    # Round-trips through pyotp without raising.
    pyotp.TOTP(secret).now()
    assert len(secret) >= 16


def test_current_code_rejects_empty_secret():
    result = current_code("")

    assert result["ok"] is False
    assert "Enter a base32 secret" in result["error"]


def test_current_code_rejects_invalid_secret():
    result = current_code("not valid base32!!!")

    assert result["ok"] is False
    assert "Invalid base32 secret" in result["error"]


def test_current_code_rejects_oversized_secret():
    result = current_code("A" * (MAX_SECRET_LENGTH + 1))

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_current_code_matches_pyotp_directly(monkeypatch):
    secret = pyotp.random_base32()
    fixed_now = 1_700_000_000
    monkeypatch.setattr("utils.totp_tools.time.time", lambda: fixed_now)
    result = current_code(secret)

    assert result["ok"] is True
    assert result["code"] == pyotp.TOTP(secret).at(fixed_now)
    assert 0 < result["seconds_remaining"] <= 30


def test_verify_code_accepts_correct_code():
    secret = pyotp.random_base32()
    code = pyotp.TOTP(secret).now()

    result = verify_code(secret, code)

    assert result["ok"] is True
    assert result["valid"] is True


def test_verify_code_rejects_wrong_code():
    secret = pyotp.random_base32()

    result = verify_code(secret, "000000")

    assert result["ok"] is True
    assert result["valid"] is False


def test_verify_code_rejects_empty_secret():
    result = verify_code("", "123456")

    assert result["ok"] is False
    assert "Enter a base32 secret" in result["error"]


def test_verify_code_rejects_empty_code():
    result = verify_code(pyotp.random_base32(), "")

    assert result["ok"] is False
    assert "Enter a code to verify" in result["error"]


def test_verify_code_rejects_invalid_secret():
    result = verify_code("not valid base32!!!", "123456")

    assert result["ok"] is False
    assert "Invalid base32 secret" in result["error"]


def test_verify_code_rejects_oversized_code():
    result = verify_code(pyotp.random_base32(), "1" * (MAX_CODE_LENGTH + 1))

    assert result["ok"] is False
    assert "longer than" in result["error"]
