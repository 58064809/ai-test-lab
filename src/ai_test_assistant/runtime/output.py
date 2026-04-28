from __future__ import annotations

from typing import Any

from ai_test_assistant.intent.models import IntentRouteResult
from ai_test_assistant.orchestrator.state import OrchestratorState


def render_intent_only(task_text: str, result: IntentRouteResult) -> str:
    lines = [
        "任务摘要",
        f"- 原始任务：{task_text}",
        f"- 识别意图：{result.intent}",
        f"- 置信度：{result.confidence}",
        f"- 是否需要澄清：{'是' if result.clarification_required else '否'}",
        f"- 推荐 workflow：{result.recommended_workflow or '未匹配'}",
    ]

    if result.matched_rules:
        lines.append(f"- 命中规则：{', '.join(result.matched_rules)}")

    if result.required_context:
        lines.append(f"- 必要上下文：{', '.join(result.required_context)}")

    if result.clarification_questions:
        lines.append("- 澄清问题：")
        for question in result.clarification_questions:
            lines.append(f"  - {question}")

    return "\n".join(lines)


def render_orchestrator_result(state: OrchestratorState, write_memory: bool) -> str:
    intent_result = state["intent_result"]
    loaded_memory = state.get("loaded_memory", {})
    recommended_tools = list(state.get("recommended_tools", []))
    tool_decisions = list(state.get("tool_decisions", []))
    lines = [
        "任务摘要",
        f"- 原始任务：{state['task_text']}",
        f"- dry-run：{'是' if state.get('dry_run', True) else '否'}",
        f"- 识别意图：{intent_result.intent}",
        f"- 置信度：{intent_result.confidence}",
        f"- 是否需要澄清：{'是' if intent_result.clarification_required else '否'}",
        f"- 推荐 workflow：{state.get('selected_workflow') or '未匹配'}",
        f"- 风险等级：{state.get('risk_level', 'unknown')}",
        f"- 是否需要确认：{'是' if state.get('requires_confirmation', False) else '否'}",
        f"- 记忆摘要：project_rule={len(loaded_memory.get('project_rule', []))}，user_preference={len(loaded_memory.get('user_preference', []))}",
        f"- 任务结果记忆写入：{'允许' if write_memory else '禁止'}",
        f"- 工具授权评估：{'已完成' if state.get('tool_authorization_evaluated', False) else '未完成'}",
        f"- 推荐工具：{', '.join(recommended_tools) if recommended_tools else '无'}",
        "- 工具风险提示：当前 runtime 不执行外部工具、不执行本地命令、不访问外部网络。",
        "- 下一步计划：",
    ]

    for step in state.get("execution_plan", []):
        lines.append(f"  - {step}")

    if tool_decisions:
        lines.append("- 工具授权结果：")
        for decision in tool_decisions:
            status = decision.get("status") or "未评估"
            risk_level = decision.get("risk_level") or "未评估"
            lines.append(
                "  - "
                f"{decision.get('tool_name')} | 状态={status} | 风险={risk_level} | "
                f"允许执行={'是' if decision.get('allowed', False) else '否'} | "
                f"需要确认={'是' if decision.get('requires_confirmation', False) else '否'}"
            )
            reasons = list(decision.get("reasons", []))
            if reasons:
                lines.append(f"    拒绝原因：{'；'.join(reasons)}")

    if intent_result.clarification_required and intent_result.clarification_questions:
        lines.append("- 澄清问题：")
        for question in intent_result.clarification_questions:
            lines.append(f"  - {question}")

    return "\n".join(lines)


def render_error(message: str, details: dict[str, Any] | None = None) -> str:
    lines = [f"错误：{message}"]
    if details:
        for key, value in details.items():
            lines.append(f"- {key}：{value}")
    return "\n".join(lines)
