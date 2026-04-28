# Current Status

## 已实现

- `memory` 最小可运行底座已落地。
- `intent router` 最小可运行底座已落地。
- orchestrator 工业级选型说明已完成，正式目标方案选择为 LangGraph。
- LangGraph 最小 orchestrator 骨架已落地，支持 dry-run 计划生成。
- tool registry 与权限模型底座已落地。
- 最小 runtime CLI 已落地，支持 intent-only 与 dry-run 入口。
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
- `IntentRouter` 支持基于配置化规则、关键词、置信度和澄清策略进行意图识别。
- `tests/test_intent_router.py` 覆盖 12 类 intent 路由、模糊输入澄清和配置异常场景。
- `TaskOrchestrator` 支持最小流程：
  - `receive_task`
  - `load_memory`
  - `classify_intent`
  - `select_workflow`
  - `prepare_context`
  - `plan`
  - `review`
  - `write_memory`
- `tests/test_orchestrator_smoke.py` 覆盖 dry-run、澄清和非执行边界。
- `ToolRegistry` 支持工具配置加载、状态查询和权限判定。
- `tests/test_tool_registry.py` 覆盖注册表加载、状态风险检查和权限边界。
- `runtime CLI` 支持 `task_text`、`--dry-run`、`--intent-only`、`--write-memory`、`--config`。
- `tests/test_runtime_cli.py` 覆盖启动、intent-only、dry-run、澄清提示和配置异常。

## 待验证

- Windows 之外环境的 SQLite 文件行为。
- 更大数据量下的搜索性能。
- 后续多模块并发访问时的锁竞争行为。

## 待接入

- MCP 的真实接入

## 受限能力

- 当前搜索不是语义检索，只是 namespace 内文本匹配和简单过滤。
- 当前 intent 不是复杂 NLP，只是规则匹配。
- 当前 intent 不调用外部 LLM。
- 当前 orchestrator 只实现最小 LangGraph 骨架，不包含 checkpointer、HITL、工具执行和复杂状态流。
- 当前 tool registry 只做注册与权限判定，不执行本地命令，不访问外部网络，也不接入真实 MCP Server。
- 当前 runtime CLI 只允许调用 intent-only 和 orchestrator dry-run 能力，不开放真实工具执行。
