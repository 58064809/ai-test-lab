from __future__ import annotations

from pathlib import Path

from ai_test_assistant.memory.service import MemoryService
from ai_test_assistant.memory.sqlite_store import SQLiteMemoryStore


def test_put_and_get_memory(tmp_path: Path) -> None:
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")

    record = store.put_memory(
        namespace="project_rule/default",
        key="agents_md",
        value={"path": "AGENTS.md", "summary": "项目级规则入口"},
        source="AGENTS.md",
    )

    assert record.memory_type == "project_rule"
    assert record.value["summary"] == "项目级规则入口"

    loaded = store.get_memory("project_rule/default", "agents_md")
    assert loaded is not None
    assert loaded.source == "AGENTS.md"
    assert loaded.value["path"] == "AGENTS.md"


def test_search_memory_in_namespace(tmp_path: Path) -> None:
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")
    store.put_memory(
        namespace="workflow_memory/api",
        key="schema-first",
        value={"note": "先读 OpenAPI 再设计场景"},
        source="workflows/api-test-workflow.md",
    )
    store.put_memory(
        namespace="workflow_memory/api",
        key="risk-boundary",
        value={"note": "高风险写接口不要直接 fuzz"},
        source="workflows/api-test-workflow.md",
    )

    results = store.search_memory("workflow_memory/api", query="OpenAPI")
    assert len(results) == 1
    assert results[0].key == "schema-first"

    filtered = store.search_memory(
        "workflow_memory/api",
        filters={"memory_type": "workflow_memory", "source": "workflows/api-test-workflow.md"},
    )
    assert len(filtered) == 2


def test_delete_memory(tmp_path: Path) -> None:
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")
    store.put_memory(
        namespace="task_result/daily",
        key="task-001",
        value={"status": "done"},
        source="manual",
    )

    assert store.delete_memory("task_result/daily", "task-001") is True
    assert store.get_memory("task_result/daily", "task-001") is None
    assert store.delete_memory("task_result/daily", "task-001") is False


def test_memory_persists_after_reinstantiation(tmp_path: Path) -> None:
    db_path = tmp_path / "memory.sqlite3"
    store = SQLiteMemoryStore(db_path)
    store.put_memory(
        namespace="user_preference/default",
        key="language",
        value={"default_output_language": "zh-CN"},
        source="user_input",
    )

    reloaded_store = SQLiteMemoryStore(db_path)
    loaded = reloaded_store.get_memory("user_preference/default", "language")

    assert loaded is not None
    assert loaded.value["default_output_language"] == "zh-CN"


def test_memory_service_reads_yaml_config(tmp_path: Path) -> None:
    db_path = tmp_path / "assistant-memory.sqlite3"
    config_path = tmp_path / "assistant.yaml"
    config_path.write_text(
        "\n".join(
            [
                "memory:",
                "  backend: sqlite",
                f"  sqlite_path: {db_path.as_posix()}",
            ]
        ),
        encoding="utf-8",
    )

    service = MemoryService.from_config(config_path)
    service.put_memory(
        namespace="tool_capability/local",
        key="sqlite",
        value={"status": "implemented"},
        source="tests",
    )

    reloaded = SQLiteMemoryStore(db_path).get_memory("tool_capability/local", "sqlite")
    assert reloaded is not None
    assert reloaded.value["status"] == "implemented"

