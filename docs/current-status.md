# Current Status

## 已实现

- `memory` 最小可运行底座已落地。
- Agent 资产已统一迁移到 `agent-assets/`。
- 工具说明文档已统一迁移到 `docs/tools/`。
- Python 工程代码统一放在 `src/ai_test_assistant/`。
- `SQLiteMemoryStore` 支持：
  - `put_memory`
  - `get_memory`
  - `search_memory`
  - `delete_memory`
- `MemoryService` 可从 YAML 配置读取 SQLite 路径。
- `tests/test_memory_store.py` 覆盖写入、读取、搜索、删除、重建实例后的持久化读取。

## 待验证

- Windows 之外环境的 SQLite 文件行为。
- 更大数据量下的搜索性能。
- 后续多模块并发访问时的锁竞争行为。

## 待接入

- intent router
- orchestrator
- tool registry
- runtime CLI
- LangGraph / MCP 的真实接入

## 受限能力

- 当前搜索不是语义检索，只是 namespace 内文本匹配和简单过滤。
- 当前没有工具执行能力。
- 当前没有任务编排能力。
