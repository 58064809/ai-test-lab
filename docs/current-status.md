# Current Status

## 已实现

- `memory` 最小可运行底座已落地。
- `intent router` 最小可运行底座已落地。
- orchestrator 工业级选型说明已完成，正式目标方案选择为 LangGraph。
- LangGraph 最小 orchestrator 骨架已落地，支持 dry-run 计划生成。
- tool registry 与权限模型底座已落地。
- 最小 runtime CLI 已落地，支持 intent-only 与 dry-run 入口。
- 已新增真实任务样本集与 dry-run 验证器。
- `python scripts/run_assistant.py ...` 已可从仓库根目录直接运行，不依赖测试注入 `src` 路径。
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
- `TaskOrchestrator.run(..., write_memory=False)` 默认不写入 `task_result/orchestrator`。
- 只有显式传 `write_memory=True` 或 CLI 传 `--write-memory` 时，才写入 `task_result/orchestrator`。
- `TaskOrchestrator` 已在 dry-run 阶段接入 tool registry 授权联动，可输出推荐工具、工具状态、风险等级、是否允许执行、是否需要确认和拒绝原因。
- `tests/test_orchestrator_smoke.py` 覆盖 dry-run、澄清和非执行边界。
- `ToolRegistry` 支持工具配置加载、状态查询和权限判定。
- `tests/test_tool_registry.py` 覆盖注册表加载、状态风险检查和权限边界。
- `runtime CLI` 支持 `task_text`、`--dry-run`、`--intent-only`、`--write-memory`、`--config`。
- `tests/test_runtime_cli.py` 覆盖启动、intent-only、dry-run、澄清提示、配置异常、memory 写入开关语义和工具风险提示输出。
- `validation/real-task-samples.yaml` 覆盖 15 类通用测试工程样本。
- `tests/test_validation_samples.py` 覆盖样本加载、12 类主要 intent 验证、模糊输入澄清和 dry-run 工具授权结果。

## 待验证

- Windows 之外环境的 SQLite 文件行为。
- 更大数据量下的搜索性能。
- 后续多模块并发访问时的锁竞争行为。
- 更真实任务文本下的 orchestrator 计划质量与澄清触发阈值。
- tool-intent 映射在更多真实项目中的稳定性。

## 待接入

- MCP 的真实接入。
- 真实工具执行层。
- orchestrator 的正式执行分支。
- 与 tool registry 联动的更细粒度执行授权。
- 如果未来确有收益，再评估 tool registry 到 MCP 真实执行器的适配层。

## 受限能力

- 当前搜索不是语义检索，只是 namespace 内文本匹配和简单过滤。
- 当前 intent 不是复杂 NLP，只是规则匹配。
- 当前 intent 不调用外部 LLM。
- 当前 orchestrator 只实现最小 LangGraph 骨架，不包含 checkpointer、HITL、工具执行和复杂状态流。
- 当前 orchestrator 的 tool registry 联动只做 dry-run 级风险评估，不会触发真实工具。
- 当前 tool registry 只做注册与权限判定，不执行本地命令，不访问外部网络，也不接入真实 MCP Server。
- 当前 runtime CLI 只允许调用 intent-only 和 orchestrator dry-run 能力，不开放真实工具执行。
- 当前默认不写入 `task_result/orchestrator`，需要显式 `--write-memory`。

## 明确不做

- 不自研 MCP 协议。
- 不把规则路由、dry-run 计划或文档占位能力包装成工业级能力。
- 不在当前阶段接入复杂多 Agent 聊天系统。
- 不写死任何电商业务规则。
