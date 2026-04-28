from __future__ import annotations

from ai_test_assistant.intent.models import IntentRouteResult


HIGH_RISK_INTENTS = {
    "repo_file_change",
    "pytest_execution",
    "memory_update",
}

MEDIUM_RISK_INTENTS = {
    "api_test_design",
    "ui_test_design",
    "tool_research",
    "workflow_update",
}


def determine_risk_level(intent_result: IntentRouteResult, dry_run: bool) -> str:
    if dry_run:
        if intent_result.intent in HIGH_RISK_INTENTS:
            return "medium"
        if intent_result.intent in MEDIUM_RISK_INTENTS:
            return "medium"
        return "low"

    if intent_result.intent in HIGH_RISK_INTENTS:
        return "high"
    if intent_result.intent in MEDIUM_RISK_INTENTS:
        return "medium"
    return "low"


def requires_confirmation(intent_result: IntentRouteResult, dry_run: bool) -> bool:
    if intent_result.clarification_required:
        return True
    if not dry_run and intent_result.intent in HIGH_RISK_INTENTS:
        return True
    return False

