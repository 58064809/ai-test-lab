from __future__ import annotations

from pathlib import Path

from ai_test_assistant.orchestrator.graph import TaskOrchestrator


def _write_assistant_config(tmp_path: Path) -> Path:
    memory_db_path = (tmp_path / "memory.sqlite3").resolve()
    intents_path = Path("configs/intents.yaml").resolve()
    tools_path = Path("configs/tools.yaml").resolve()
    assistant_config = tmp_path / "assistant.yaml"
    assistant_config.write_text(
        "\n".join(
            [
                "memory:",
                "  backend: sqlite",
                f"  sqlite_path: {memory_db_path.as_posix()}",
                "intent:",
                f"  rules_path: {intents_path.as_posix()}",
                "tool_registry:",
                f"  config_path: {tools_path.as_posix()}",
            ]
        ),
        encoding="utf-8",
    )
    return assistant_config


def test_orchestrator_dry_run_generates_plan_without_writing_memory_by_default(tmp_path: Path) -> None:
    assistant_config = _write_assistant_config(tmp_path)
    orchestrator = TaskOrchestrator.from_config(assistant_config)

    orchestrator.memory_service.put_memory(
        namespace="project_rule/default",
        key="agents_md",
        value={"summary": "遵守 AGENTS.md"},
        source="AGENTS.md",
    )
    orchestrator.memory_service.put_memory(
        namespace="user_preference/default",
        key="language",
        value={"default_output_language": "zh-CN"},
        source="user_input",
    )

    result = orchestrator.run("根据这个需求生成测试用例", dry_run=True, write_memory=False)

    assert result["intent_result"].intent == "test_case_generation"
    assert result["selected_workflow"] == "agent-assets/prompts/test-case-generation.md"
    assert result["risk_level"] == "low"
    assert result["requires_confirmation"] is False
    assert any("dry-run" in step for step in result["execution_plan"])
    assert result["loaded_memory"]["project_rule"]
    assert result["loaded_memory"]["user_preference"]
    assert result["recommended_tools"] == ["memory_read"]
    assert result["tool_authorization_evaluated"] is True
    assert result["tool_decisions"][0]["tool_name"] == "memory_read"
    assert result["tool_decisions"][0]["status"] == "enabled"
    assert result["tool_decisions"][0]["allowed"] is True
    assert result["result"]["memory_write_status"] == "skipped"

    saved = orchestrator.memory_service.get_memory("task_result/orchestrator", result["task_id"])
    assert saved is None


def test_orchestrator_accepts_input_file_context_and_keeps_only_metadata_in_memory(tmp_path: Path) -> None:
    assistant_config = _write_assistant_config(tmp_path)
    orchestrator = TaskOrchestrator.from_config(assistant_config)
    input_files = [
        {
            "requested_path": "README.md",
            "path": "README.md",
            "allowed": True,
            "content": "line1\nline2",
            "reason": "Read allowed.",
            "truncated": False,
        }
    ]

    result = orchestrator.run("请读取 README 并分析项目状态", dry_run=True, write_memory=True, input_files=input_files)

    assert len(result["input_files"]) == 1
    assert result["prepared_context"]["input_files"][0]["path"] == "README.md"
    assert result["prepared_context"]["input_files"][0]["content_in_context"] is True
    assert result["prepared_context"]["input_files"][0]["content_length"] == len("line1\nline2")
    assert any("显式文件上下文：1 个" in step for step in result["execution_plan"])
    saved = orchestrator.memory_service.get_memory("task_result/orchestrator", result["task_id"])
    assert saved is not None
    assert saved.value["input_files"][0]["path"] == "README.md"
    assert saved.value["input_files"][0]["content_length"] == len("line1\nline2")
    assert "content" not in saved.value["input_files"][0]


def test_orchestrator_without_read_file_has_no_input_file_context(tmp_path: Path) -> None:
    assistant_config = _write_assistant_config(tmp_path)
    orchestrator = TaskOrchestrator.from_config(assistant_config)

    result = orchestrator.run("根据这个需求生成测试用例", dry_run=True, write_memory=False, input_files=None)

    assert result.get("input_files", []) == []
    assert result["prepared_context"]["input_files"] == []
    assert any("当前无显式文件上下文。" in step for step in result["execution_plan"])


