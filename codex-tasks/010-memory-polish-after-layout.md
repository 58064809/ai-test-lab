# Codex Task 010：目录重构后补齐 memory 遗留修复

## 背景

009 目录结构重构总体方向正确：

- Agent 资产已迁移到 `agent-assets/`
- 工具说明已迁移到 `docs/tools/`
- Python 工程代码保留在 `src/ai_test_assistant/`
- 已新增 `pyproject.toml`
- 已新增 `.gitignore`

但 008 中仍有少量 memory 修复未完成。本任务只补齐这些遗留问题，不实现 intent、orchestrator、tool registry、runtime。

## 必须先阅读

- `codex-tasks/008-memory-review-fixes.md`
- `codex-tasks/009-restructure-project-layout.md`
- `src/ai_test_assistant/memory/README.md`
- `tests/test_memory_store.py`
- `src/ai_test_assistant/memory/sqlite_store.py`

## 修复 1：memory README 需要明确 filter 边界

当前 `src/ai_test_assistant/memory/README.md` 只写了 `search_memory` 支持简单文本匹配和结构化过滤，但没有明确具体支持哪些 filters。

请补充说明：

- 当前 `search_memory` 只支持 `memory_type` 和 `source` 两个 filter。
- 不支持任意 JSON 字段过滤。
- 传入未知 filter 会抛出 `ValueError`。
- 语义检索、向量检索、跨 namespace 检索均未实现。

## 修复 2：补充未知 filter 抛错测试

在 `tests/test_memory_store.py` 中补充测试，验证：

```python
store.search_memory("workflow_memory/api", filters={"unknown": "value"})
```

会抛出 `ValueError`。

要求：

- 使用 pytest 的异常断言。
- 不要为了测试改弱生产代码。
- 不要伪装支持任意 filter。

## 修复 3：测试数据中的旧路径需要更新

当前 `tests/test_memory_store.py` 中仍出现旧路径：

```text
workflows/api-test-workflow.md
```

目录重构后应改为：

```text
agent-assets/workflows/api-test-workflow.md
```

请只更新测试数据中的路径，不改变业务逻辑。

## 修复 4：确认 pyproject 测试配置合理

检查 `pyproject.toml` 中的 pytest 配置是否足以支持 src-layout 下直接运行测试。

如有必要，补充最小配置，但不要引入多余依赖。

## 禁止事项

- 不要实现 intent router。
- 不要实现 orchestrator。
- 不要实现 tool registry。
- 不要实现 runtime CLI。
- 不要引入 LangGraph。
- 不要引入向量库。
- 不要重写 memory 核心逻辑。
- 不要把未实现能力写成已完成。

## 验收命令

```bash
pytest tests/test_memory_store.py
```

## 完成标准

- memory README 明确 filter 边界。
- tests 中有未知 filter 抛错用例。
- tests 中不再出现旧 `workflows/` 路径。
- memory 测试通过。
- 不新增无关功能。