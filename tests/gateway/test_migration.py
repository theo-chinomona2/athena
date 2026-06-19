import os
import tempfile
from pathlib import Path

import pytest

from hermes_state import SessionDB
from hermes_cli.migration import migrate_main_sessions


@pytest.fixture
def db_with_sessions():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    db = SessionDB(db_path=Path(path))
    # Insert a pre-migration session (tenant columns NULL).
    db._conn.execute(
        "INSERT INTO sessions (id, source, started_at) VALUES (?, ?, ?)",
        ("sess-legacy-1", "whatsapp", 1000.0),
    )
    db._conn.commit()
    yield db, path
    os.unlink(path)


def test_migrate_sets_main_triple(db_with_sessions):
    db, path = db_with_sessions
    count = migrate_main_sessions(path)
    assert count == 1
    row = db._conn.execute(
        "SELECT tenant_id, member_id, agent_id FROM sessions WHERE id = 'sess-legacy-1'"
    ).fetchone()
    assert row["tenant_id"] == "main"
    assert row["member_id"] == "main"
    assert row["agent_id"] == "main"


def test_migrate_is_idempotent(db_with_sessions):
    db, path = db_with_sessions
    assert migrate_main_sessions(path) == 1
    # Second run touches nothing — already-stamped rows are skipped.
    assert migrate_main_sessions(path) == 0


def test_migrate_preserves_existing_tenant(db_with_sessions):
    db, path = db_with_sessions
    db._conn.execute(
        "INSERT INTO sessions (id, source, started_at, tenant_id, member_id, agent_id) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("sess-tenant-1", "whatsapp", 2000.0, "dad", "emp1", "research"),
    )
    db._conn.commit()
    migrate_main_sessions(path)
    row = db._conn.execute(
        "SELECT tenant_id, member_id, agent_id FROM sessions WHERE id = 'sess-tenant-1'"
    ).fetchone()
    assert row["tenant_id"] == "dad"
    assert row["member_id"] == "emp1"
    assert row["agent_id"] == "research"
