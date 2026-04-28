from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from ai_test_assistant.intent.models import IntentRule


@dataclass(slots=True)
class IntentRulesConfig:
    minimum_confidence: float
    ambiguity_gap: float
    generic_clarification_questions: list[str]
    rules: list[IntentRule]


class IntentRulesLoader:
    """Loads configuration-driven intent rules from YAML."""

    REQUIRED_FIELDS = {
        "name",
        "description",
        "triggers",
        "negative_triggers",
        "required_context",
        "optional_context",
        "recommended_workflow",
        "default_prompt",
    }

    @classmethod
    def load(cls, config_path: str | Path) -> IntentRulesConfig:
        path = Path(config_path)
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        defaults = data.get("defaults", {})
        intents = data.get("intents", [])

        minimum_confidence = float(defaults.get("minimum_confidence", 0.45))
        ambiguity_gap = float(defaults.get("ambiguity_gap", 0.15))
        cls._validate_probability("minimum_confidence", minimum_confidence)
        cls._validate_probability("ambiguity_gap", ambiguity_gap)

        rules = [cls._build_rule(item) for item in intents]
        cls._validate_rule_names(rules)
        return IntentRulesConfig(
            minimum_confidence=minimum_confidence,
            ambiguity_gap=ambiguity_gap,
            generic_clarification_questions=list(
                defaults.get(
                    "generic_clarification_questions",
                    [
                        "请说明你希望我做哪类任务，例如需求分析、测试用例生成、日志分析或缺陷报告。",
                        "请补充你已有的材料，例如需求原文、日志、接口文档或问题现象。",
                    ],
                )
            ),
            rules=rules,
        )

    @classmethod
    def _build_rule(cls, item: dict[str, object]) -> IntentRule:
        missing = sorted(cls.REQUIRED_FIELDS - set(item))
        if missing:
            raise ValueError(f"Intent rule missing required fields: {missing}")

        triggers = cls._as_str_list(item["triggers"])
        required_context = cls._as_str_list(item["required_context"])
        if not triggers:
            raise ValueError(f"Intent rule '{item['name']}' must define at least one trigger.")
        if not required_context:
            raise ValueError(f"Intent rule '{item['name']}' must define at least one required_context item.")

        return IntentRule(
            name=str(item["name"]),
            description=str(item["description"]),
            triggers=triggers,
            negative_triggers=cls._as_str_list(item["negative_triggers"]),
            required_context=required_context,
            optional_context=cls._as_str_list(item["optional_context"]),
            recommended_workflow=str(item["recommended_workflow"]),
            default_prompt=str(item["default_prompt"]),
        )

    @staticmethod
    def _as_str_list(value: object) -> list[str]:
        if not isinstance(value, list):
            raise ValueError("Intent rule list fields must use YAML arrays.")
        return [str(item) for item in value]

    @staticmethod
    def _validate_probability(field_name: str, value: float) -> None:
        if not 0 <= value <= 1:
            raise ValueError(f"{field_name} must be within 0 and 1.")

    @staticmethod
    def _validate_rule_names(rules: list[IntentRule]) -> None:
        names = [rule.name for rule in rules]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            raise ValueError(f"Duplicate intent rule names found: {duplicates}")
