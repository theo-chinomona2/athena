import pytest
from toolsets import resolve_toolset_for_role


def test_client_denied_terminal():
    tools = resolve_toolset_for_role("client")
    assert "terminal" not in tools
    assert "delegate_task" not in tools
    assert "write_file" not in tools
    assert "execute_code" not in tools
    assert "cronjob" not in tools
    assert "session_search" not in tools


def test_client_has_web_search():
    tools = resolve_toolset_for_role("client")
    assert "web_search" in tools
    assert "memory" in tools


def test_tenant_admin_has_session_search():
    tools = resolve_toolset_for_role("tenant_admin")
    assert "session_search" in tools
    assert "terminal" not in tools


def test_operator_has_everything():
    tools = resolve_toolset_for_role("operator")
    assert "terminal" in tools
    assert "delegate_task" in tools
    assert "session_search" in tools
    assert "cronjob" in tools


def test_invalid_role_raises():
    with pytest.raises(ValueError, match="Unknown role"):
        resolve_toolset_for_role("superadmin")
