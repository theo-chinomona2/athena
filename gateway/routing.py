"""Gateway routing: maps a SessionSource to a TenantIdentity via config bindings."""
from __future__ import annotations

from gateway.session import SessionSource, Platform
from gateway.tenancy import TenantConfig, TenantIdentity, resolve_identity


def _canonical_source_id(source: SessionSource) -> str:
    """Extract the stable identifier used as a binding key.

    For WhatsApp DMs, this is the canonical phone number (chat_id) — the same
    canonicalisation ``build_session_key`` applies, so bindings must store the
    canonical (``+``-stripped) form.  For other platforms, use chat_id if
    available, else user_id_alt, else user_id.
    """
    if source.platform == Platform.WHATSAPP and source.chat_id:
        from gateway.session import canonical_whatsapp_identifier
        return canonical_whatsapp_identifier(source.chat_id) or source.chat_id
    return source.chat_id or source.user_id_alt or source.user_id or ""


def resolve_identity_from_source(source: SessionSource, config: TenantConfig) -> TenantIdentity:
    """Resolve an inbound message source to a TenantIdentity via config bindings."""
    source_id = _canonical_source_id(source)
    return resolve_identity(source_id, config)


def agent_id_for_source(source: SessionSource, config: "TenantConfig | None") -> str:
    """Return the session-key agent_id (triple) for a source.

    Single source of truth shared by the gateway runner AND every platform
    adapter so all session-key sites agree (no split-brain busy-guard /
    interrupt / pending-queue state).  When tenancy is not configured (no
    tenants and no bindings) returns the legacy default ``"main.main.main"`` so
    single-tenant installs are unaffected.
    """
    if not config or (not config.tenants and not config.bindings):
        return "main.main.main"
    return resolve_identity_from_source(source, config).triple
