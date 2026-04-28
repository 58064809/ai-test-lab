from __future__ import annotations

from typing import Any, TypedDict

from ai_test_assistant.intent.models import IntentRouteResult
from ai_test_assistant.memory.models import MemoryRecord


class OrchestratorState(TypedDict, total=False):
    task_id: str
    task_text: str
    dry_run: bool
    write_memory: bool
    intent_result: IntentRouteResult
    loaded_memory: dict[str, list[MemoryRecord]]
    selected_workflow: str | None
    prepared_context: dict[str, Any]
    execution_plan: list[str]
    risk_level: str
    requires_confirmation: bool
    result: dict[str, Any]
    errors: list[str]
