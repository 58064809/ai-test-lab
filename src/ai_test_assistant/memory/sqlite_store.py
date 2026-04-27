from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_test_assistant.memory.models import MemoryRecord, SUPPORTED_MEMORY_TYPES


class SQLiteMemoryStore:
    """SQLite-backed structured memory store.

    This store intentionally keeps retrieval simple:
    - exact lookup by namespace + key
    - text search over key and JSON payload

    Semantic search, embeddings, and vector indexes are not implemented in
    this first round.
    """

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def put_memory(
        self,
        namespace: str,
        key: str,
        value: Mapping[str, object],
        memory_type: str | None = None,
        source: str | None = None,
    ) -> MemoryRecord:
        namespace = self._validate_namespace(namespace)
        key = self._validate_key(key)
        resolved_type = self._resolve_memory_type(namespace, memory_type)
        payload = self._validate_value(value)
        now = self._now()
        created_at = now

        existing = self.get_memory(namespace, key)
        if existing is not None:
            created_at = existing.created_at

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO memories (
                    namespace, key, value_json, memory_type, created_at, updated_at, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(namespace, key) DO UPDATE SET
                    value_json=excluded.value_json,
                    memory_type=excluded.memory_type,
                    updated_at=excluded.updated_at,
                    source=excluded.source
                """,
                (
                    namespace,
                    key,
                    json.dumps(payload, ensure_ascii=False, sort_keys=True),
                    resolved_type,
                    created_at.isoformat(),
                    now.isoformat(),
                    source,
                ),
            )

        return self.get_memory(namespace, key)  # type: ignore[return-value]

    def get_memory(self, namespace: str, key: str) -> MemoryRecord | None:
        namespace = self._validate_namespace(namespace)
        key = self._validate_key(key)

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT namespace, key, value_json, memory_type, created_at, updated_at, source
                FROM memories
                WHERE namespace = ? AND key = ?
                """,
                (namespace, key),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_record(row)

    def search_memory(
        self,
        namespace: str,
        query: str | None = None,
        filters: Mapping[str, object] | None = None,
    ) -> list[MemoryRecord]:
        namespace = self._validate_namespace(namespace)
        filters = filters or {}
        clauses = ["namespace = ?"]
        params: list[object] = [namespace]

        if query:
            clauses.append("(key LIKE ? OR value_json LIKE ?)")
            pattern = f"%{query}%"
            params.extend([pattern, pattern])

        supported_filters = {"memory_type", "source"}
        unknown_filters = set(filters) - supported_filters
        if unknown_filters:
            raise ValueError(f"Unsupported memory filters: {sorted(unknown_filters)}")

        if "memory_type" in filters:
            clauses.append("memory_type = ?")
            params.append(str(filters["memory_type"]))

        if "source" in filters:
            clauses.append("source = ?")
            params.append(str(filters["source"]))

        sql = f"""
            SELECT namespace, key, value_json, memory_type, created_at, updated_at, source
            FROM memories
            WHERE {' AND '.join(clauses)}
            ORDER BY updated_at DESC, key ASC
        """

        with self._connect() as connection:
            rows = connection.execute(sql, params).fetchall()

        return [self._row_to_record(row) for row in rows]

    def delete_memory(self, namespace: str, key: str) -> bool:
        namespace = self._validate_namespace(namespace)
        key = self._validate_key(key)

        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM memories WHERE namespace = ? AND key = ?",
                (namespace, key),
            )

        return cursor.rowcount > 0

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    namespace TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    source TEXT,
                    PRIMARY KEY(namespace, key)
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_memories_namespace_updated
                ON memories(namespace, updated_at DESC)
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _row_to_record(self, row: sqlite3.Row) -> MemoryRecord:
        return MemoryRecord(
            namespace=row["namespace"],
            key=row["key"],
            value=json.loads(row["value_json"]),
            memory_type=row["memory_type"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            source=row["source"],
        )

    def _resolve_memory_type(self, namespace: str, memory_type: str | None) -> str:
        candidate = memory_type or namespace.split("/", 1)[0]
        if candidate not in SUPPORTED_MEMORY_TYPES:
            supported = ", ".join(SUPPORTED_MEMORY_TYPES)
            raise ValueError(f"Unsupported memory_type: {candidate}. Supported: {supported}")
        return candidate

    def _validate_namespace(self, namespace: str) -> str:
        namespace = namespace.strip()
        if not namespace:
            raise ValueError("Memory namespace must not be empty.")
        return namespace

    def _validate_key(self, key: str) -> str:
        key = key.strip()
        if not key:
            raise ValueError("Memory key must not be empty.")
        return key

    def _validate_value(self, value: Mapping[str, object]) -> dict[str, Any]:
        if not isinstance(value, Mapping):
            raise TypeError("Memory value must be a mapping that can be stored as JSON.")
        payload = dict(value)
        try:
            json.dumps(payload, ensure_ascii=False, sort_keys=True)
        except TypeError as exc:
            raise TypeError("Memory value must be JSON serializable.") from exc
        return payload

    def _now(self) -> datetime:
        return datetime.now(UTC)

