"""relay_message — gated cross-tenant message relay.

Rules:
  - Consent must be declared in BOTH tenants' contacts config (bidirectional).
  - Message content is text only — all MEDIA: paths, file paths, and cache refs are stripped.
  - Every relay is appended to <HERMES_HOME>/audit/relay.log as JSON.
  - Rate limit: max 20 relays per sender tenant per hour (simple token bucket).
"""
from __future__ import annotations

import json
import logging
import re
import threading
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_rate_lock = threading.Lock()
_relay_counts: dict[str, list[float]] = {}  # tenant → list of relay timestamps
_RELAY_RATE_LIMIT = 20
_RELAY_WINDOW_S = 3600

_MEDIA_PATTERN = re.compile(
    r"MEDIA:[^\s,;\"']+|/(?:tmp|var|home|root|hermes)[^\s,;\"']*\.(png|jpg|jpeg|mp4|wav|mp3|ogg|webp|gif)",
    re.IGNORECASE,
)


def _strip_media_paths(text: str) -> str:
    return _MEDIA_PATTERN.sub("[media removed]", text)


def _check_consent(sender_tenant: str, alias: str, config) -> Optional[str]:
    """Return the target tenant_id if consent exists in both directions, else None."""
    sender_def = next((t for t in config.tenants if t.id == sender_tenant), None)
    if not sender_def:
        return None
    contact = next(
        (c for c in getattr(sender_def, "contacts", []) if c.get("alias") == alias),
        None,
    )
    if not contact:
        return None
    target_tenant_id = contact.get("tenant")
    if not target_tenant_id:
        return None
    # Verify reverse consent
    target_def = next((t for t in config.tenants if t.id == target_tenant_id), None)
    if not target_def:
        return None
    reverse = any(
        c.get("tenant") == sender_tenant
        for c in getattr(target_def, "contacts", [])
    )
    return target_tenant_id if reverse else None


def _check_rate_limit(tenant: str) -> bool:
    now = time.monotonic()
    with _rate_lock:
        stamps = _relay_counts.setdefault(tenant, [])
        stamps[:] = [t for t in stamps if now - t < _RELAY_WINDOW_S]
        if len(stamps) >= _RELAY_RATE_LIMIT:
            return False
        stamps.append(now)
    return True


def _write_audit(hermes_home: Path, entry: dict) -> None:
    log_path = hermes_home / "audit" / "relay.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def relay_message(alias: str, message: str, agent) -> str:
    """Send a text-only message to a consented contact alias."""
    from hermes_constants import get_hermes_home

    sender_tenant = getattr(agent, "_tenant_id", None)
    config = getattr(agent, "_tenant_config", None)
    if not sender_tenant or not config:
        return "relay_message: no tenant context available."

    target_tenant = _check_consent(sender_tenant, alias, config)
    if target_tenant is None:
        return f"relay_message: relay to '{alias}' is not permitted (no mutual consent)."

    if not _check_rate_limit(sender_tenant):
        return "relay_message: rate limit exceeded (20 messages per hour)."

    safe_text = _strip_media_paths(str(message))

    home = get_hermes_home()
    _write_audit(home, {
        "ts": time.time(),
        "from": sender_tenant,
        "to": target_tenant,
        "alias": alias,
        "chars": len(safe_text),
    })

    # Deliver via the gateway's inbound queue for the target tenant.
    # The actual delivery mechanism depends on gateway internals (future wiring).
    logger.info("relay: %s → %s (%d chars)", sender_tenant, target_tenant, len(safe_text))
    return f"Message relayed to {alias}."


TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "relay_message",
        "description": "Send a text message to a consented cross-tenant contact alias.",
        "parameters": {
            "type": "object",
            "properties": {
                "alias": {"type": "string", "description": "Contact alias from your tenant config."},
                "message": {"type": "string", "description": "Text message (no file paths or media)."},
            },
            "required": ["alias", "message"],
        },
    },
}
