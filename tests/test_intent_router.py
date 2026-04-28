from __future__ import annotations

from pathlib import Path

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


def test_routes_test_case_generation_from_clear_request() -> None:
    router = IntentRouter.from_rules_file("configs/intents.yaml")

    result = router.route("根据这个需求生成测试用例")

    assert result.intent == "test_case_generation"
    assert result.confidence >= 0.5
    assert "测试用例" in result.matched_rules
    assert result.recommended_workflow == "agent-assets/prompts/test-case-generation.md"
    assert result.clarification_required is False


def test_routes_log_analysis_from_clear_request() -> None:
    router = IntentRouter.from_rules_file("configs/intents.yaml")

    result = router.route("分析这段报错日志")

    assert result.intent == "log_analysis"
    assert result.confidence >= 0.5
    assert any(item in result.matched_rules for item in ["日志", "报错"])
    assert result.recommended_workflow == "agent-assets/prompts/log-analysis.md"
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
