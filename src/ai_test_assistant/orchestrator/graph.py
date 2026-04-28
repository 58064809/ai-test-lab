from __future__ import annotations

from pathlib import Path

from langgraph.graph import END, START, StateGraph

from ai_test_assistant.intent.router import IntentRouter
from ai_test_assistant.memory.service import MemoryService
from ai_test_assistant.orchestrator.nodes import OrchestratorNodes
from ai_test_assistant.orchestrator.state import OrchestratorState


class TaskOrchestrator:
    """Minimal LangGraph-based orchestrator skeleton.

    This class intentionally keeps orchestration thin:
    - LangGraph expresses the flow
    - nodes delegate to memory and intent modules
    - dry-run only produces a plan and writes internal task memory
    """

    def __init__(self, memory_service: MemoryService, intent_router: IntentRouter) -> None:
        self.memory_service = memory_service
        self.intent_router = intent_router
        self.nodes = OrchestratorNodes(memory_service=memory_service, intent_router=intent_router)
        self.graph = self._build_graph()

    @classmethod
    def from_config(cls, assistant_config_path: str | Path = "configs/assistant.yaml") -> "TaskOrchestrator":
        memory_service = MemoryService.from_config(assistant_config_path)
        intent_router = IntentRouter.from_assistant_config(assistant_config_path)
        return cls(memory_service=memory_service, intent_router=intent_router)

    def run(self, task_text: str, dry_run: bool = True, write_memory: bool = False) -> OrchestratorState:
        initial_state: OrchestratorState = {
            "task_text": task_text,
            "dry_run": dry_run,
            "write_memory": write_memory,
            "errors": [],
        }
        return self.graph.invoke(initial_state)

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
