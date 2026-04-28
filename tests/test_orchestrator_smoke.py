from __future__ import annotations

from pathlib import Path

from ai_test_assistant.orchestrator.graph import TaskOrchestrator


def _write_assistant_config(tmp_path: Path) -> Path:
    memory_db_path = (tmp_path / "memory.sqlite3").resolve()
    intents_path = Path("configs/intents.yaml").resolve()
    assistant_config = tmp_path / "assistant.yaml"
    assistant_config.write_text(
        "\n".join(
            [
                "memory:",
                "  backend: sqlite",
                f"  sqlite_path: {memory_db_path.as_posix()}",
                "intent:",
                f"  rules_path: {intents_path.as_posix()}",
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
    assert result["result"]["memory_write_status"] == "skipped"

    saved = orchestrator.memory_service.get_memory("task_result/orchestrator", result["task_id"])
    assert saved is None


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
    assert result["result"]["dry_run"] is False
    assert result["result"]["memory_write_status"] == "skipped"
