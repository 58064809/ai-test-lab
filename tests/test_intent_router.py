from __future__ import annotations

from pathlib import Path

import pytest

from ai_test_assistant.intent.router import IntentRouter
from ai_test_assistant.intent.rules_loader import IntentRulesLoader


def test_rules_loader_loads_required_intents() -> None:
    config = IntentRulesLoader.load("configs/intents.yaml")

    assert config.minimum_confidence > 0
    assert config.ambiguity_gap > 0
    names = {rule.name for rule in config.rules}
    assert "test_case_generation" in names
    assert "log_analysis" in names
    assert "workflow_update" in names


@pytest.mark.parametrize(
    ("task_text", "expected_intent", "expected_workflow"),
    [
        ("请做需求分析", "requirement_analysis", "agent-assets/prompts/requirement-analysis.md"),
        ("根据这个需求生成测试用例", "test_case_generation", "agent-assets/prompts/test-case-generation.md"),
        ("请基于OpenAPI设计接口测试方案", "api_test_design", "agent-assets/workflows/api-test-workflow.md"),
        ("请设计UI自动化页面回归方案", "ui_test_design", "agent-assets/workflows/ui-test-workflow.md"),
        ("请运行pytest并分析allure结果", "pytest_execution", "docs/tools/pytest-allure.md"),
        ("分析这段报错日志", "log_analysis", "agent-assets/prompts/log-analysis.md"),
        ("请整理缺陷报告和复现步骤", "bug_report", "agent-assets/prompts/bug-report.md"),
        ("请做 code review", "code_review", "待接入：代码评审工作流"),
        ("请修改文件并修复路径引用", "repo_file_change", "待接入：仓库改动工作流"),
        ("请调研 Schemathesis 接入方式", "tool_research", "docs/tools/sources.md"),
        ("请读取 README 并分析项目状态", "tool_research", "docs/tools/sources.md"),
        ("读取 README 并分析项目状态", "tool_research", "docs/tools/sources.md"),
        ("结合 README 分析项目状态", "tool_research", "docs/tools/sources.md"),
        ("请记住并保存偏好", "memory_update", "src/ai_test_assistant/memory/README.md"),
        ("请更新工作流并修改模板", "workflow_update", "agent-assets/workflows/defect-analysis-workflow.md"),
    ],
)
def test_routes_all_required_intents_from_clear_requests(
    task_text: str,
    expected_intent: str,
    expected_workflow: str,
) -> None:
    router = IntentRouter.from_rules_file("configs/intents.yaml")

    result = router.route(task_text)

    assert result.intent == expected_intent
    assert result.confidence >= 0.5
    assert result.recommended_workflow == expected_workflow
    assert result.clarification_required is False


def test_ambiguous_input_requires_clarification() -> None:
    router = IntentRouter.from_rules_file("configs/intents.yaml")

    result = router.route("帮我看看这个")

    assert result.intent == "unknown"
    assert result.confidence == 0.0
    assert result.clarification_required is True
    assert len(result.clarification_questions) >= 1


def test_conflicting_intents_require_clarification() -> None:
    router = IntentRouter.from_rules_file("configs/intents.yaml")

    result = router.route("请根据日志生成缺陷报告")

    assert result.intent in {"log_analysis", "bug_report"}
    assert result.clarification_required is True
    assert len(result.clarification_questions) >= 1


def test_router_can_load_rules_path_from_assistant_config(tmp_path: Path) -> None:
    intents_path = Path("configs/intents.yaml").resolve()
    assistant_config = tmp_path / "assistant.yaml"
    assistant_config.write_text(
        "\n".join(
            [
                "memory:",
                "  backend: sqlite",
                "  sqlite_path: .assistant/memory.sqlite3",
                "intent:",
                f"  rules_path: {intents_path.as_posix()}",
            ]
        ),
        encoding="utf-8",
    )

    router = IntentRouter.from_assistant_config(assistant_config)
    result = router.route("请做需求分析")

    assert result.intent == "requirement_analysis"
    assert result.clarification_required is False


