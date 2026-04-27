# Codex Task 004：实现 orchestrator 任务编排底座

## 任务目标

实现个人 AI 测试助手的任务编排底座。

这不是让你自研任务编排框架，而是优先复用 LangGraph 的 state graph、node、edge、checkpoint 设计。如果当前环境暂不适合直接引入 LangGraph，也必须保持接口和目录结构兼容未来接入。

## 官方依据

LangGraph 官方 persistence 文档说明：编译 graph 时使用 checkpointer，可以在每一步保存图状态 checkpoint，并支持 human-in-the-loop、会话记忆、time travel debugging 和故障恢复。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/001-foundation.md`
- `codex-tasks/002-memory-foundation.md`
- `codex-tasks/003-intent-router.md`
- `tools/langgraph.md`
- `tools/sources.md`

## 实现范围

请实现：

```text
src/ai_test_assistant/orchestrator/
  __init__.py
  state.py
  graph.py
  nodes.py
  policies.py
  README.md

tests/test_orchestrator_smoke.py
```

## 最小流程

必须支持以下节点：

1. receive_task
2. load_memory
3. classify_intent
4. select_workflow
5. prepare_context
6. plan
7. review
8. write_memory

## 状态模型

任务状态至少包含：

- task_text
- dry_run
- intent_result
- loaded_memory
- selected_workflow
- execution_plan
- risk_level
- requires_confirmation
- result
- errors

## dry-run 要求

第一版必须支持 dry-run。

在 dry-run 模式下：

- 只做意图识别、记忆读取、workflow 选择和计划生成。
- 不执行外部工具。
- 不运行测试。
- 不修改业务文件。

## LangGraph 接入要求

优先尝试使用 LangGraph。

如果没有引入 LangGraph，必须在 README 中说明：

- 暂未引入原因。
- 当前接口如何对齐 LangGraph。
- 后续如何替换成真正 LangGraph StateGraph。

## 禁止事项

- 不要自研复杂编排框架。
- 不要做多 Agent 聊天系统。
- 不要跳过 intent router。
- 不要在 dry-run 中执行高风险动作。
- 不要把 workflow markdown 当成真正编排实现。

## 验收命令

```bash
pytest tests/test_orchestrator_smoke.py
python scripts/run_assistant.py "根据这个需求生成测试用例" --dry-run
```

## 完成标准

- smoke test 通过。
- dry-run 能输出任务计划。
- 编排层能调用 memory 和 intent。
- README 明确当前是否已使用 LangGraph。