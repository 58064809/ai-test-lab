from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

MemoryType = Literal[
    "project_rule",
    "user_preference",
    "workflow_memory",
    "task_result",
    "tool_capability",
]

SUPPORTED_MEMORY_TYPES: tuple[str, ...] = (
    "project_rule",
    "user_preference",
    "workflow_memory",
    "task_result",
    "tool_capability",
)


@dataclass(slots=True)
class MemoryRecord:
    namespace: str
    key: str
    value: dict[str, Any]
    memory_type: str
    created_at: datetime
    updated_at: datetime
    source: str | None = None