def test_orchestrator_writes_memory_when_explicitly_enabled(tmp_path: Path) -> None:
    assistant_config = _write_assistant_config(tmp_path)
    orchestrator = TaskOrchestrator.from_config(assistant_config)

    result = orchestrator.run("根据这个需求生成测试用例", dry_run=True, write_memory=True)

    assert result["result"]["memory_write_status"] == "written"
    saved = orchestrator.memory_service.get_memory("task_result/orchestrator", result["task_id"])
    assert saved is not None
    assert saved.value["intent"] == "test_case_generation"
    assert saved.value["dry_run"] is True
    assert saved.value["write_memory"] is True


def test_orchestrator_ambiguous_input_requires_confirmation(tmp_path: Path) -> None:
    assistant_config = _write_assistant_config(tmp_path)
    orchestrator = TaskOrchestrator.from_config(assistant_config)

    result = orchestrator.run("帮我看看这个", dry_run=True, write_memory=False)

    assert result["intent_result"].intent == "unknown"
    assert result["requires_confirmation"] is True
    assert result["risk_level"] == "low"
    assert result["selected_workflow"] is None
    assert "当前未匹配到明确 workflow，需要人工澄清。" in result["execution_plan"]
    assert result["result"]["requires_confirmation"] is True
    assert result["result"]["memory_write_status"] == "skipped"


def test_orchestrator_preserves_non_execution_boundary_in_non_dry_run_mode(tmp_path: Path) -> None:
    assistant_config = _write_assistant_config(tmp_path)
    orchestrator = TaskOrchestrator.from_config(assistant_config)

    result = orchestrator.run("请修改文件并修复路径引用", dry_run=False, write_memory=False)

    assert result["intent_result"].intent == "repo_file_change"
    assert result["requires_confirmation"] is True
    assert result["risk_level"] == "high"
    assert "非 dry-run 执行路径待后续接入，目前未开放。" in result["execution_plan"]
    assert result["recommended_tools"] == ["filesystem"]
    assert result["tool_decisions"][0]["status"] == "disabled"
    assert result["tool_decisions"][0]["allowed"] is False
    assert result["result"]["dry_run"] is False
    assert result["result"]["memory_write_status"] == "skipped"


def test_orchestrator_uses_planned_tools_for_pytest_and_ui_tasks(tmp_path: Path) -> None:
    assistant_config = _write_assistant_config(tmp_path)
    orchestrator = TaskOrchestrator.from_config(assistant_config)

    pytest_result = orchestrator.run("请运行 pytest 并分析 Allure 结果", dry_run=True, write_memory=False)
    ui_result = orchestrator.run("请设计这个页面的 UI 自动化回归方案", dry_run=True, write_memory=False)

    assert pytest_result["intent_result"].intent == "pytest_execution"
    assert pytest_result["recommended_tools"] == ["pytest_runner"]
    assert pytest_result["tool_decisions"][0]["status"] == "planned"
    assert pytest_result["tool_decisions"][0]["risk_level"] == "execute_local_command"
    assert pytest_result["tool_decisions"][0]["allowed"] is False
    assert any("planned" in reason for reason in pytest_result["tool_decisions"][0]["reasons"])

    assert ui_result["intent_result"].intent == "ui_test_design"
    assert ui_result["recommended_tools"] == ["playwright_mcp"]
    assert ui_result["tool_decisions"][0]["status"] == "planned"
    assert ui_result["tool_decisions"][0]["risk_level"] == "external_network"
    assert ui_result["tool_decisions"][0]["allowed"] is False


def test_orchestrator_memory_update_uses_restricted_memory_write_tool(tmp_path: Path) -> None:
    assistant_config = _write_assistant_config(tmp_path)
    orchestrator = TaskOrchestrator.from_config(assistant_config)

    result = orchestrator.run("请记住这个输出偏好并更新记忆", dry_run=True, write_memory=False)

    assert result["intent_result"].intent == "memory_update"
    assert result["recommended_tools"] == ["memory_write"]
    assert result["tool_decisions"][0]["status"] == "disabled"
    assert result["tool_decisions"][0]["risk_level"] == "restricted_action"
    assert result["tool_decisions"][0]["allowed"] is False
    assert any("disabled" in reason or "not enabled" in reason for reason in result["tool_decisions"][0]["reasons"])
