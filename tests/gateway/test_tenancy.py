import pytest
from pathlib import Path
from gateway.tenancy import (
    Role, TenantIdentity, TenantBinding, MemberDef, TenantDef, TenantConfig,
    resolve_identity, capabilities, tenant_path, member_path, agent_path,
    memory_path, workspace_path, skill_read_paths,
)


@pytest.fixture
def config():
    return TenantConfig(
        tenants=[
            TenantDef(id="theo", members=[
                MemberDef(id="theo", role="operator", default_agent="coding"),
            ]),
            TenantDef(id="dad", members=[
                MemberDef(id="dad", role="tenant_admin", default_agent="news"),
                MemberDef(id="employee1", role="client", default_agent="research"),
            ]),
        ],
        bindings=[
            TenantBinding(source_id="+27-you", tenant="theo", member="theo", agent="coding"),
            TenantBinding(source_id="+27-dad", tenant="dad", member="dad", agent="news"),
            TenantBinding(source_id="+27-emp1", tenant="dad", member="employee1", agent="research"),
        ],
    )


def test_resolve_identity_known(config):
    identity = resolve_identity("+27-dad", config)
    assert identity.tenant == "dad"
    assert identity.member == "dad"
    assert identity.agent == "news"
    assert identity.role == Role.TENANT_ADMIN


def test_resolve_identity_client(config):
    identity = resolve_identity("+27-emp1", config)
    assert identity.role == Role.CLIENT


def test_resolve_identity_operator(config):
    identity = resolve_identity("+27-you", config)
    assert identity.role == Role.OPERATOR


def test_resolve_identity_unknown_defaults_client(config):
    identity = resolve_identity("+27-unknown", config)
    assert identity.role == Role.CLIENT
    # Unknown sources slug to an isolated client tenant. The slug preserves
    # isolation (distinct sources -> distinct slugs); "+27-unknown" -> "_27_unknown".
    assert identity.tenant == "_27_unknown"
    assert identity.triple == "_27_unknown._27_unknown.main"


def test_triple(config):
    identity = resolve_identity("+27-you", config)
    assert identity.triple == "theo.theo.coding"


def test_capabilities_client_denies_terminal(config):
    caps = capabilities(Role.CLIENT)
    assert "terminal" not in caps
    assert "delegate_task" not in caps
    assert "web_search" in caps


def test_capabilities_operator_has_all(config):
    caps = capabilities(Role.OPERATOR)
    assert "terminal" in caps
    assert "delegate_task" in caps


def test_tenant_path(config):
    home = Path("/home/hermes")
    identity = resolve_identity("+27-dad", config)
    assert tenant_path(home, identity) == Path("/home/hermes/tenants/dad")


def test_agent_path(config):
    home = Path("/home/hermes")
    identity = resolve_identity("+27-you", config)
    assert agent_path(home, identity) == Path("/home/hermes/tenants/theo/members/theo/agents/coding")


def test_memory_path(config):
    home = Path("/home/hermes")
    identity = resolve_identity("+27-you", config)
    assert memory_path(home, identity) == Path("/home/hermes/tenants/theo/members/theo/agents/coding/memory")


def test_skill_read_paths_order(config):
    home = Path("/home/hermes")
    identity = resolve_identity("+27-you", config)
    paths = skill_read_paths(home, identity)
    # agent-private first, bundled last
    assert paths[0] == agent_path(home, identity) / "workspace"
    assert paths[-1] == home / "skills"


def test_capabilities_tenant_admin_no_escalation():
    caps = capabilities(Role.TENANT_ADMIN)
    assert "manage_all_tenants" not in caps
    assert "raw_pty" not in caps
