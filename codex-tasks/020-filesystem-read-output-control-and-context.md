# Codex Task 020：filesystem_read 输出收敛与 dry-run 上下文接入

## 任务背景

019 已经实现 `filesystem_read` 本地白名单只读 adapter，并允许 CLI 通过 `--read-file` 显式读取单个仓库相对路径文件。

审查结论：主体通过，但存在一个需要收敛的问题：

- 当前 `render_orchestrator_result()` 会把允许读取的文件内容完整打印出来。
- 虽然 adapter 有 128KB 上限，且必须显式 `--read-file`，但默认完整输出仍可能过长，也不利于后续作为上下文使用。
- 当前读取结果只是 CLI 旁路展示，没有进入 orchestrator 的 dry-run 上下文模型。

本任务目标：

1. 文件内容默认不完整打印，只展示摘要 / 预览。
2. 允许用户显式选择展示文件内容。
3. 将 `--read-file` 的读取结果作为 dry-run 上下文传入 orchestrator state/result，而不是只在 CLI 输出层旁路展示。
4. 仍然不接入 MCP，不写文件，不执行命令，不访问网络。

## 最高原则

1. 不接入 MCP Server。
2. 不调用 MCP SDK。
3. 不执行本地命令。
4. 不访问外部网络。
5. 不开放 filesystem write。
6. 不自动根据自然语言猜测文件。
7. 不支持批量读取文件。
8. 不默认完整打印文件内容。
9. 不读取黑名单文件。
10. 不把本地 adapter 包装成 MCP 已接入。
11. Markdown 文档默认中文。

## 必须先阅读

- `codex-tasks/019-filesystem-read-local-adapter.md`
- `src/ai_test_assistant/filesystem/adapter.py`
- `src/ai_test_assistant/filesystem/policy.py`
- `src/ai_test_assistant/runtime/cli.py`
- `src/ai_test_assistant/runtime/output.py`
- `src/ai_test_assistant/orchestrator/state.py`
- `src/ai_test_assistant/orchestrator/nodes.py`
- `tests/test_runtime_cli.py`
- `tests/test_filesystem_read_adapter.py`
- `docs/current-status.md`

## 任务一：收敛 CLI 文件内容输出

请调整 runtime 输出策略：

默认情况下，`--read-file README.md` 不再完整打印文件内容。

默认输出只展示：

- 是否请求读取文件
- 是否允许读取
- 归一化路径
- 文件字符数或字节数
- 是否截断
- 结果说明
- 内容预览，例如前 20 行或前 4000 字符，二选一即可

新增 CLI 参数，二选一即可：

方案 A：

```bash
--show-file-content
```

只有传入该参数时才完整展示 adapter 返回的内容。

方案 B：

```bash
--file-preview-lines 20
```

默认只展示指定行数，且不提供完整展示。

推荐方案 A + 默认预览，简单直接。

要求：

- 不传 `--show-file-content` 时，不完整输出文件内容。
- 传 `--show-file-content` 时，也只能展示 adapter 已允许读取的内容。
- 如果文件被拒绝，不展示任何内容。
- `.env`、`.git/`、token/secret/password 路径仍然拒绝。

## 任务二：将读取结果接入 orchestrator dry-run 上下文

当前 CLI 先读取文件，再调用 orchestrator，但读取结果只传给输出函数。

请做最小改造：

1. 在 `OrchestratorState` 中增加可选字段，例如：

```python
input_files: list[dict[str, object]]
```

或等价命名。

2. `TaskOrchestrator.run()` 增加可选参数，例如：

```python
input_files: list[dict[str, object]] | None = None
```

3. CLI 读取文件后，把结构化结果传给 orchestrator。

4. `prepare_context` 或 `plan` 节点需要体现：

- 当前任务包含显式读取文件上下文
- 文件路径
- 是否允许读取
- 是否被截断
- 内容是否已进入上下文

5. `write_memory` 的 summary 中可以记录文件路径和读取状态，但不要把完整文件内容写进 memory。

要求：

- 不要把文件内容写入 `task_result/orchestrator` memory。
- 只记录文件元信息，例如 path、allowed、truncated、content_length、reason。
- 不要因为有文件读取就自动执行任何工具。

## 任务三：更新测试

更新或新增测试，至少覆盖：

1. `--read-file README.md` 默认只展示预览，不完整展示全文。
2. `--read-file README.md --show-file-content` 才展示完整内容。
3. `--read-file .env` 仍拒绝读取，且不展示内容。
4. orchestrator state/result 中包含文件读取元信息。
5. `--write-memory` 时，写入的 task_result memory 只包含文件元信息，不包含完整文件内容。
6. 不传 `--read-file` 时，orchestrator state/result 不包含 input file。

可以使用临时文件或仓库 README 做测试，但不要依赖敏感文件存在。

## 任务四：更新文档

更新：

- `src/ai_test_assistant/runtime/README.md`
- `src/ai_test_assistant/filesystem/README.md`
- `src/ai_test_assistant/orchestrator/README.md`
- `docs/current-status.md`
- `docs/next-steps.md`

必须明确：

- `--read-file` 仍然只支持显式单文件读取。
- 默认只展示预览，不完整打印。
- 只有显式参数才展示完整允许内容。
- 文件内容不会写入 task_result memory。
- 当前仍未接入 MCP Server。
- 当前仍不支持写文件。

## 禁止事项

- 不要接入 MCP Server。
- 不要调用 MCP SDK。
- 不要实现 filesystem_write。
- 不要读仓库外文件。
- 不要读 `.env`、`.git/`、`.assistant/`、密钥、token、密码类文件。
- 不要执行 shell 命令。
- 不要访问外部网络。
- 不要自动根据自然语言猜测并读取多个文件。
- 不要把完整文件内容写入 memory。
- 不要引入复杂 UI。

## 验收命令

```bash
pytest
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --read-file README.md
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --read-file README.md --show-file-content
python scripts/run_assistant.py "请读取环境配置" --dry-run --read-file .env
```

## 完成标准

- 默认文件输出已收敛为预览。
- 显式参数才展示完整允许内容。
- 文件读取结果进入 orchestrator dry-run 上下文。
- task_result memory 不保存完整文件内容。
- 所有测试通过。
- 文档真实同步当前能力边界。