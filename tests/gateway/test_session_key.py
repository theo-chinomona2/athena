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
    assert key.startswith("agent:main.main.main:")


def test_triple_in_key():
    key = build_session_key(_dm_source(), agent_id="theo.theo.coding")
    # canonical_whatsapp_identifier strips the leading "+".
    assert key == "agent:theo.theo.coding:whatsapp:dm:27831234567"


def test_legacy_main_still_works():
    # Old callers that pass no agent_id get main.main.main (was "main").
    key = build_session_key(_dm_source(), agent_id="main.main.main")
    assert "main.main.main" in key


def test_different_agents_different_keys():
    s = _dm_source()
    k1 = build_session_key(s, agent_id="theo.theo.coding")
    k2 = build_session_key(s, agent_id="dad.dad.news")
    assert k1 != k2
