from pathlib import Path
from gateway.tenancy import (
    TenantIdentity, Role, skill_read_paths, agent_path, member_path, tenant_path,
)


def test_skill_paths_differ_by_tenant():
    identity_theo = TenantIdentity(tenant="theo", member="theo", agent="coding", role=Role.OPERATOR)
    identity_dad = TenantIdentity(tenant="dad", member="dad", agent="news", role=Role.TENANT_ADMIN)
    home = Path("/hermes")
    paths_theo = skill_read_paths(home, identity_theo)
    paths_dad = skill_read_paths(home, identity_dad)
    assert paths_theo != paths_dad
    # Every theo path is either under theo's tree or the shared bundled dir.
    assert all("theo" in str(p) or str(p) == str(home / "skills") for p in paths_theo)
    assert all("dad" in str(p) or str(p) == str(home / "skills") for p in paths_dad)


def test_skill_paths_ordering_agent_private_first_bundled_last():
    identity = TenantIdentity(tenant="t", member="m", agent="a", role=Role.OPERATOR)
    home = Path("/hermes")
    paths = skill_read_paths(home, identity)
    # agent-private workspace first; bundled global skills last.
    assert paths[0] == agent_path(home, identity) / "workspace"
    assert paths[1] == agent_path(home, identity)
    assert paths[2] == member_path(home, identity) / "shared"
    assert paths[3] == tenant_path(home, identity) / "shared"
    assert paths[-1] == home / "skills"


def test_skill_paths_isolation_no_cross_tenant_leak():
    a = TenantIdentity(tenant="alpha", member="m1", agent="x", role=Role.CLIENT)
    b = TenantIdentity(tenant="beta", member="m1", agent="x", role=Role.CLIENT)
    home = Path("/hermes")
    pa = {str(p) for p in skill_read_paths(home, a)}
    pb = {str(p) for p in skill_read_paths(home, b)}
    # Only the shared bundled dir is common; no tenant-private path leaks across.
    assert pa & pb == {str(home / "skills")}
