from __future__ import annotations

from dataclasses import replace

import pytest

from ai_test_assistant.tool_registry.models import ToolRiskLevel, ToolStatus
from ai_test_assistant.tool_registry.permissions import ToolPermissionContext
from ai_test_assistant.tool_registry.registry import ToolRegistry


def test_registry_loads_first_batch_tools() -> None:
    registry = ToolRegistry.from_yaml("configs/tools.yaml")

    names = {tool.name for tool in registry.list_tools()}
    assert names == {
        "memory_read",
        "memory_write",
        "intent_router",
        "pytest_runner",
        "allure_report",
        "playwright_mcp",
        "playwright_browser",
        "schemathesis",
        "keploy",
        "github",
        "github_read",
        "github_write",
        "filesystem",
        "filesystem_read",
        "filesystem_mcp_read",
        "filesystem_write",
        "shell",
        "database_readonly",
        "redis_readonly",
    }


def test_registry_exposes_status_and_risk_level() -> None:
    registry = ToolRegistry.from_yaml("configs/tools.yaml")

    memory_read_tool = registry.get_tool("memory_read")
    assert memory_read_tool.status is ToolStatus.ENABLED
    assert memory_read_tool.risk_level is ToolRiskLevel.READ_ONLY

    memory_write_tool = registry.get_tool("memory_write")
    assert memory_write_tool.status is ToolStatus.DISABLED
    assert memory_write_tool.risk_level is ToolRiskLevel.RESTRICTED_ACTION

    filesystem_read_tool = registry.get_tool("filesystem_read")
    assert filesystem_read_tool.status is ToolStatus.ENABLED
    assert filesystem_read_tool.risk_level is ToolRiskLevel.READ_ONLY

    pytest_runner_tool = registry.get_tool("pytest_runner")
    assert pytest_runner_tool.status is ToolStatus.ENABLED
    assert pytest_runner_tool.risk_level is ToolRiskLevel.EXECUTE_LOCAL_COMMAND

    filesystem_mcp_read_tool = registry.get_tool("filesystem_mcp_read")
    assert filesystem_mcp_read_tool.status is ToolStatus.ENABLED
    assert filesystem_mcp_read_tool.risk_level is ToolRiskLevel.READ_ONLY

    github_read_tool = registry.get_tool("github_read")
    assert github_read_tool.status is ToolStatus.ENABLED
    assert github_read_tool.risk_level is ToolRiskLevel.EXTERNAL_NETWORK

    shell_tool = registry.get_tool("shell")
    assert shell_tool.status is ToolStatus.DISABLED
    assert shell_tool.risk_level is ToolRiskLevel.EXECUTE_LOCAL_COMMAND

    filesystem_write_tool = registry.get_tool("filesystem_write")
    assert filesystem_write_tool.status is ToolStatus.DISABLED
    assert filesystem_write_tool.risk_level is ToolRiskLevel.WRITE_PROJECT_FILES


def test_enabled_read_only_tool_is_allowed_by_default() -> None:
    registry = ToolRegistry.from_yaml("configs/tools.yaml")

    decision = registry.evaluate_execution("filesystem_read")
    mcp_decision = registry.evaluate_execution("filesystem_mcp_read")

    assert decision.allowed is True
    assert decision.requires_confirmation is False
    assert decision.reasons == []
    assert mcp_decision.allowed is True
    assert mcp_decision.requires_confirmation is False
    assert mcp_decision.reasons == []


@pytest.mark.parametrize("tool_name", ["pytest_runner", "playwright_mcp", "keploy", "shell", "database_readonly"])
def test_non_enabled_tools_are_not_executable(tool_name: str) -> None:
    registry = ToolRegistry.from_yaml("configs/tools.yaml")

    decision = registry.evaluate_execution(tool_name)

    if tool_name == "pytest_runner":
        assert decision.allowed is False
        assert any("dry-run" in reason for reason in decision.reasons)
        return

    assert decision.allowed is False
    assert any("not enabled" in reason for reason in decision.reasons)


