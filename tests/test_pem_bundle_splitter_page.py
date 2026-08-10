from __future__ import annotations

import datetime
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "70_PEM_Bundle_Splitter.py")


def _make_cert(cn):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30))
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.PEM).decode()


def test_split_shows_dataframe():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value(_make_cert("leaf.example.com") + _make_cert("intermediate.example.com"))
    app.button[0].click().run()
    assert not app.exception

    assert any("2 certificate" in c.value for c in app.caption)
    assert len(app.dataframe) == 1


def test_invalid_bundle_shows_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_area[0].set_value("not a certificate")
    app.button[0].click().run()
    assert not app.exception
    assert any("Could not parse certificate bundle" in e.value for e in app.error)


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_area[0].set_value(_make_cert("leaf.example.com"))
    app.button[0].click().run()
    assert not app.exception
    before = len(app.dataframe)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.dataframe) == before
