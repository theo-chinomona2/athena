import pytest
from gateway.session import build_session_key, SessionSource, Platform


def _dm_source(platform=Platform.WHATSAPP, chat_id="+27831234567"):
    return SessionSource(
        platform=platform,
        chat_type="dm",
        chat_id=chat_id,
        user_id=None,
        user_id_alt=None,
        thread_id=None,
    )


def test_backward_compat_default():
    key = build_session_key(_dm_source())
    assert key.startswith("agent:main:")


def test_triple_in_key():
    key = build_session_key(_dm_source(), agent_id="theo.theo.coding")
    # canonical_whatsapp_identifier strips the leading "+".
    assert key == "agent:theo.theo.coding:whatsapp:dm:27831234567"


def test_legacy_main_still_works():
    # The default tenant triple collapses to the legacy single-tenant namespace.
    key = build_session_key(_dm_source(), agent_id="main.main.main")
    assert key.startswith("agent:main:")


def test_different_agents_different_keys():
    s = _dm_source()
    k1 = build_session_key(s, agent_id="theo.theo.coding")
    k2 = build_session_key(s, agent_id="dad.dad.news")
    assert k1 != k2


def test_named_profile_and_tenant_both_isolate_namespace():
    key = build_session_key(
        _dm_source(), agent_id="theo.theo.coding", profile="work"
    )
    assert key == "agent:work.theo.theo.coding:whatsapp:dm:27831234567"
