"""Method-level authorization for tui_gateway connections.

Maps each JSON-RPC method to the minimum role required to call it.  Local
operator connections (the default for the stdio TUI) clear every gate; the
policy only bites for authenticated per-tenant connections (dashboard WS that
presented a per-tenant token via ``hermes_cli.dashboard_auth.verify_token``).
"""
from __future__ import annotations

# Map method → minimum required role.  Methods not listed default to DENY for
# non-operators (operator-only), so a new method is fail-closed until policy is set.
_METHOD_POLICY: dict[str, str] = {
    # Client-accessible
    "chat.send": "client",
    "session.list": "client",   # results filtered by tenant_id in the DB query
    "session.read": "client",   # filtered by tenant_id
    "memory.read": "client",
    "memory.write": "client",
    # Admin
    "config.read": "tenant_admin",
    "agent.manage": "tenant_admin",
    # Operator-only
    "config.edit": "operator",
    "terminal.spawn": "operator",
    "pty.spawn": "operator",
    "tenant.manage": "operator",
}

_ROLE_ORDER = {"client": 0, "tenant_admin": 1, "operator": 2}


def authorize_method(method: str, role: str, tenant_id: str | None = None) -> bool:
    """Return True if ``role`` is allowed to call ``method``.

    Unknown methods default to operator-only (fail-closed); unknown roles get
    level -1 (deny everything).  ``tenant_id`` is accepted for symmetry with the
    call sites (row-level tenant filtering happens in the DB layer, not here).
    """
    required = _METHOD_POLICY.get(method, "operator")
    caller_level = _ROLE_ORDER.get(role, -1)
    required_level = _ROLE_ORDER.get(required, 99)
    return caller_level >= required_level
