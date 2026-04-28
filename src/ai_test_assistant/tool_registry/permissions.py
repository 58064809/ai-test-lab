from __future__ import annotations

from dataclasses import dataclass

from ai_test_assistant.tool_registry.models import (
    ToolDefinition,
    ToolExecutionDecision,
    ToolRiskLevel,
    ToolStatus,
)


@dataclass(slots=True)
class ToolPermissionContext:
    dry_run: bool = True
    allow_write_project_files: bool = False
    allow_execute_local_command: bool = False
    allow_external_network: bool = False
    allow_restricted_action: bool = False


class ToolPermissionEvaluator:
    """Evaluates whether a registered tool may be used under current policy."""

    def evaluate(self, tool: ToolDefinition, context: ToolPermissionContext | None = None) -> ToolExecutionDecision:
        context = context or ToolPermissionContext()

        if tool.status is not ToolStatus.ENABLED:
            return ToolExecutionDecision(
                allowed=False,
                reasons=[f"Tool '{tool.name}' is not enabled. Current status: {tool.status.value}."],
            )

        if tool.risk_level is ToolRiskLevel.READ_ONLY:
            return ToolExecutionDecision(allowed=True)

        if tool.risk_level is ToolRiskLevel.WRITE_PROJECT_FILES:
            if context.allow_write_project_files:
                return ToolExecutionDecision(allowed=True)
            return ToolExecutionDecision(
                allowed=False,
                requires_confirmation=True,
                reasons=[f"Tool '{tool.name}' writes project files and needs explicit approval."],
            )

        if tool.risk_level is ToolRiskLevel.EXECUTE_LOCAL_COMMAND:
            if context.dry_run:
                return ToolExecutionDecision(
                    allowed=False,
                    reasons=[f"Tool '{tool.name}' cannot run local commands during dry-run."],
                )
            if context.allow_execute_local_command:
                return ToolExecutionDecision(allowed=True)
            return ToolExecutionDecision(
                allowed=False,
                requires_confirmation=True,
                reasons=[f"Tool '{tool.name}' executes local commands and needs explicit approval."],
            )

        if tool.risk_level is ToolRiskLevel.EXTERNAL_NETWORK:
            if context.allow_external_network:
                return ToolExecutionDecision(allowed=True)
            return ToolExecutionDecision(
                allowed=False,
                requires_confirmation=True,
                reasons=[f"Tool '{tool.name}' needs external network approval."],
            )

        if tool.risk_level is ToolRiskLevel.RESTRICTED_ACTION:
            if context.allow_restricted_action:
                return ToolExecutionDecision(
                    allowed=True,
                    requires_confirmation=True,
                    reasons=[f"Tool '{tool.name}' is restricted and should be used only with elevated approval."],
                )
            return ToolExecutionDecision(
                allowed=False,
                reasons=[f"Tool '{tool.name}' is restricted_action and is denied by default."],
            )

        return ToolExecutionDecision(
            allowed=False,
            reasons=[f"Unknown risk level for tool '{tool.name}'."],
        )

