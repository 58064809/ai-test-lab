# Memory 底座说明

## 已实现

- 基于 SQLite 的本地持久化 memory store。
- 参考 LangGraph / LangChain long-term memory 的 `namespace + key + JSON document` 组织方式。
- 支持以下 memory type：
  - `project_rule`
  - `user_preference`
  - `workflow_memory`
  - `task_result`
  - `tool_capability`
- 提供最小 API：
  - `put_memory`
  - `get_memory`
  - `search_memory`
  - `delete_memory`
- 支持服务层 `MemoryService.from_config()` 从 `configs/assistant.yaml` 加载 SQLite 路径。

## 当前限制

- 当前只实现结构化记忆，不包含语义检索。
- 当前不接入向量库、embedding、reranker。
- 当前 `search_memory` 只支持 namespace 内的简单文本匹配和结构化过滤。
- 当前 `search_memory` 的 filters 只支持 `memory_type` 和 `source`。
- 当前不支持任意 JSON 字段过滤。
- 传入未知 filter 会抛出 `ValueError`。
- 当前未实现跨 namespace 检索。
- 当前没有 LangGraph 官方 store 适配器，后续如确认有必要再接入。

## 待验证 / 待接入

- 待验证：不同操作系统下 SQLite 文件路径与锁行为。
- 待验证：后续 intent / orchestrator 调用时的并发访问模式。
- 待接入：如未来确实存在稳定的长期工作流，再评估 LangGraph store 或 checkpoint 集成。

## 明确不做

- 第一轮不自研 memory 框架。
- 第一轮不把 `AGENTS.md` 当长期记忆数据库。
- 第一轮不写死具体业务规则到 memory 代码。
