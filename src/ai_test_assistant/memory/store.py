from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from ai_test_assistant.memory.models import MemoryRecord


class MemoryStore(Protocol):
    """Store contract compatible with future orchestrator and intent layers."""

    def put_memory(
        self,
        namespace: str,
        key: str,
        value: Mapping[str, object],
        memory_type: str | None = None,
        source: str | None = None,
    ) -> MemoryRecord: ...

    def get_memory(self, namespace: str, key: str) -> MemoryRecord | None: ...

    def search_memory(
        self,
        namespace: str,
        query: str | None = None,
        filters: Mapping[str, object] | None = None,
    ) -> list[MemoryRecord]: ...

    def delete_memory(self, namespace: str, key: str) -> bool: ...

