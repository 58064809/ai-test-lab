from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from ai_test_assistant.intent.models import IntentRouteResult, IntentRule
from ai_test_assistant.intent.rules_loader import IntentRulesConfig, IntentRulesLoader


@dataclass(slots=True)
class _ScoredRule:
    rule: IntentRule
    confidence: float
    positive_matches: list[str]
    negative_matches: list[str]


class IntentRouter:
    """Configuration-driven intent router without external LLM calls."""

    def __init__(self, config: IntentRulesConfig) -> None:
        self.config = config

    @classmethod
    def from_rules_file(cls, rules_path: str | Path) -> "IntentRouter":
        return cls(IntentRulesLoader.load(rules_path))

    @classmethod
    def from_assistant_config(cls, assistant_config_path: str | Path = "configs/assistant.yaml") -> "IntentRouter":
        config_file = Path(assistant_config_path)
        assistant_config = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
        intent_config = assistant_config.get("intent", {})
        rules_path = intent_config.get("rules_path", "configs/intents.yaml")
        return cls.from_rules_file(rules_path)

    def route(self, task_text: str) -> IntentRouteResult:
        normalized_text = self._normalize(task_text)
        scored_rules = [self._score_rule(rule, normalized_text) for rule in self.config.rules]
        scored_rules.sort(key=lambda item: item.confidence, reverse=True)

        top_rule = scored_rules[0] if scored_rules else None
        second_rule = scored_rules[1] if len(scored_rules) > 1 else None

        if top_rule is None or not top_rule.positive_matches:
            return IntentRouteResult(
                intent="unknown",
                confidence=0.0,
                clarification_required=True,
                clarification_questions=self._build_generic_questions(),
            )

        clarification_required = False
        clarification_questions: list[str] = []

        if top_rule.confidence < self.config.minimum_confidence:
            clarification_required = True
            clarification_questions.extend(self._build_generic_questions())

        if second_rule is not None and second_rule.confidence > 0:
            if top_rule.confidence - second_rule.confidence < self.config.ambiguity_gap:
                clarification_required = True
                clarification_questions.extend(
                    [
                        f"当前输入同时接近“{top_rule.rule.name}”和“{second_rule.rule.name}”，请明确你更希望我执行哪类任务。",
                    ]
                )

        if clarification_required and not clarification_questions:
            clarification_questions.extend(self._build_generic_questions())

        clarification_questions = self._deduplicate(clarification_questions)

        return IntentRouteResult(
            intent=top_rule.rule.name,
            confidence=round(top_rule.confidence, 2),
            matched_rules=top_rule.positive_matches,
            required_context=list(top_rule.rule.required_context),
            recommended_workflow=top_rule.rule.recommended_workflow,
            clarification_required=clarification_required,
            clarification_questions=clarification_questions,
        )

    def _score_rule(self, rule: IntentRule, normalized_text: str) -> _ScoredRule:
        positive_matches = [trigger for trigger in rule.triggers if self._normalize(trigger) in normalized_text]
        negative_matches = [trigger for trigger in rule.negative_triggers if self._normalize(trigger) in normalized_text]

        confidence = 0.0
        if positive_matches:
            confidence = 0.2 + min(0.65, len(positive_matches) * 0.2)
            if len(positive_matches) >= 2:
                confidence += 0.1
            confidence -= min(0.5, len(negative_matches) * 0.25)
            confidence = max(0.0, min(0.95, confidence))

        return _ScoredRule(
            rule=rule,
            confidence=confidence,
            positive_matches=positive_matches,
            negative_matches=negative_matches,
        )

    def _build_generic_questions(self) -> list[str]:
        return list(self.config.generic_clarification_questions)

    def _normalize(self, value: str) -> str:
        return "".join(value.lower().split())

    def _deduplicate(self, items: list[str]) -> list[str]:
        ordered: list[str] = []
        seen: set[str] = set()
        for item in items:
            if item not in seen:
                ordered.append(item)
                seen.add(item)
        return ordered