def test_router_can_load_relative_rules_path_from_assistant_config(tmp_path: Path) -> None:
    assistant_config = tmp_path / "assistant.yaml"
    assistant_config.write_text(
        "\n".join(
            [
                "memory:",
                "  backend: sqlite",
                "  sqlite_path: .assistant/memory.sqlite3",
                "intent:",
                "  rules_path: configs/intents.yaml",
            ]
        ),
        encoding="utf-8",
    )

    router = IntentRouter.from_assistant_config(assistant_config)
    result = router.route("请做需求分析")

    assert result.intent == "requirement_analysis"
    assert result.clarification_required is False


def test_rules_loader_rejects_duplicate_intent_names(tmp_path: Path) -> None:
    config_path = tmp_path / "duplicate.yaml"
    config_path.write_text(
        "\n".join(
            [
                "defaults:",
                "  minimum_confidence: 0.45",
                "  ambiguity_gap: 0.15",
                "intents:",
                "  - name: duplicate_intent",
                "    description: first",
                "    triggers: [\"a\"]",
                "    negative_triggers: []",
                "    required_context: [\"ctx\"]",
                "    optional_context: []",
                "    recommended_workflow: wf1",
                "    default_prompt: prompt1",
                "  - name: duplicate_intent",
                "    description: second",
                "    triggers: [\"b\"]",
                "    negative_triggers: []",
                "    required_context: [\"ctx\"]",
                "    optional_context: []",
                "    recommended_workflow: wf2",
                "    default_prompt: prompt2",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate intent rule names found"):
        IntentRulesLoader.load(config_path)


@pytest.mark.parametrize(
    ("field_name", "field_lines", "expected_message"),
    [
        ("triggers", ["    triggers: []"], "must define at least one trigger"),
        ("required_context", ["    required_context: []"], "must define at least one required_context item"),
    ],
)
def test_rules_loader_rejects_empty_required_rule_lists(
    tmp_path: Path,
    field_name: str,
    field_lines: list[str],
    expected_message: str,
) -> None:
    base_lines = [
        "defaults:",
        "  minimum_confidence: 0.45",
        "  ambiguity_gap: 0.15",
        "intents:",
        "  - name: sample_intent",
        "    description: sample",
        "    triggers: [\"trigger\"]",
        "    negative_triggers: []",
        "    required_context: [\"ctx\"]",
        "    optional_context: []",
        "    recommended_workflow: sample-workflow",
        "    default_prompt: sample-prompt",
    ]
    replacements = {
        "triggers": "    triggers: [\"trigger\"]",
        "required_context": "    required_context: [\"ctx\"]",
    }
    replaced = [
        field_lines[0] if line == replacements[field_name] else line
        for line in base_lines
    ]
    config_path = tmp_path / f"{field_name}-empty.yaml"
    config_path.write_text("\n".join(replaced), encoding="utf-8")

    with pytest.raises(ValueError, match=expected_message):
        IntentRulesLoader.load(config_path)


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("minimum_confidence", "1.2"),
        ("ambiguity_gap", "-0.1"),
    ],
)
def test_rules_loader_rejects_probability_values_out_of_range(
    tmp_path: Path,
    field_name: str,
    field_value: str,
) -> None:
    config_path = tmp_path / f"{field_name}-invalid.yaml"
    config_path.write_text(
        "\n".join(
            [
                "defaults:",
                f"  {field_name}: {field_value}",
                "  ambiguity_gap: 0.15" if field_name != "ambiguity_gap" else "  minimum_confidence: 0.45",
                "intents:",
                "  - name: sample_intent",
                "    description: sample",
                "    triggers: [\"trigger\"]",
                "    negative_triggers: []",
                "    required_context: [\"ctx\"]",
                "    optional_context: []",
                "    recommended_workflow: sample-workflow",
                "    default_prompt: sample-prompt",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=f"{field_name} must be within 0 and 1"):
        IntentRulesLoader.load(config_path)
