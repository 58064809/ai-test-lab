# Codex Task 013：修复 runtime CLI 的 memory 写入开关语义

## 背景

006 runtime CLI 已完成最小入口，但审查发现一个关键问题：

`--write-memory` 当前只是输出层标记，实际 `TaskOrchestrator` 在所有非 intent-only 路径都会执行 `write_memory` 节点并写入 `task_result/orchestrator`。

这会导致：

- 用户没有传 `--write-memory` 时，CLI 输出“任务结果记忆写入：禁止”，但实际已经写入 memory。
- CLI 参数语义和真实行为不一致。
- 后续接入真实工具前，执行边界不够清晰。

本任务只修复 memory 写入开关，不实现 MCP、真实工具执行、外部网络、本地命令执行。

## 必须先阅读

- `codex-tasks/006-runtime-cli-and-tests.md`
- `src/ai_test_assistant/runtime/cli.py`
- `src/ai_test_assistant/orchestrator/graph.py`
- `src/ai_test_assistant/orchestrator/nodes.py`
- `tests/test_runtime_cli.py`
- `tests/test_orchestrator_smoke.py`
- `src/ai_test_assistant/runtime/README.md`

## 修复目标

让 `--write-memory` 真正控制是否写入 task_result memory。

默认行为：

- 不传 `--write-memory`：不写入 `task_result/orchestrator`。
- 传 `--write-memory`：允许写入 `task_result/orchestrator`。
- `--intent-only`：始终不写入 task_result memory。

## 推荐实现方式

优先保持简单：

1. 在 `OrchestratorState` 中增加 `write_memory: bool` 字段。
2. `TaskOrchestrator.run()` 增加参数 `write_memory: bool = False`。
3. 初始 state 写入 `write_memory`。
4. `write_memory` 节点根据 state 判断：
   - 如果 `write_memory=False`，不调用 `MemoryService.put_memory()`，只返回 result summary，并标记 memory 写入被跳过。
   - 如果 `write_memory=True`，才调用 `put_memory()`。
5. `runtime.cli.run_cli()` 调用 `orchestrator.run(..., write_memory=args.write_memory)`。

不要为了这个问题重构整个 graph。

## 测试要求

请补充或修改测试，至少覆盖：

1. CLI 不传 `--write-memory` 时，不写入 `task_result/orchestrator`。
2. CLI 传 `--write-memory` 时，写入 `task_result/orchestrator`。
3. Orchestrator 直接调用 `run(..., write_memory=False)` 时不写入。
4. Orchestrator 直接调用 `run(..., write_memory=True)` 时写入。
5. `--intent-only` 不写入 task_result memory。

可以通过测试用临时 SQLite 数据库验证。

## 文档要求

更新：

- `src/ai_test_assistant/runtime/README.md`
- `src/ai_test_assistant/orchestrator/README.md`
- `docs/current-status.md`

必须明确：

- CLI 默认不写入 task_result memory。
- 只有传 `--write-memory` 才写入。
- 当前仍不执行外部工具、不执行本地命令、不访问外部网络。

## 禁止事项

- 不要实现 MCP。
- 不要实现真实工具执行。
- 不要执行本地命令。
- 不要访问外部网络。
- 不要实现 Web UI。
- 不要扩大 runtime CLI 功能范围。
- 不要把 memory 写入开关写成只影响输出。

## 验收命令

```bash
pytest tests/test_runtime_cli.py tests/test_orchestrator_smoke.py tests/test_tool_registry.py tests/test_intent_router.py tests/test_memory_store.py
```

## 完成标准

- `--write-memory` 语义和真实行为一致。
- 默认 CLI 不写 task_result memory。
- 传 `--write-memory` 才写 task_result memory。
- 文档同步。
- 不新增无关功能。