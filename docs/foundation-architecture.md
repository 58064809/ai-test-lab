# Foundation Architecture

## 本轮实现范围

本轮只实现 `memory` 最小可运行底座，不实现 `intent`、`orchestrator`、`tool registry`、`runtime CLI`。

## 已实现

- 包入口：[src/ai_test_assistant/__init__.py](/D:/TestHome/ai-test-lab/src/ai_test_assistant/__init__.py:1)
- memory 数据模型：[src/ai_test_assistant/memory/models.py](/D:/TestHome/ai-test-lab/src/ai_test_assistant/memory/models.py:1)
- store 协议：[src/ai_test_assistant/memory/store.py](/D:/TestHome/ai-test-lab/src/ai_test_assistant/memory/store.py:1)
- SQLite 持久化实现：[src/ai_test_assistant/memory/sqlite_store.py](/D:/TestHome/ai-test-lab/src/ai_test_assistant/memory/sqlite_store.py:1)
- service 胶水层：[src/ai_test_assistant/memory/service.py](/D:/TestHome/ai-test-lab/src/ai_test_assistant/memory/service.py:1)
- 配置文件：[configs/assistant.yaml](/D:/TestHome/ai-test-lab/configs/assistant.yaml:1)
- 单测：[tests/test_memory_store.py](/D:/TestHome/ai-test-lab/tests/test_memory_store.py:1)

## 当前设计

memory 底座遵循 `namespace + key + JSON value` 模型。

每条记录包含：

- `namespace`
- `key`
- `value`
- `memory_type`
- `created_at`
- `updated_at`
- `source`

存储后端使用 SQLite，原因：

- Python 标准库自带 `sqlite3`
- 满足第一轮本地持久化要求
- 不引入向量库或复杂服务

## 已设计但未实现

- 语义搜索
- embedding / vector store
- LangGraph 官方 store 适配器
- 跨 namespace 检索策略
- 并发写入优化

## 明确不做

- 不把 `AGENTS.md` 当 memory 数据库
- 不自研复杂 memory 框架
- 不把业务规则硬编码到 memory 实现

