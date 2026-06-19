"""Tenant stamping on agent session rows — used by cron (Task 11) and gateway."""
from pathlib import Path

from hermes_state import SessionDB
from run_agent import AIAgent


def _bare_agent(**attrs):
    a = object.__new__(AIAgent)
    a._session_db_created = False
    a.model = "m"
    a._session_init_model_config = {}
    a._cached_system_prompt = ""
    a._parent_session_id = None
    a.platform = "cron"
    a._session_db = None
    a._tenant_id = None
    a._gateway_session_key = None
    for k, v in attrs.items():
        setattr(a, k, v)
    return a


def test_tenant_columns_from_triple_key():
    a = _bare_agent(
        _tenant_id="dad",
        _gateway_session_key="agent:dad.emp1.research:whatsapp:dm:1",
    )
    cols = a._tenant_session_columns()
    assert cols["tenant_id"] == "dad"
    assert cols["member_id"] == "emp1"
    assert cols["agent_id"] == "research"
    assert cols["session_key"] == "agent:dad.emp1.research:whatsapp:dm:1"


def test_tenant_columns_empty_for_single_tenant():
    a = _bare_agent(_tenant_id=None, _gateway_session_key=None)
    assert a._tenant_session_columns() == {}


def test_cron_session_stamped_with_tenant(tmp_path):
    # Cron agent: tenant_id set, no gateway session key (member/agent NULL).
    db = SessionDB(db_path=tmp_path / "state.db")
    a = _bare_agent(_session_db=db, session_id="cron-1", _tenant_id="dad")
    a._ensure_db_session()
    row = db.get_session("cron-1")
    assert row["tenant_id"] == "dad"


def test_single_tenant_session_leaves_tenant_null(tmp_path):
    db = SessionDB(db_path=tmp_path / "state.db")
    a = _bare_agent(_session_db=db, session_id="cli-1", _tenant_id=None)
    a._ensure_db_session()
    row = db.get_session("cli-1")
    assert row["tenant_id"] is None
