from __future__ import annotations

from pathlib import Path

from ai_test_assistant.intent.router import IntentRouter
from ai_test_assistant.orchestrator.graph import TaskOrchestrator
from ai_test_assistant.validation import RealTaskSampleLoader, RealTaskValidationRunner


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


def test_real_task_samples_load_successfully() -> None:
    samples = RealTaskSampleLoader.load()

    assert len(samples) >= 15
    categories = {sample.category for sample in samples}
    assert {
        "requirement_analysis",
        "test_case_generation",
        "api_test_design",
        "ui_test_design",
        "pytest_execution",
        "log_analysis",
        "bug_report",
        "code_review",
        "repo_file_change",
        "tool_research",
        "memory_update",
        "workflow_update",
        "ambiguous",
        "conflicting",
        "risky",
    }.issubset(categories)


def test_main_intent_samples_pass_validation(tmp_path: Path) -> None:
    config_path = _write_assistant_config(tmp_path)
    samples = RealTaskSampleLoader.load()
    router = IntentRouter.from_assistant_config(config_path)
    orchestrator = TaskOrchestrator.from_config(config_path)
    runner = RealTaskValidationRunner(router, orchestrator)

    major_categories = {
        "requirement_analysis",
        "test_case_generation",
        "api_test_design",
        "ui_test_design",
        "pytest_execution",
        "log_analysis",
        "bug_report",
        "code_review",
        "repo_file_change",
        "tool_research",
        "memory_update",
        "workflow_update",
    }
    target_samples = [sample for sample in samples if sample.category in major_categories]

    results = runner.run_all(target_samples)

    assert len(results) == 12
    assert all(result.passed for result in results), results


def test_ambiguous_and_conflicting_samples_trigger_clarification(tmp_path: Path) -> None:
    config_path = _write_assistant_config(tmp_path)
    samples = {sample.category: sample for sample in RealTaskSampleLoader.load()}
    router = IntentRouter.from_assistant_config(config_path)
    orchestrator = TaskOrchestrator.from_config(config_path)
    runner = RealTaskValidationRunner(router, orchestrator)

    ambiguous_result = runner.run_sample(samples["ambiguous"])
    conflicting_result = runner.run_sample(samples["conflicting"])

    assert ambiguous_result.passed is True
    assert ambiguous_result.actual_intent == "unknown"
    assert ambiguous_result.actual_clarification_required is True

    assert conflicting_result.passed is True
    assert conflicting_result.actual_clarification_required is True


def test_risky_tool_samples_produce_expected_dry_run_authorization_results(tmp_path: Path) -> None:
    config_path = _write_assistant_config(tmp_path)
    samples = {sample.category: sample for sample in RealTaskSampleLoader.load()}
    router = IntentRouter.from_assistant_config(config_path)
    orchestrator = TaskOrchestrator.from_config(config_path)
    runner = RealTaskValidationRunner(router, orchestrator)

    pytest_result = runner.run_sample(samples["pytest_execution"])
    repo_result = runner.run_sample(samples["repo_file_change"])
    ui_result = runner.run_sample(samples["ui_test_design"])

    assert pytest_result.passed is True
    assert pytest_result.actual_tool_statuses["pytest_runner"] == "planned"
    assert pytest_result.actual_tool_allowed["pytest_runner"] is False

    assert repo_result.passed is True
    assert repo_result.actual_tool_statuses["filesystem"] == "disabled"
    assert repo_result.actual_tool_allowed["filesystem"] is False

    assert ui_result.passed is True
    assert ui_result.actual_tool_statuses["playwright_mcp"] == "planned"
    assert ui_result.actual_tool_allowed["playwright_mcp"] is False
