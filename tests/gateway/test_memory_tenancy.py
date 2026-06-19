import pytest
import tempfile
from pathlib import Path
from tools.memory_tool import get_memory_dir, MemoryStore


def test_global_fallback():
    d = get_memory_dir()
    assert "memories" in str(d)


def test_per_identity_root():
    custom = Path("/tmp/hermes/tenants/theo/members/theo/agents/coding/memory")
    d = get_memory_dir(identity_root=custom)
    assert d == custom


def test_identity_root_does_not_contaminate_global():
    custom = Path("/tmp/t1/memory")
    d1 = get_memory_dir(identity_root=custom)
    d2 = get_memory_dir()  # global
    assert d1 != d2


def test_memory_store_writes_to_identity_root(tmp_path):
    root_a = tmp_path / "tenantA" / "memory"
    root_b = tmp_path / "tenantB" / "memory"
    store_a = MemoryStore(identity_root=root_a)
    store_b = MemoryStore(identity_root=root_b)
    store_a.load_from_disk()
    store_b.load_from_disk()
    store_a.memory_entries = ["tenant A secret"]
    store_a.save_to_disk("memory")
    # Tenant B's root must be untouched by tenant A's write.
    assert (root_a / "MEMORY.md").exists()
    assert not (root_b / "MEMORY.md").read_text().strip() if (root_b / "MEMORY.md").exists() else True
    # Tenant B re-reading sees nothing of tenant A's memory.
    store_b._reload_target("memory")
    assert "tenant A secret" not in store_b.memory_entries