def test_memory_write_is_denied_by_default_even_before_real_execution_exists() -> None:
    registry = ToolRegistry.from_yaml("configs/tools.yaml")

    decision = registry.evaluate_execution("memory_write")

    assert decision.allowed is False
    assert any("not enabled" in reason for reason in decision.reasons)


def test_write_project_files_requires_explicit_approval() -> None:
    registry = ToolRegistry.from_yaml("configs/tools.yaml")

    tool = registry.get_tool("filesystem")
    enabled_tool = replace(tool, status=ToolStatus.ENABLED)
    registry = ToolRegistry({"filesystem": enabled_tool})

    denied = registry.evaluate_execution("filesystem")
    assert denied.allowed is False
    assert denied.requires_confirmation is True

    allowed = registry.evaluate_execution(
        "filesystem",
        ToolPermissionContext(allow_write_project_files=True),
    )
    assert allowed.allowed is True


def test_execute_local_command_is_denied_in_dry_run_even_if_enabled() -> None:
    registry = ToolRegistry.from_yaml("configs/tools.yaml")
    tool = registry.get_tool("shell")
    enabled_tool = replace(tool, status=ToolStatus.ENABLED)
    registry = ToolRegistry({"shell": enabled_tool})

    dry_run_decision = registry.evaluate_execution("shell", ToolPermissionContext(dry_run=True))
    assert dry_run_decision.allowed is False
    assert any("dry-run" in reason for reason in dry_run_decision.reasons)


def test_execute_local_command_requires_explicit_approval_outside_dry_run() -> None:
    registry = ToolRegistry.from_yaml("configs/tools.yaml")
    tool = registry.get_tool("shell")
    enabled_tool = replace(tool, status=ToolStatus.ENABLED)
    registry = ToolRegistry({"shell": enabled_tool})

    denied = registry.evaluate_execution("shell", ToolPermissionContext(dry_run=False))
    assert denied.allowed is False
    assert denied.requires_confirmation is True

    allowed = registry.evaluate_execution(
        "shell",
        ToolPermissionContext(dry_run=False, allow_execute_local_command=True),
    )
    assert allowed.allowed is True


def test_external_network_requires_confirmation_even_if_enabled() -> None:
    registry = ToolRegistry.from_yaml("configs/tools.yaml")
    tool = registry.get_tool("github_read")
    registry = ToolRegistry({"github_read": tool})

    denied = registry.evaluate_execution("github_read")
    assert denied.allowed is False
    assert denied.requires_confirmation is True

    allowed = registry.evaluate_execution(
        "github_read",
        ToolPermissionContext(allow_external_network=True),
    )
    assert allowed.allowed is True


def test_restricted_action_is_denied_by_default() -> None:
    registry = ToolRegistry.from_yaml("configs/tools.yaml")
    tool = registry.get_tool("keploy")
    enabled_tool = replace(tool, status=ToolStatus.ENABLED)
    registry = ToolRegistry({"keploy": enabled_tool})

    denied = registry.evaluate_execution("keploy")
    assert denied.allowed is False
    assert denied.requires_confirmation is False
    assert any("restricted_action" in reason for reason in denied.reasons)

    elevated = registry.evaluate_execution(
        "keploy",
        ToolPermissionContext(allow_restricted_action=True),
    )
    assert elevated.allowed is True
    assert elevated.requires_confirmation is True


def test_registry_rejects_duplicate_tool_names(tmp_path) -> None:
    config_path = tmp_path / "tools.yaml"
    config_path.write_text(
        "\n".join(
            [
                "tools:",
                "  - name: duplicate_tool",
                "    description: first",
                "    status: enabled",
                "    risk_level: read_only",
                "    category: internal",
                "    implementation: local_python",
                "  - name: duplicate_tool",
                "    description: second",
                "    status: planned",
                "    risk_level: external_network",
                "    category: scm",
                "    implementation: planned_mcp",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate tool name found"):
        ToolRegistry.from_yaml(config_path)
