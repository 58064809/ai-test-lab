# Codex Task 002：实现 memory 记忆系统底座

## 任务目标

在 `001-foundation.md` 的基础上，专门实现个人 AI 测试助手的记忆系统底座。

这不是让你自研一套 memory 框架，而是复用 LangGraph / LangChain 的长期记忆思想，做本项目需要的最小胶水层和本地持久化适配。

## 官方依据

优先参考：

- LangChain / LangGraph long-term memory：长期记忆用于跨会话保存和召回信息。
- LangGraph store：长期记忆以 JSON document 保存，并按 namespace + key 组织。
- 官方文档说明 InMemoryStore 适合实验，生产或长期使用应使用 DB-backed store。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/001-foundation.md`
- `docs/tools/langgraph.md`
- `docs/tools/sources.md`

## 实现范围

请实现：

```text
src/ai_test_assistant/memory/
  __init__.py
  models.py
  store.py
  sqlite_store.py
  service.py
  README.md

tests/test_memory_store.py
```

## memory 数据模型

必须支持以下类型：

- project_rule：项目规则
- user_preference：用户偏好
- workflow_memory：工作流经验
- task_result：任务结果
- tool_capability：工具能力与限制

每条 memory 至少包含：

- namespace
- key
- value JSON
- memory_type
- created_at
- updated_at
- source

## 最小 API

必须提供：

- `put_memory(namespace, key, value, memory_type=None, source=None)`
- `get_memory(namespace, key)`
- `search_memory(namespace, query=None, filters=None)`
- `delete_memory(namespace, key)`

## 持久化要求

第一版优先使用 SQLite。

要求：

- 默认数据库路径可配置。
- 程序退出后数据仍可读取。
- value 必须以 JSON 形式保存。
- 不要接入向量库。
- 不要自研 embedding。

## 配置要求

在 `configs/assistant.yaml` 中补充 memory 配置，例如：

```yaml
memory:
  backend: sqlite
  sqlite_path: .assistant/memory.sqlite3
```

## 测试要求

`tests/test_memory_store.py` 至少覆盖：

1. 写入 memory。
2. 读取 memory。
3. 搜索 namespace 下的 memory。
4. 删除 memory。
5. 重新实例化 store 后仍能读取旧数据。

## 禁止事项

- 不要把 `AGENTS.md` 当成长期记忆数据库。
- 不要自研复杂 memory 框架。
- 不要引入向量库作为第一版依赖。
- 不要把业务规则写死在 memory 代码里。
- 不要把未实现的语义搜索写成已完成。

## 验收命令

```bash
pytest tests/test_memory_store.py
```

## 完成标准

- 单测通过。
- SQLite 持久化可用。
- README 明确说明当前只实现结构化记忆，不包含语义检索。
- 代码能被后续 intent 和 orchestrator 调用。
