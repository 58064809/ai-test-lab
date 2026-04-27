from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from ai_test_assistant.memory.models import MemoryRecord
from ai_test_assistant.memory.sqlite_store import SQLiteMemoryStore
from ai_test_assistant.memory.store import MemoryStore


class MemoryService:
    """Thin service layer for future orchestrator and intent integration."""

    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    @classmethod
    def from_config(cls, config_path: str | Path = "configs/assistant.yaml") -> "MemoryService":
        config_file = Path(config_path)
        config_data = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
        memory_config = config_data.get("memory", {})
        backend = memory_config.get("backend", "sqlite")

        if backend != "sqlite":
            raise ValueError(f"Unsupported memory backend: {backend}. Only sqlite is implemented.")

        sqlite_path = memory_config.get("sqlite_path", ".assistant/memory.sqlite3")
        return cls(SQLiteMemoryStore(sqlite_path))

    def put_memory(
        self,
        namespace: str,
        key: str,
        value: Mapping[str, object],
        memory_type: str | None = None,
        source: str | None = None,
    ) -> MemoryRecord:
        return self.store.put_memory(namespace, key, value, memory_type=memory_type, source=source)

    def get_memory(self, namespace: str, key: str) -> MemoryRecord | None:
        return self.store.get_memory(namespace, key)

    def search_memory(
        self,
        namespace: str,
        query: str | None = None,
        filters: Mapping[str, Any] | None = None,
    ) -> list[MemoryRecord]:
        return self.store.search_memory(namespace, query=query, filters=filters)

    def delete_memory(self, namespace: str, key: str) -> bool:
        return self.store.delete_memory(namespace, key)

