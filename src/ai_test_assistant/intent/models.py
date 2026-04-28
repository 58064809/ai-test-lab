from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class IntentRule:
    name: str
    description: str
    triggers: list[str]
    negative_triggers: list[str]
    required_context: list[str]
    optional_context: list[str]
    recommended_workflow: str
    default_prompt: str


@dataclass(slots=True)
class IntentRouteResult:
    intent: str
    confidence: float
    matched_rules: list[str] = field(default_factory=list)
    required_context: list[str] = field(default_factory=list)
    recommended_workflow: str | None = None
    clarification_required: bool = False
    clarification_questions: list[str] = field(default_factory=list)

