from __future__ import annotations

from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "69_CSR_Decoder.py")


def _sample_csr():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "example.com")])).sign(key, hashes.SHA256())
    return csr.public_bytes(serialization.Encoding.PEM).decode()


def test_decode_shows_key_metrics():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value(_sample_csr())
    app.button[0].click().run()
    assert not app.exception

    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Public key"] == "RSA"
    assert metrics["Key size"] == "2048"
    assert metrics["Signature"] == "Valid"


def test_invalid_csr_shows_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_area[0].set_value("not a csr")
    app.button[0].click().run()
    assert not app.exception
    md = " ".join(m.value for m in app.markdown)
    assert "tool-status-note-warning" in md
    assert "CSR decode needs attention" in md


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_area[0].set_value(_sample_csr())
    app.button[0].click().run()
    assert not app.exception
    before = len(app.metric)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.metric) == before
