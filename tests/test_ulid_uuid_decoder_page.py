from __future__ import annotations

import uuid
from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils.id_generator import generate_ulid


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "53_ULID_UUID_Decoder.py")


def test_ulid_tab_decodes_a_real_generated_ulid():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    generated = generate_ulid(timestamp_ms=1_700_000_000_000)
    ulid_input = next(t for t in app.text_input if t.label == "ULID")
    ulid_input.set_value(generated).run()
    assert not app.exception

    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Epoch milliseconds"] == "1700000000000"
    assert "2023-11-14" in metrics["Created (UTC)"]


def test_ulid_tab_shows_empty_state_when_blank():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md
    assert not app.error


def test_uuid_tab_decodes_v1_and_v4():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    uuid_input = next(t for t in app.text_input if t.label == "UUID")
    uuid_input.set_value(str(uuid.uuid1())).run()
    assert not app.exception
    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Version"] == "1"
    assert "Created (UTC)" in metrics

    uuid_input2 = next(t for t in app.text_input if t.label == "UUID")
    uuid_input2.set_value(str(uuid.uuid4())).run()
    assert not app.exception
    infos = [i.value for i in app.info]
    assert any("does not embed a creation timestamp" in i for i in infos)


def test_uuid_tab_variant_is_not_rendered_as_a_metric():
    """Regression: uuid.UUID.variant returns a full phrase ("specified in
    RFC 4122"), not the short number/word every other st.metric here shows
    -- it must render as a caption instead."""
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    uuid_input = next(t for t in app.text_input if t.label == "UUID")
    uuid_input.set_value(str(uuid.uuid4())).run()
    assert not app.exception

    assert "Variant" not in {m.label for m in app.metric}
    captions = " ".join(c.value for c in app.caption)
    assert "Variant: specified in RFC 4122" in captions


def test_uuid_tab_nil_uuid_shows_na_not_bare_none():
    """Regression: the nil UUID (all zeros) has no version bits set --
    decode_uuid returns version=None, which must not render as a literal
    "None" metric value with no explanation."""
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    uuid_input = next(t for t in app.text_input if t.label == "UUID")
    uuid_input.set_value("00000000-0000-0000-0000-000000000000").run()
    assert not app.exception

    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Version"] == "N/A"
    captions = " ".join(c.value for c in app.caption)
    assert "no version bits set" in captions
    infos = [i.value for i in app.info]
    assert not any("UUID version None" in i for i in infos)


def test_ulid_and_uuid_inputs_are_length_limited():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    ulid_input = next(t for t in app.text_input if t.label == "ULID")
    uuid_input = next(t for t in app.text_input if t.label == "UUID")
    assert ulid_input.proto.max_chars > 0
    assert uuid_input.proto.max_chars > 0


def test_results_persist_after_sidebar_interaction():
    """Regression recipe used across this app: touching the sidebar's
    quick-search box triggers a rerun of the whole page -- since this page
    has no submit button/session_state, it simply recomputes from the
    current live input on every rerun, so results must not vanish."""
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    ulid_input = next(t for t in app.text_input if t.label == "ULID")
    ulid_input.set_value(generate_ulid(timestamp_ms=1_700_000_000_000)).run()
    assert not app.exception
    before = len(app.metric)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.metric) == before
