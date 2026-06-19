"""Per-tenant dashboard bearer-token registry.

Separate from the OAuth provider system in this package (``registry.py`` /
``routes.py`` / ``middleware.py``, which gate public binds via session cookies).
This is the loopback/desktop token path: a process-lifetime map from an opaque
bearer token to the tenant identity it authenticates.

The operator's loopback token is registered here at dashboard startup (tenant
``main``, role ``operator``) so the single-token loopback flow becomes one entry
in the same registry that issues per-tenant tokens. Tokens are in-memory only
(die with the process) — the same lifetime guarantee the ephemeral loopback
token always had.
"""
from __future__ import annotations

import secrets
import time
from typing import Optional

# token → {"tenant_id": str, "role": str, "expires": float}
_tokens: dict[str, dict] = {}


def issue_token(tenant_id: str, role: str, ttl_s: int = 86400, token: Optional[str] = None) -> str:
    """Mint (or register a caller-supplied) bearer token for an identity.

    ``token`` lets the dashboard register a pre-existing value (e.g. the operator
    token injected via ``HERMES_DASHBOARD_SESSION_TOKEN``) so external processes
    that already hold it keep authenticating.
    """
    tok = token or secrets.token_urlsafe(32)
    _tokens[tok] = {
        "tenant_id": tenant_id,
        "role": role,
        "expires": time.time() + ttl_s,
    }
    return tok


def verify_token(token: str) -> Optional[dict]:
    """Return the identity ``{tenant_id, role, expires}`` for a valid token, else None.

    Expired tokens are evicted on access.
    """
    if not token:
        return None
    entry = _tokens.get(token)
    if entry is None:
        return None
    if time.time() > entry["expires"]:
        _tokens.pop(token, None)
        return None
    return entry


def revoke_token(token: str) -> None:
    """Drop a token from the registry (logout / rotation)."""
    _tokens.pop(token, None)
