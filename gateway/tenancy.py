"""Multi-tenant identity model, role resolver, capability map, and path resolver."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class Role(str, Enum):
    OPERATOR = "operator"
    TENANT_ADMIN = "tenant_admin"
    CLIENT = "client"


@dataclass
class MemberDef:
    id: str
    role: str = "client"
    default_agent: str = "main"


@dataclass
class TenantDef:
    id: str
    members: List[MemberDef] = field(default_factory=list)


@dataclass
class TenantBinding:
    source_id: str
    tenant: str
    member: str
    agent: str


@dataclass
class TenantConfig:
    tenants: List[TenantDef] = field(default_factory=list)
    bindings: List[TenantBinding] = field(default_factory=list)


@dataclass
class TenantIdentity:
    tenant: str
    member: str
    agent: str
    role: Role

    @property
    def triple(self) -> str:
        return f"{self.tenant}.{self.member}.{self.agent}"


_ROLE_MAP = {
    "operator": Role.OPERATOR,
    "tenant_admin": Role.TENANT_ADMIN,
    "client": Role.CLIENT,
}

# Tools available to each role.  OPERATOR gets everything; CLIENT gets only
# curated assistant tools.  These are the ALLOWED sets — toolsets.py uses them
# to build the bundle; everything not in the set is denied.
_ROLE_CAPS: dict[Role, set[str]] = {
    Role.OPERATOR: {
        "web_search", "web_extract", "terminal", "process", "read_terminal",
        "read_file", "write_file", "patch", "search_files",
        "vision_analyze", "image_generate",
        "skills_list", "skill_view", "skill_manage",
        "browser_navigate", "browser_snapshot", "browser_click",
        "browser_type", "browser_scroll", "browser_back",
        "browser_press", "browser_get_images", "browser_vision",
        "browser_console", "browser_cdp", "browser_dialog",
        "text_to_speech", "todo", "memory",
        "session_search", "clarify",
        "execute_code", "delegate_task", "cronjob",
        "ha_list_entities", "ha_get_state", "ha_list_services", "ha_call_service",
        "kanban_show", "kanban_list", "kanban_complete", "kanban_block",
        "kanban_heartbeat", "kanban_comment", "kanban_create",
        "kanban_link", "kanban_unblock", "computer_use",
        "relay_message",
        "manage_all_tenants", "raw_pty",
    },
    Role.TENANT_ADMIN: {
        "web_search", "web_extract", "read_file",
        "vision_analyze", "image_generate",
        "skills_list", "skill_view",
        "browser_navigate", "browser_snapshot", "browser_click",
        "browser_type", "browser_scroll", "browser_back",
        "browser_press", "browser_get_images", "browser_vision",
        "todo", "memory", "session_search", "clarify",
        "relay_message",
    },
    Role.CLIENT: {
        "web_search", "web_extract",
        "vision_analyze", "image_generate",
        "browser_navigate", "browser_snapshot",
        "todo", "memory", "clarify",
        "relay_message",
    },
}


def resolve_identity(source_id: str, config: TenantConfig) -> TenantIdentity:
    """Map a raw source identifier (phone number, user hash, etc.) to an identity triple + role.

    Falls back to an isolated CLIENT identity for unknown sources.
    """
    for binding in config.bindings:
        if binding.source_id == source_id:
            role_str = _member_role(binding.tenant, binding.member, config)
            role = _ROLE_MAP.get(role_str, Role.CLIENT)
            return TenantIdentity(
                tenant=binding.tenant,
                member=binding.member,
                agent=binding.agent,
                role=role,
            )
    # Unknown source — isolated client-only sandbox; tenant = source_id slug.
    slug = _slugify(source_id)
    logger.warning("Unknown source_id %r — isolated client identity '%s'", source_id, slug)
    return TenantIdentity(tenant=slug, member=slug, agent="main", role=Role.CLIENT)


def _member_role(tenant_id: str, member_id: str, config: TenantConfig) -> str:
    for t in config.tenants:
        if t.id == tenant_id:
            for m in t.members:
                if m.id == member_id:
                    return m.role
    return "client"


def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9_]", "_", s.lower())


def capabilities(role: Role) -> set[str]:
    """Return the set of allowed tool names for this role."""
    return set(_ROLE_CAPS.get(role, set()))


# ── Path resolvers ──────────────────────────────────────────────────────────

def tenant_path(hermes_home: Path, identity: TenantIdentity) -> Path:
    return hermes_home / "tenants" / identity.tenant


def member_path(hermes_home: Path, identity: TenantIdentity) -> Path:
    return tenant_path(hermes_home, identity) / "members" / identity.member


def agent_path(hermes_home: Path, identity: TenantIdentity) -> Path:
    return member_path(hermes_home, identity) / "agents" / identity.agent


def memory_path(hermes_home: Path, identity: TenantIdentity) -> Path:
    return agent_path(hermes_home, identity) / "memory"


def workspace_path(hermes_home: Path, identity: TenantIdentity) -> Path:
    return agent_path(hermes_home, identity) / "workspace"


def skill_read_paths(hermes_home: Path, identity: TenantIdentity) -> list[Path]:
    """Ordered skill discovery path stack: agent-private → member-shared → tenant-shared → bundled."""
    return [
        workspace_path(hermes_home, identity),
        agent_path(hermes_home, identity),
        member_path(hermes_home, identity) / "shared",
        tenant_path(hermes_home, identity) / "shared",
        hermes_home / "skills",
    ]
