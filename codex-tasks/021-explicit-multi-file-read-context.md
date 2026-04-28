# Codex Task 021：显式多文件只读上下文支持

## 任务背景

020 已完成：

- `--read-file` 显式单文件读取
- 默认只展示预览
- `--show-file-content` 才展示完整允许内容
- 文件读取结果已进入 orchestrator dry-run 上下文
- `task_result/orchestrator` memory 只记录文件元信息，不保存完整文件内容

当前限制是：一次只能读取一个文件。真实测试任务中，经常需要显式提供多个低风险上下文文件，例如：

- `README.md`
- `AGENTS.md`
- `docs/current-status.md`
- `configs/intents.yaml`
- `tests/test_runtime_cli.py`

本任务目标：在不扩大安全边界的前提下，支持**显式多文件只读上下文**。

注意：这不是自动检索，也不是自动猜测相关文件，也不是 MCP 接入。

## 最高原则

1. 不接入 MCP Server。
2. 不调用 MCP SDK。
3. 不执行本地命令。
4. 不访问外部网络。
5. 不开放 filesystem write。
6. 不自动根据自然语言猜测文件。
7. 只读取用户通过 CLI 显式传入的路径。
8. 每个文件都必须经过 `FilesystemReadPolicy`。
9. 不读取黑名单文件。
10. 不读取仓库外文件。
11. 不把完整文件内容写入 memory。
12. Markdown 文档默认中文。

## 必须先阅读

- `codex-tasks/019-filesystem-read-local-adapter.md`
- `codex-tasks/020-filesystem-read-output-control-and-context.md`
- `src/ai_test_assistant/filesystem/adapter.py`
- `src/ai_test_assistant/filesystem/policy.py`
- `src/ai_test_assistant/runtime/cli.py`
- `src/ai_test_assistant/runtime/output.py`
- `src/ai_test_assistant/orchestrator/state.py`
- `src/ai_test_assistant/orchestrator/nodes.py`
- `tests/test_runtime_cli.py`
- `docs/current-status.md`
- `src/ai_test_assistant/runtime/README.md`

## 任务一：CLI 支持显式多次传入 --read-file

将当前单个 `--read-file` 扩展为可重复参数，例如：

```bash
python scripts/run_assistant.py "请结合项目状态分析下一步" --dry-run \
  --read-file README.md \
  --read-file docs/current-status.md
```

要求：

- 只支持通过多个 `--read-file` 显式传入。
- 不支持逗号拆分。
- 不支持通配符。
- 不支持目录读取。
- 不自动根据自然语言猜测文件。
- 第一版最多允许 5 个文件。
- 超过 5 个应返回错误或结构化拒绝，推荐 CLI 返回非 0 退出码。

## 任务二：增加总内容上限

当前 adapter 单文件有上限，但多文件还需要总上限。

要求：

- CLI 层或 runtime 层增加总内容上限，例如 256KB。
- 如果读取结果超过总上限，应停止继续读取或截断后续内容。
- 结果必须标记：
  - 哪些文件被读取
  - 哪些文件被跳过或截断
  - 总内容是否超限
- 不要因为总内容超限而读取敏感文件。

推荐实现：

- 单文件仍由 `LocalFilesystemReadAdapter` 负责。
- CLI/runtime 负责最多文件数和总内容大小控制。

## 任务三：orchestrator context 与 memory 继续保持安全

要求：

- `input_files` 支持多个文件。
- `prepare_context` / `plan` 能展示多个文件上下文元信息。
- `write_memory` 仍只写元信息，不写完整内容。
- 每个文件元信息至少包含：
  - requested_path
  - path
  - allowed
  - truncated
  - reason
  - content_length
- 不允许把完整 `content` 写入 memory。

## 任务四：输出收敛

默认输出：

- 每个文件只展示预览。
- 输出总文件数。
- 输出每个文件的允许状态、路径、字符数、是否截断、说明。

`--show-file-content`：

- 仅展示被允许读取的文件内容。
- 仍然必须尊重单文件和总内容上限。
- 被拒绝的文件不展示内容。

## 任务五：更新测试

新增或更新测试，至少覆盖：

1. 单个 `--read-file README.md` 仍兼容。
2. 多个 `--read-file` 可读取多个允许文件。
3. 多个文件中某个是 `.env` 时，该文件被拒绝，其他允许文件仍可展示预览。
4. 超过 5 个 `--read-file` 返回错误。
5. 通配符如 `docs/*.md` 不应被展开，应按普通路径走策略并被拒绝或不存在。
6. 目录路径如 `docs/` 被拒绝。
7. `--show-file-content` 时只展示允许文件内容。
8. `--write-memory` 时 memory 中只保存多个文件元信息，不保存 content。
9. 不传 `--read-file` 时行为保持不变。

## 任务六：更新文档

更新：

- `src/ai_test_assistant/runtime/README.md`
- `src/ai_test_assistant/filesystem/README.md`
- `src/ai_test_assistant/orchestrator/README.md`
- `docs/current-status.md`
- `docs/next-steps.md`

必须明确：

- `--read-file` 可以重复传入，但只支持显式路径。
- 最多 5 个文件。
- 不支持目录、通配符、自动猜测。
- 默认只展示预览。
- `--show-file-content` 才展示完整允许内容。
- 文件内容仍不会写入 memory。
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
- 不要自动根据自然语言猜测文件。
- 不要支持目录递归读取。
- 不要支持 glob 通配符展开。
- 不要把完整文件内容写入 memory。

## 验收命令

```bash
pytest
python scripts/run_assistant.py "请结合项目状态分析下一步" --dry-run --read-file README.md --read-file docs/current-status.md
python scripts/run_assistant.py "请读取环境配置和项目说明" --dry-run --read-file README.md --read-file .env
python scripts/run_assistant.py "请结合项目状态分析下一步" --dry-run --read-file README.md --read-file docs/current-status.md --show-file-content
```

## 完成标准

- 支持最多 5 个显式文件读取。
- 每个文件仍经过安全策略。
- 默认输出仍是预览。
- `--show-file-content` 只展示允许文件内容。
- memory 只保存文件元信息。
- 不接 MCP、不写文件、不执行命令、不访问网络。
- 所有测试通过。