"""One-time migration: backfill pre-tenancy sessions with the main.main.main identity.

Existing single-tenant deployments have sessions whose ``tenant_id`` / ``member_id``
/ ``agent_id`` columns are NULL (rows created before multi-tenancy).  This migration
stamps them with ``main`` so they belong to the default tenant triple
``main.main.main`` — keeping legacy keys valid and recall-authz consistent.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Union


def migrate_main_sessions(db_path: Union[str, Path]) -> int:
    """Set tenant_id/member_id/agent_id = 'main' on sessions that have none.

    Safe to run multiple times — the ``WHERE tenant_id IS NULL`` clause is
    idempotent (already-migrated rows are skipped).  Returns the number of
    rows updated.
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(
            "UPDATE sessions SET tenant_id='main', member_id='main', agent_id='main' "
            "WHERE tenant_id IS NULL"
        )
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()
