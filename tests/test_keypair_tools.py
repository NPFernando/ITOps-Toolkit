from cryptography.hazmat.primitives import serialization

from utils.keypair_tools import generate_keypair


def test_generate_keypair_rejects_unknown_key_type():
    result = generate_keypair("DSA")

    assert result["ok"] is False
    assert "Unknown key type" in result["error"]


def test_generate_keypair_rejects_unsupported_rsa_size():
    result = generate_keypair("RSA", rsa_key_size=1024)

    assert result["ok"] is False
    assert "Unsupported RSA key size" in result["error"]


def test_generate_keypair_rsa_produces_loadable_pem_and_matching_public_key():
    result = generate_keypair("RSA", rsa_key_size=2048)

    assert result["ok"] is True
    private_key = serialization.load_pem_private_key(result["private_key_pem"].encode(), password=None)
    assert private_key.key_size == 2048

    regenerated_public = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )
    assert regenerated_public.decode() == result["public_key_openssh"]


def test_generate_keypair_ed25519_produces_loadable_pem():
    result = generate_keypair("Ed25519")

    assert result["ok"] is True
    private_key = serialization.load_pem_private_key(result["private_key_pem"].encode(), password=None)
    assert result["public_key_openssh"].startswith("ssh-ed25519 ")
    assert private_key is not None


def test_generate_keypair_fingerprint_matches_sha256_format():
    result = generate_keypair("Ed25519")

    assert result["fingerprint"].startswith("SHA256:")
    assert "=" not in result["fingerprint"]


def test_generate_keypair_produces_different_keys_each_call():
    a = generate_keypair("Ed25519")
    b = generate_keypair("Ed25519")

    assert a["private_key_pem"] != b["private_key_pem"]
    assert a["fingerprint"] != b["fingerprint"]
