import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import hermes_constants


def test_relay_strips_media_paths():
    from tools.relay_tool import _strip_media_paths
    msg = "Hello! MEDIA:/hermes/cache/image.png Check this out."
    stripped = _strip_media_paths(msg)
    assert "MEDIA:" not in stripped
    assert "/hermes/cache/image.png" not in stripped


def test_relay_denied_without_consent():
    from tools.relay_tool import relay_message
    agent = MagicMock()
    agent._tenant_id = "theo"
    agent._tenant_config = MagicMock()
    agent._tenant_config.tenants = []  # no contacts defined → no consent
    result = relay_message("girlfriend", "hello", agent)
    assert "not permitted" in result.lower() or "no consent" in result.lower()


def test_relay_audit_logged(tmp_path, monkeypatch):
    from tools import relay_tool

    monkeypatch.setattr(hermes_constants, "get_hermes_home", lambda: tmp_path)
    # Reset the module-global rate-limit bucket so prior tests can't leak in.
    relay_tool._relay_counts.clear()

    agent = MagicMock()
    agent._tenant_id = "theo"
    # Bidirectional mutual consent: theo↔girlfriend.
    agent._tenant_config = SimpleNamespace(
        tenants=[
            SimpleNamespace(id="theo", contacts=[{"alias": "gf", "tenant": "girlfriend"}]),
            SimpleNamespace(id="girlfriend", contacts=[{"alias": "theo", "tenant": "theo"}]),
        ]
    )

    raw = "hello MEDIA:/tmp/x.png"
    result = relay_tool.relay_message("gf", raw, agent)
    assert "relayed" in result.lower()

    log_path = tmp_path / "audit" / "relay.log"
    assert log_path.exists()
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["from"] == "theo"
    assert entry["to"] == "girlfriend"
    assert entry["alias"] == "gf"
    # Audited length reflects the media-stripped text, not the raw message.
    assert entry["chars"] == len(relay_tool._strip_media_paths(raw))
    assert entry["chars"] != len(raw)
