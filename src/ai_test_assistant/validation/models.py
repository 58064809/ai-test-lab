from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RealTaskSample:
    id: str
    category: str
    task_text: str
    expected_intent: str
    expected_clarification_required: bool
    expected_workflow: str | None
    expected_risk_level: str
    expected_recommended_tools: list[str] = field(default_factory=list)
    expected_tool_statuses: dict[str, str] = field(default_factory=dict)
    expected_tool_allowed: dict[str, bool] = field(default_factory=dict)
    notes: str = ""


@dataclass(slots=True)
class ValidationRunResult:
    sample_id: str
    passed: bool
    checks: dict[str, bool]
    actual_intent: str
    actual_clarification_required: bool
    actual_workflow: str | None
    actual_risk_level: str
    actual_recommended_tools: list[str]
    actual_tool_statuses: dict[str, str | None]
    actual_tool_allowed: dict[str, bool]
