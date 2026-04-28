from __future__ import annotations

from pathlib import Path

import yaml

from ai_test_assistant.validation.models import RealTaskSample


class RealTaskSampleLoader:
    """Load real-task dry-run validation samples from YAML."""

    @staticmethod
    def load(path: str | Path = "validation/real-task-samples.yaml") -> list[RealTaskSample]:
        file_path = Path(path)
        data = yaml.safe_load(file_path.read_text(encoding="utf-8")) or {}
        items = data.get("samples", [])
        samples: list[RealTaskSample] = []
        for item in items:
            samples.append(
                RealTaskSample(
                    id=str(item["id"]),
                    category=str(item["category"]),
                    task_text=str(item["task_text"]),
                    expected_intent=str(item["expected_intent"]),
                    expected_clarification_required=bool(item["expected_clarification_required"]),
                    expected_workflow=item.get("expected_workflow"),
                    expected_risk_level=str(item["expected_risk_level"]),
                    expected_recommended_tools=[str(tool_name) for tool_name in item.get("expected_recommended_tools", [])],
                    expected_tool_statuses={
                        str(tool_name): str(status)
                        for tool_name, status in (item.get("expected_tool_statuses", {}) or {}).items()
                    },
                    expected_tool_allowed={
                        str(tool_name): bool(allowed)
                        for tool_name, allowed in (item.get("expected_tool_allowed", {}) or {}).items()
                    },
                    notes=str(item.get("notes", "")),
                )
            )
        return samples
