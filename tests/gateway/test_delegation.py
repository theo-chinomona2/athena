import pytest
from unittest.mock import MagicMock


class _Captured(Exception):
    """Raised by the fake AIAgent after capturing kwargs to skip heavy post-build work."""


def _fake_parent(tenant_id, memory_root, enabled_toolsets):
    p = MagicMock()
    p._tenant_id = tenant_id
    p._memory_root = memory_root
    p.enabled_toolsets = enabled_toolsets
    p._delegate_depth = 0
    p.model = "test-model"
    p.base_url = ""
    p.provider = ""
    p.api_mode = None
    p.api_key = "k"
    p.acp_command = None
    p.acp_args = []
    p.reasoning_config = None
    p._fallback_chain = None
    p.providers_allowed = None
    p.providers_ignored = None
    p.providers_order = None
    p.provider_sort = None
    p.openrouter_min_coding_score = None
    p.max_tokens = None
    p.prefill_messages = None
    p._session_db = None
    p.session_id = "parent-sess"
    p._credential_pool = None
    p._delegate_spinner = None
    p.tool_progress_callback = None
    p._subagent_id = None
    p._subdirectory_hints = None
    p.terminal_cwd = None
    p.cwd = None
    p._current_turn_id = ""
    p.valid_tool_names = []
    p._client_kwargs = {}
    return p


def _capture_child_kwargs(parent, monkeypatch):
    import run_agent
    import tools.delegate_tool as dt
    captured = {}

    def fake_AIAgent(**kwargs):
        captured.update(kwargs)
        raise _Captured()

    monkeypatch.setattr(run_agent, "AIAgent", fake_AIAgent)
    with pytest.raises(_Captured):
        dt._build_child_agent(
            task_index=0,
            goal="do x",
            context=None,
            toolsets=None,
            model="test-model",
            max_iterations=10,
            task_count=1,
            parent_agent=parent,
        )
    return captured


def test_child_inherits_parent_tenant(monkeypatch):
    """Child AIAgent constructed by delegate_task must receive parent's tenant identity."""
    parent = _fake_parent(
        "dad", "/h/tenants/dad/members/dad/agents/news/memory", ["tenant_admin_bundle"]
    )
    captured = _capture_child_kwargs(parent, monkeypatch)
    assert captured["tenant_id"] == "dad"
    assert captured["memory_root"] == "/h/tenants/dad/members/dad/agents/news/memory"


def test_child_cannot_escalate_tenant(monkeypatch):
    """A client-role parent's child must never gain operator/developer tools."""
    parent = _fake_parent("dad", "/h/dad/mem", ["client_curated"])
    captured = _capture_child_kwargs(parent, monkeypatch)
    child_ts = captured["enabled_toolsets"] or []
    assert "client_curated" in child_ts
    assert "terminal" not in child_ts
    assert "delegate_task" not in child_ts
    assert "operator_bundle" not in child_ts


def test_child_without_tenant_passes_none(monkeypatch):
    """Single-tenant parent (no tenant id) -> child tenant_id None (no scoping)."""
    parent = _fake_parent(None, None, ["hermes-cli"])
    captured = _capture_child_kwargs(parent, monkeypatch)
    assert captured["tenant_id"] is None
    assert captured["memory_root"] is None
