from __future__ import annotations

from pathlib import Path

import yaml

from ai_test_assistant.tool_registry.models import (
    ToolDefinition,
    ToolRiskLevel,
    ToolStatus,
)
from ai_test_assistant.tool_registry.permissions import ToolExecutionDecision, ToolPermissionContext, ToolPermissionEvaluator


class ToolRegistry:
    """Loads and exposes tool metadata and permission decisions."""

    REQUIRED_FIELDS = {
        "name",
        "description",
        "status",
        "risk_level",
        "category",
        "implementation",
    }

    def __init__(self, tools: dict[str, ToolDefinition], evaluator: ToolPermissionEvaluator | None = None) -> None:
        self._tools = tools
        self._evaluator = evaluator or ToolPermissionEvaluator()

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> "ToolRegistry":
        path = Path(config_path)
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        tool_items = data.get("tools", [])
        tools: dict[str, ToolDefinition] = {}

        for item in tool_items:
            tool = cls._build_tool(item)
            if tool.name in tools:
                raise ValueError(f"Duplicate tool name found: {tool.name}")
            tools[tool.name] = tool

        return cls(tools)

    def list_tools(self) -> list[ToolDefinition]:
        return sorted(self._tools.values(), key=lambda item: item.name)

    def get_tool(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Tool '{name}' is not registered.") from exc

    def evaluate_execution(
        self,
        name: str,
        context: ToolPermissionContext | None = None,
    ) -> ToolExecutionDecision:
        tool = self.get_tool(name)
        return self._evaluator.evaluate(tool, context=context)

    @classmethod
    def _build_tool(cls, item: dict[str, object]) -> ToolDefinition:
        missing = sorted(cls.REQUIRED_FIELDS - set(item))
        if missing:
            raise ValueError(f"Tool definition missing required fields: {missing}")

        status = ToolStatus(str(item["status"]))
        risk_level = ToolRiskLevel(str(item["risk_level"]))
        return ToolDefinition(
            name=str(item["name"]),
            description=str(item["description"]),
            status=status,
            risk_level=risk_level,
            category=str(item["category"]),
            implementation=str(item["implementation"]),
            notes=str(item.get("notes", "")),
        )

