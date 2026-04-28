from __future__ import annotations

from ai_test_assistant.intent.router import IntentRouter
from ai_test_assistant.orchestrator import TaskOrchestrator
from ai_test_assistant.validation.models import RealTaskSample, ValidationRunResult


class RealTaskValidationRunner:
    """Run dry-run validation against real task samples without executing tools."""

    def __init__(self, intent_router: IntentRouter, orchestrator: TaskOrchestrator) -> None:
        self.intent_router = intent_router
        self.orchestrator = orchestrator

    def run_sample(self, sample: RealTaskSample) -> ValidationRunResult:
        intent_result = self.intent_router.route(sample.task_text)
        state = self.orchestrator.run(sample.task_text, dry_run=True, write_memory=False)

        tool_statuses = {
            str(decision["tool_name"]): decision.get("status")
            for decision in state.get("tool_decisions", [])
        }
        tool_allowed = {
            str(decision["tool_name"]): bool(decision.get("allowed", False))
            for decision in state.get("tool_decisions", [])
        }

        checks: dict[str, bool] = {
            "intent": intent_result.intent == sample.expected_intent and state["intent_result"].intent == sample.expected_intent,
            "clarification_required": state["intent_result"].clarification_required == sample.expected_clarification_required,
            "workflow": state.get("selected_workflow") == sample.expected_workflow,
            "risk_level": state.get("risk_level") == sample.expected_risk_level,
            "recommended_tools": list(state.get("recommended_tools", [])) == list(sample.expected_recommended_tools),
            "dry_run": state.get("dry_run", False) is True,
        }

        for tool_name, expected_status in sample.expected_tool_statuses.items():
            checks[f"tool_status:{tool_name}"] = tool_statuses.get(tool_name) == expected_status

        for tool_name, expected_allowed in sample.expected_tool_allowed.items():
            checks[f"tool_allowed:{tool_name}"] = tool_allowed.get(tool_name) == expected_allowed

        return ValidationRunResult(
            sample_id=sample.id,
            passed=all(checks.values()),
            checks=checks,
            actual_intent=state["intent_result"].intent,
            actual_clarification_required=state["intent_result"].clarification_required,
            actual_workflow=state.get("selected_workflow"),
            actual_risk_level=str(state.get("risk_level")),
            actual_recommended_tools=list(state.get("recommended_tools", [])),
            actual_tool_statuses=tool_statuses,
            actual_tool_allowed=tool_allowed,
        )

    def run_all(self, samples: list[RealTaskSample]) -> list[ValidationRunResult]:
        return [self.run_sample(sample) for sample in samples]
