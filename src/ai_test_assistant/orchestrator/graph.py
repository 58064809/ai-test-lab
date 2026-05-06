from __future__ import annotations

from pathlib import Path

import yaml
from langgraph.graph import END, START, StateGraph

from ai_test_assistant.intent.router import IntentRouter
from ai_test_assistant.memory.service import MemoryService
from ai_test_assistant.orchestrator.nodes import OrchestratorNodes
from ai_test_assistant.orchestrator.state import OrchestratorState
from ai_test_assistant.tool_registry import ToolRegistry


class TaskOrchestrator:
    """Minimal LangGraph-based orchestrator skeleton.

    This class intentionally keeps orchestration thin:
    - LangGraph expresses the flow
    - nodes delegate to memory and intent modules
    - dry-run only produces a plan and writes internal task memory
    """

    def __init__(
        self,
        memory_service: MemoryService,
        intent_router: IntentRouter,
        tool_registry: ToolRegistry | None = None,
    ) -> None:
        self.memory_service = memory_service
        self.intent_router = intent_router
        self.tool_registry = tool_registry
        self.nodes = OrchestratorNodes(
            memory_service=memory_service,
            intent_router=intent_router,
            tool_registry=tool_registry,
        )
        self.graph = self._build_graph()

    @classmethod
    def from_config(cls, assistant_config_path: str | Path = "configs/assistant.yaml") -> "TaskOrchestrator":
        memory_service = MemoryService.from_config(assistant_config_path)
        intent_router = IntentRouter.from_assistant_config(assistant_config_path)
        tool_registry = cls._load_tool_registry(assistant_config_path)
        return cls(
            memory_service=memory_service,
            intent_router=intent_router,
            tool_registry=tool_registry,
        )

    def run(
        self,
        task_text: str,
        dry_run: bool = True,
        write_memory: bool = False,
        input_files: list[dict[str, object]] | None = None,
        allure_reports: list[dict[str, object]] | None = None,
        explicit_tool_executions: list[dict[str, object]] | None = None,
    ) -> OrchestratorState:
        initial_state: OrchestratorState = {
            "task_text": task_text,
            "dry_run": dry_run,
            "write_memory": write_memory,
            "input_files": list(input_files or []),
            "allure_reports": list(allure_reports or []),
            "explicit_tool_executions": list(explicit_tool_executions or []),
            "errors": [],
        }
        return self.graph.invoke(initial_state)

    @staticmethod
    def _load_tool_registry(assistant_config_path: str | Path) -> ToolRegistry | None:
        config_file = Path(assistant_config_path)
        config_data = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
        tool_registry_config = config_data.get("tool_registry", {})
        config_path = tool_registry_config.get("config_path")
        if not config_path:
            return None

        tool_config_path = Path(str(config_path))
        if not tool_config_path.exists():
            return None

        return ToolRegistry.from_yaml(tool_config_path)

    def _build_graph(self):
        builder = StateGraph(OrchestratorState)
        builder.add_node("receive_task", self.nodes.receive_task)
        builder.add_node("load_memory", self.nodes.load_memory)
        builder.add_node("classify_intent", self.nodes.classify_intent)
        builder.add_node("select_workflow", self.nodes.select_workflow)
        builder.add_node("prepare_context", self.nodes.prepare_context)
        builder.add_node("plan", self.nodes.plan)
        builder.add_node("review", self.nodes.review)
        builder.add_node("write_memory", self.nodes.write_memory)

        builder.add_edge(START, "receive_task")
        builder.add_edge("receive_task", "load_memory")
        builder.add_edge("load_memory", "classify_intent")
        builder.add_edge("classify_intent", "select_workflow")
        builder.add_edge("select_workflow", "prepare_context")
        builder.add_edge("prepare_context", "plan")
        builder.add_edge("plan", "review")
        builder.add_edge("review", "write_memory")
        builder.add_edge("write_memory", END)
        return builder.compile()
