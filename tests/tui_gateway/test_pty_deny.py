"""PTY role gate: only the operator may reach the raw host shell.

Task 17 of the multi-tenant gateway plan. The host PTY is a raw shell;
tenant roles must be denied until v3 per-tenant Docker sandboxing exists.
"""

import pytest

from hermes_cli.pty_bridge import PtyBridge


def test_pty_denied_for_client():
    with pytest.raises(PermissionError, match="PTY access denied"):
        PtyBridge.spawn(["/bin/sh"], role="client")


def test_pty_denied_for_tenant_admin():
    with pytest.raises(PermissionError, match="PTY access denied"):
        PtyBridge.spawn(["/bin/sh"], role="tenant_admin")


def test_pty_allowed_for_operator(monkeypatch):
    # Don't actually fork a shell in tests — replace the real ``ptyprocess``
    # module reference that ``PtyBridge.spawn`` calls into.  ``PtyBridge.__init__``
    # reads ``proc.fd``, so the fake process must expose it.
    import hermes_cli.pty_bridge as pb

    class FakeProc:
        pid = 1234
        fd = 5

        def __init__(self, *args, **kwargs):
            pass

    class FakePtyProcess:
        @classmethod
        def spawn(cls, *args, **kwargs):
            return FakeProc()

    class FakeModule:
        PtyProcess = FakePtyProcess

    # Force availability on so the gate is exercised regardless of host setup.
    monkeypatch.setattr(pb, "_PTY_AVAILABLE", True)
    monkeypatch.setattr(pb, "ptyprocess", FakeModule)

    bridge = PtyBridge.spawn(["/bin/sh"], role="operator")
    assert bridge is not None
    assert bridge.pid == 1234
