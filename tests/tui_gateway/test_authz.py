"""Desktop/dashboard tenancy authz: method-level policy + per-tenant token auth."""
import time

from tui_gateway.authz import authorize_method
from hermes_cli.dashboard_auth import tenant_tokens as dashboard_auth


# ── Task 16: method-level role policy ────────────────────────────────────────

def test_client_allowed_own_session_methods():
    assert authorize_method("session.list", role="client", tenant_id="dad") is True
    assert authorize_method("session.read", role="client", tenant_id="dad") is True
    assert authorize_method("chat.send", role="client", tenant_id="dad") is True


def test_client_denied_admin_and_operator_methods():
    assert authorize_method("config.edit", role="client", tenant_id="dad") is False
    assert authorize_method("config.read", role="client", tenant_id="dad") is False
    assert authorize_method("tenant.manage", role="client", tenant_id="dad") is False


def test_pty_and_terminal_operator_only():
    for role in ("client", "tenant_admin"):
        assert authorize_method("pty.spawn", role=role, tenant_id="dad") is False
        assert authorize_method("terminal.spawn", role=role, tenant_id="dad") is False
    assert authorize_method("pty.spawn", role="operator", tenant_id="theo") is True
    assert authorize_method("terminal.spawn", role="operator", tenant_id="theo") is True


def test_tenant_admin_between_client_and_operator():
    assert authorize_method("config.read", role="tenant_admin", tenant_id="dad") is True
    assert authorize_method("config.edit", role="tenant_admin", tenant_id="dad") is False


def test_unknown_method_fails_closed_operator_only():
    assert authorize_method("secret.new_method", role="client", tenant_id="dad") is False
    assert authorize_method("secret.new_method", role="tenant_admin", tenant_id="dad") is False
    assert authorize_method("secret.new_method", role="operator", tenant_id="theo") is True


def test_unknown_role_denied_everything():
    assert authorize_method("chat.send", role="superadmin", tenant_id="x") is False
    assert authorize_method("session.list", role="", tenant_id="x") is False


# ── Task 15: per-tenant dashboard token registry (behavior contract) ─────────
# (Replaces the plan's change-detector `_SESSION_TOKEN =` literal-count assertion
#  with the real security contract: tokens resolve to the right identity, and a
#  tenant token can never present as another tenant / the operator.)

def test_issued_token_verifies_to_its_identity():
    tok = dashboard_auth.issue_token("dad", "client")
    ident = dashboard_auth.verify_token(tok)
    assert ident is not None
    assert ident["tenant_id"] == "dad"
    assert ident["role"] == "client"


def test_tenant_token_is_not_operator():
    tok = dashboard_auth.issue_token("dad", "client")
    ident = dashboard_auth.verify_token(tok)
    assert ident["role"] != "operator"
    assert ident["tenant_id"] != "main"


def test_distinct_tenants_get_distinct_tokens_and_identities():
    t1 = dashboard_auth.issue_token("dad", "client")
    t2 = dashboard_auth.issue_token("theo", "operator")
    assert t1 != t2
    assert dashboard_auth.verify_token(t1)["tenant_id"] == "dad"
    assert dashboard_auth.verify_token(t2)["tenant_id"] == "theo"


def test_unknown_and_empty_tokens_rejected():
    assert dashboard_auth.verify_token("nope-not-a-token") is None
    assert dashboard_auth.verify_token("") is None


def test_expired_token_rejected_and_evicted():
    tok = dashboard_auth.issue_token("dad", "client", ttl_s=-1)
    assert dashboard_auth.verify_token(tok) is None


def test_revoked_token_rejected():
    tok = dashboard_auth.issue_token("dad", "client")
    assert dashboard_auth.verify_token(tok) is not None
    dashboard_auth.revoke_token(tok)
    assert dashboard_auth.verify_token(tok) is None


def test_caller_supplied_token_registers_verbatim():
    dashboard_auth.issue_token("main", "operator", token="operator-loopback-xyz")
    ident = dashboard_auth.verify_token("operator-loopback-xyz")
    assert ident["tenant_id"] == "main"
    assert ident["role"] == "operator"
