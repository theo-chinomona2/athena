import pytest
from gateway.session import SessionSource, Platform
from gateway.tenancy import TenantConfig, TenantDef, MemberDef, TenantBinding, Role
from gateway.routing import resolve_identity_from_source


@pytest.fixture
def config():
    # WhatsApp bindings store the canonical (+ -stripped) phone number, matching
    # the canonicalisation build_session_key / _canonical_source_id apply.
    return TenantConfig(
        tenants=[TenantDef(id="theo", members=[MemberDef(id="theo", role="operator", default_agent="coding")])],
        bindings=[TenantBinding(source_id="27831234567", tenant="theo", member="theo", agent="coding")],
    )


def _wa_source(chat_id):
    return SessionSource(
        platform=Platform.WHATSAPP, chat_type="dm",
        chat_id=chat_id, user_id=None, user_id_alt=None, thread_id=None,
    )


def test_whatsapp_dm_resolves(config):
    identity = resolve_identity_from_source(_wa_source("+27831234567"), config)
    assert identity.tenant == "theo"
    assert identity.role == Role.OPERATOR


def test_unknown_source_returns_client(config):
    identity = resolve_identity_from_source(_wa_source("+27999999999"), config)
    assert identity.role == Role.CLIENT
