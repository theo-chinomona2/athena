import pytest
import tempfile
import os
from pathlib import Path
from hermes_state import SessionDB


@pytest.fixture
def db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    db = SessionDB(db_path=Path(path))
    yield db
    os.unlink(path)


def _make_session(db, session_id, tenant_id, source="whatsapp"):
    db.create_session(
        session_id=session_id,
        source=source,
        tenant_id=tenant_id,
        member_id="m1",
        agent_id="a1",
        session_key=f"agent:{tenant_id}.m1.a1:{source}:dm:+1",
    )


def test_search_sessions_tenant_isolation(db):
    _make_session(db, "sess-theo-1", "theo")
    _make_session(db, "sess-dad-1", "dad")
    results = db.search_sessions(tenant_id="theo")
    ids = [r["id"] for r in results]
    assert "sess-theo-1" in ids
    assert "sess-dad-1" not in ids


def test_search_sessions_no_filter_returns_all_for_operator(db):
    _make_session(db, "sess-theo-1", "theo")
    _make_session(db, "sess-dad-1", "dad")
    results = db.search_sessions()  # no tenant filter = operator view
    ids = [r["id"] for r in results]
    assert "sess-theo-1" in ids
    assert "sess-dad-1" in ids


def test_get_session_tenant_mismatch_returns_none(db):
    # get_session(session_id, tenant_id) is the scalar recall-authz gate.
    _make_session(db, "sess-theo-1", "theo")
    result = db.get_session("sess-theo-1", tenant_id="dad")
    assert result is None


def test_get_session_tenant_match(db):
    _make_session(db, "sess-theo-1", "theo")
    result = db.get_session("sess-theo-1", tenant_id="theo")
    assert result is not None
    assert result["id"] == "sess-theo-1"


def test_tenant_columns_persisted(db):
    _make_session(db, "sess-theo-1", "theo")
    result = db.get_session("sess-theo-1", tenant_id="theo")
    assert result["tenant_id"] == "theo"
    assert result["member_id"] == "m1"
    assert result["agent_id"] == "a1"
