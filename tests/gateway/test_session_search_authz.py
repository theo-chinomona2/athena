import json
import os
import tempfile
from pathlib import Path

import pytest

from hermes_state import SessionDB
from tools.session_search_tool import session_search


@pytest.fixture
def db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    db = SessionDB(db_path=Path(path))
    yield db
    os.unlink(path)


def _seed(db, sid, tenant):
    db.create_session(
        session_id=sid,
        source="whatsapp",
        tenant_id=tenant,
        member_id="m",
        agent_id="a",
        session_key=f"agent:{tenant}.m.a:whatsapp:dm:1",
    )
    db.append_message(sid, role="user", content=f"hello from {tenant} secret")


def test_browse_isolated_by_tenant(db):
    _seed(db, "s-theo", "theo")
    _seed(db, "s-dad", "dad")
    out = json.loads(session_search(db=db, tenant_id="theo"))
    ids = [r["session_id"] for r in out["results"]]
    assert "s-theo" in ids
    assert "s-dad" not in ids


def test_operator_browse_sees_all(db):
    _seed(db, "s-theo", "theo")
    _seed(db, "s-dad", "dad")
    out = json.loads(session_search(db=db, tenant_id=None))
    ids = [r["session_id"] for r in out["results"]]
    assert "s-theo" in ids
    assert "s-dad" in ids


def test_read_other_tenant_denied(db):
    _seed(db, "s-theo", "theo")
    out = json.loads(session_search(db=db, session_id="s-theo", tenant_id="dad"))
    assert out["success"] is False


def test_read_own_tenant_ok(db):
    _seed(db, "s-theo", "theo")
    out = json.loads(session_search(db=db, session_id="s-theo", tenant_id="theo"))
    assert out["success"] is True
    assert out["session_id"] == "s-theo"


def test_discover_isolated_by_tenant(db):
    _seed(db, "s-theo", "theo")
    _seed(db, "s-dad", "dad")
    out = json.loads(session_search(db=db, query="secret", tenant_id="theo"))
    ids = [r["session_id"] for r in out["results"]]
    assert "s-dad" not in ids


def test_cross_profile_denied_for_tenant(db):
    out = json.loads(session_search(db=db, session_id="x", profile="work", tenant_id="theo"))
    assert out["success"] is False
    assert "restricted" in (out.get("error") or "").lower()
