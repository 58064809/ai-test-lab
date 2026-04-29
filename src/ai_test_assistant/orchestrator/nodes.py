from __future__ import annotations

from hashlib import sha1

from ai_test_assistant.intent.router import IntentRouter
from ai_test_assistant.memory.service import MemoryService
from ai_test_assistant.orchestrator.policies import determine_risk_level, requires_confirmation
from ai_test_assistant.orchestrator.state import OrchestratorState
from ai_test_assistant.tool_registry import ToolRegistry
from ai_test_assistant.tool_registry.permissions import ToolPermissionContext


INTENT_TOOL_MAP: dict[str, list[str]] = {
    "test_case_generation": ["memory_read"],
    "api_test_design": ["schemathesis"],
    "ui_test_design": ["playwright_mcp"],
    "pytest_execution": ["pytest_runner"],
    "repo_file_change": ["filesystem"],
    "code_review": ["filesystem"],
    "tool_research": ["github_read"],
    "memory_update": ["memory_write"],
    "workflow_update": ["filesystem"],
}


class OrchestratorNodes:
    """Thin LangGraph node set for the minimal dry-run orchestrator."""

    def __init__(
        self,
        memory_service: MemoryService,
        intent_router: IntentRouter,
        tool_registry: ToolRegistry | None = None,
    ) -> None:
        self.memory_service = memory_service
        self.intent_router = intent_router
        self.tool_registry = tool_registry

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
            "input_files": list(state.get("input_files", [])),
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
        intent_name = state["intent_result"].intent
        recommended_tools = list(INTENT_TOOL_MAP.get(intent_name, []))
        input_files = list(state.get("input_files", []))
        input_file_summaries = [self._summarize_input_file(item) for item in input_files]
        tool_authorization_evaluated, tool_decisions = self._evaluate_tools(
            recommended_tools,
            dry_run=state["dry_run"],
        )
        prepared_context = {
            "intent": intent_name,
            "required_context": list(state["intent_result"].required_context),
            "selected_workflow": state.get("selected_workflow"),
            "input_files": input_file_summaries,
            "recommended_tools": recommended_tools,
            "tool_authorization_evaluated": tool_authorization_evaluated,
            "tool_decisions": tool_decisions,
            "memory_counts": {
                key: len(records)
                for key, records in state.get("loaded_memory", {}).items()
            },
        }
        return {
            "prepared_context": prepared_context,
            "recommended_tools": recommended_tools,
            "tool_authorization_evaluated": tool_authorization_evaluated,
            "tool_decisions": tool_decisions,
        }

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

        input_file_summaries = list(state.get("prepared_context", {}).get("input_files", []))
        if input_file_summaries:
            plan.append(f"显式文件上下文：{len(input_file_summaries)} 个")
            for item in input_file_summaries:
                plan.append(
                    "文件上下文："
                    f"{item.get('path') or '未归一化'} | "
                    f"允许读取={'是' if item.get('allowed', False) else '否'} | "
                    f"已截断={'是' if item.get('truncated', False) else '否'} | "
                    f"内容进入上下文={'是' if item.get('content_in_context', False) else '否'}"
                )
        else:
            plan.append("当前无显式文件上下文。")

        recommended_tools = list(state.get("recommended_tools", []))
        if recommended_tools:
            plan.append(f"推荐工具：{', '.join(recommended_tools)}")
        else:
            plan.append("当前任务不依赖推荐工具。")

        if not state.get("tool_authorization_evaluated", False):
            plan.append("工具授权未评估：当前未加载 tool registry。")

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
        tool_decisions = list(state.get("tool_decisions", []))

        if any(decision.get("requires_confirmation", False) for decision in tool_decisions):
            needs_confirmation = True
        if any(not decision.get("allowed", False) for decision in tool_decisions):
            if risk_level == "low":
                risk_level = "medium"

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
            "input_files": [
                self._memory_safe_input_file(item)
                for item in state.get("input_files", [])
            ],
            "recommended_tools": list(state.get("recommended_tools", [])),
            "tool_authorization_evaluated": state.get("tool_authorization_evaluated", False),
            "tool_decisions": list(state.get("tool_decisions", [])),
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

    def _summarize_input_file(self, item: dict[str, object]) -> dict[str, object]:
        content = item.get("content")
        content_text = content if isinstance(content, str) else ""
        return {
            "requested_path": item.get("requested_path"),
            "path": item.get("path"),
            "source": item.get("source"),
            "allowed": bool(item.get("allowed", False)),
            "truncated": bool(item.get("truncated", False)),
            "reason": str(item.get("reason", "")),
            "content_length": len(content_text),
            "content_in_context": bool(item.get("allowed", False) and bool(content_text)),
        }

    def _memory_safe_input_file(self, item: dict[str, object]) -> dict[str, object]:
        content = item.get("content")
        content_text = content if isinstance(content, str) else ""
        return {
            "requested_path": item.get("requested_path"),
            "path": item.get("path"),
            "source": item.get("source"),
            "allowed": bool(item.get("allowed", False)),
            "truncated": bool(item.get("truncated", False)),
            "reason": str(item.get("reason", "")),
            "content_length": len(content_text),
        }

    def _evaluate_tools(self, recommended_tools: list[str], dry_run: bool) -> tuple[bool, list[dict[str, object]]]:
        if not recommended_tools:
            return True, []

        if self.tool_registry is None:
            return False, [
                {
                    "tool_name": tool_name,
                    "status": None,
                    "risk_level": None,
                    "allowed": False,
                    "requires_confirmation": True,
                    "reasons": ["Tool registry 未加载，当前工具授权未评估。"],
                }
                for tool_name in recommended_tools
            ]

        decisions: list[dict[str, object]] = []
        context = ToolPermissionContext(dry_run=dry_run)
        for tool_name in recommended_tools:
            tool = self.tool_registry.get_tool(tool_name)
            decision = self.tool_registry.evaluate_execution(tool_name, context=context)
            decisions.append(
                {
                    "tool_name": tool.name,
                    "status": tool.status.value,
                    "risk_level": tool.risk_level.value,
                    "allowed": decision.allowed,
                    "requires_confirmation": decision.requires_confirmation,
                    "reasons": list(decision.reasons),
                }
            )
        return True, decisions
