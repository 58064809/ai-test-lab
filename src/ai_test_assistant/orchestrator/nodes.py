from __future__ import annotations

from hashlib import sha1

from ai_test_assistant.intent.router import IntentRouter
from ai_test_assistant.memory.service import MemoryService
from ai_test_assistant.orchestrator.policies import determine_risk_level, requires_confirmation
from ai_test_assistant.orchestrator.state import OrchestratorState


class OrchestratorNodes:
    """Thin LangGraph node set for the minimal dry-run orchestrator."""

    def __init__(self, memory_service: MemoryService, intent_router: IntentRouter) -> None:
        self.memory_service = memory_service
        self.intent_router = intent_router

    def receive_task(self, state: OrchestratorState) -> OrchestratorState:
        task_text = state.get("task_text", "").strip()
        errors = list(state.get("errors", []))
        if not task_text:
            errors.append("Task text must not be empty.")

        task_id = state.get("task_id")
        if not task_id and task_text:
            task_id = sha1(task_text.encode("utf-8")).hexdigest()[:12]

        return {
            "task_id": task_id or "unknown-task",
            "task_text": task_text,
            "dry_run": bool(state.get("dry_run", True)),
            "write_memory": bool(state.get("write_memory", False)),
            "errors": errors,
        }

    def load_memory(self, state: OrchestratorState) -> OrchestratorState:
        loaded_memory = {
            "project_rule": self.memory_service.search_memory("project_rule/default"),
            "user_preference": self.memory_service.search_memory("user_preference/default"),
        }
        return {"loaded_memory": loaded_memory}

    def classify_intent(self, state: OrchestratorState) -> OrchestratorState:
        intent_result = self.intent_router.route(state["task_text"])
        return {"intent_result": intent_result}

    def select_workflow(self, state: OrchestratorState) -> OrchestratorState:
        selected_workflow = state["intent_result"].recommended_workflow
        return {"selected_workflow": selected_workflow}

    def prepare_context(self, state: OrchestratorState) -> OrchestratorState:
        prepared_context = {
            "intent": state["intent_result"].intent,
            "required_context": list(state["intent_result"].required_context),
            "selected_workflow": state.get("selected_workflow"),
            "memory_counts": {
                key: len(records)
                for key, records in state.get("loaded_memory", {}).items()
            },
        }
        return {"prepared_context": prepared_context}

    def plan(self, state: OrchestratorState) -> OrchestratorState:
        dry_run = state["dry_run"]
        intent_result = state["intent_result"]
        plan = [
            f"识别任务意图：{intent_result.intent}",
            f"加载项目规则记忆：{len(state.get('loaded_memory', {}).get('project_rule', []))} 条",
            f"加载用户偏好记忆：{len(state.get('loaded_memory', {}).get('user_preference', []))} 条",
        ]

        if state.get("selected_workflow"):
            plan.append(f"选择推荐 workflow：{state['selected_workflow']}")
        else:
            plan.append("当前未匹配到明确 workflow，需要人工澄清。")

        if dry_run:
            plan.extend(
                [
                    "当前为 dry-run：仅生成任务计划，不执行外部工具。",
                    "下一步建议：补充 required_context 后再进入真实执行层。",
                ]
            )
        else:
            plan.append("非 dry-run 执行路径待后续接入，目前未开放。")

        return {"execution_plan": plan}

    def review(self, state: OrchestratorState) -> OrchestratorState:
        intent_result = state["intent_result"]
        dry_run = state["dry_run"]
        risk_level = determine_risk_level(intent_result, dry_run=dry_run)
        needs_confirmation = requires_confirmation(intent_result, dry_run=dry_run)

        return {
            "risk_level": risk_level,
            "requires_confirmation": needs_confirmation,
        }

    def write_memory(self, state: OrchestratorState) -> OrchestratorState:
        summary = {
            "task_text": state["task_text"],
            "intent": state["intent_result"].intent,
            "selected_workflow": state.get("selected_workflow"),
            "dry_run": state["dry_run"],
            "write_memory": state.get("write_memory", False),
            "requires_confirmation": state.get("requires_confirmation", False),
            "execution_plan": list(state.get("execution_plan", [])),
        }
        if state.get("write_memory", False):
            self.memory_service.put_memory(
                namespace="task_result/orchestrator",
                key=state["task_id"],
                value=summary,
                memory_type="task_result",
                source="orchestrator",
            )
            summary["memory_write_status"] = "written"
        else:
            summary["memory_write_status"] = "skipped"
        return {"result": summary}
