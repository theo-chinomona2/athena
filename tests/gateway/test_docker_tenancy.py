from pathlib import Path

from gateway.tenancy import TenantIdentity, Role
from tools.environments.docker import _build_mounts, _default_mounts


def test_client_mount_excludes_credentials():
    identity = TenantIdentity(tenant="dad", member="dad", agent="news", role=Role.CLIENT)
    mounts = _build_mounts(identity, Path("/hermes"))
    targets = [m["target"] for m in mounts]
    assert "/workspace" in targets
    assert "/root" not in targets
    assert "/credentials" not in targets


def test_tenant_admin_mount_excludes_credentials():
    identity = TenantIdentity(tenant="dad", member="dad", agent="news", role=Role.TENANT_ADMIN)
    mounts = _build_mounts(identity, Path("/hermes"))
    targets = [m["target"] for m in mounts]
    assert "/workspace" in targets
    assert "/credentials" not in targets
    assert "/root" not in targets


def test_client_workspace_is_tenant_scoped():
    identity = TenantIdentity(tenant="dad", member="dad", agent="news", role=Role.CLIENT)
    mounts = _build_mounts(identity, Path("/hermes"))
    ws = next(m for m in mounts if m["target"] == "/workspace")
    assert "tenants/dad/members/dad/agents/news/workspace" in ws["source"]


def test_operator_gets_full_mounts():
    identity = TenantIdentity(tenant="theo", member="theo", agent="coding", role=Role.OPERATOR)
    mounts = _build_mounts(identity, Path("/hermes"))
    targets = [m["target"] for m in mounts]
    assert "/workspace" in targets
    assert "/root" in targets
    assert "/credentials" in targets


def test_no_identity_defaults_to_operator_mounts():
    mounts = _build_mounts(None, Path("/hermes"))
    assert mounts == _default_mounts(Path("/hermes"))
