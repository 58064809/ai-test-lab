# Codex Task 022：暂停 021，回到成熟工具接入路线

## 任务背景

当前仓库已经有：

- `019-filesystem-read-local-adapter.md`：本地单文件只读 adapter
- `020-filesystem-read-output-control-and-context.md`：文件读取输出收敛与 dry-run 上下文接入
- `021-explicit-multi-file-read-context.md`：显式多文件只读上下文支持任务单

但 `021` 暂未执行。

经审查，继续执行 `021` 会把当前本地 `LocalFilesystemReadAdapter` 继续扩展成多文件上下文系统，存在逐步自研文件上下文能力的倾向。

这不符合项目最高原则：不造轮子，正式能力优先复用成熟工具、成熟协议、成熟生态。

本任务用于明确：**暂停 021，不继续扩展本地 filesystem 读取能力；后续回到成熟 filesystem MCP 或等价成熟工具接入路线。**

## 当前结论

- `019` / `020` 已有能力可以保留。
- `LocalFilesystemReadAdapter` 只作为 bootstrap / fallback。
- 不执行 `021`。
- 不新增多文件读取。
- 不新增目录读取。
- 不新增 glob / 通配符读取。
- 不新增自动上下文收集。
- 不把本地 adapter 扩展成通用文件上下文系统。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/012-industrial-grade-selection-policy.md`
- `codex-tasks/017-mcp-selection-and-security-boundary.md`
- `codex-tasks/018-filesystem-read-design-and-safe-adapter.md`
- `codex-tasks/019-filesystem-read-local-adapter.md`
- `codex-tasks/020-filesystem-read-output-control-and-context.md`
- `codex-tasks/021-explicit-multi-file-read-context.md`
- `docs/mcp-selection.md`
- `docs/mcp-security-policy.md`
- `docs/filesystem-read-design.md`
- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/filesystem/README.md`

## 任务目标

本任务只做文档和路线收口，不新增代码功能。

请更新：

- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/filesystem/README.md`
- 如有必要，更新 `README.md`

必须明确写清楚：

1. `LocalFilesystemReadAdapter` 是 bootstrap / fallback，不是长期正式 filesystem 能力。
2. `021-explicit-multi-file-read-context.md` 已暂停，不应执行。
3. 本地 adapter 不继续扩展为多文件读取、目录读取、自动上下文收集或文件检索系统。
4. 后续正式 filesystem 能力优先接入成熟 filesystem MCP 或等价成熟工具。
5. 当前仍未接入 MCP Server。
6. 当前仍不支持写文件。
7. 当前仍不执行 shell 命令。
8. 当前仍不访问外部网络。

## 下一步正确路线

下一步不要开发新的本地文件系统能力，而是新增成熟工具接入前置调研任务，重点确认：

1. 官方或高质量开源 filesystem MCP 方案有哪些。
2. 是否支持 Windows 本地运行。
3. 是否支持只读模式。
4. 是否可以限制仓库根目录。
5. 是否可以和当前 `FilesystemReadPolicy` 协同。
6. 是否能通过 MCP 标准协议接入，而不是继续扩展本地 adapter。
7. 最小接入时如何只开放 `filesystem_read`，不开放 `filesystem_write`。

## 禁止事项

- 不要执行 021。
- 不要实现多文件读取。
- 不要实现目录读取。
- 不要实现 glob / 通配符读取。
- 不要实现自动上下文收集。
- 不要实现文件检索。
- 不要接入 MCP Server。
- 不要调用 MCP SDK。
- 不要开放 filesystem_write。
- 不要执行 shell 命令。
- 不要访问外部网络。
- 不要新增代码功能。

## 验收命令

```bash
pytest
```

## 完成标准

- 文档明确 021 暂停。
- 文档明确本地 filesystem adapter 只是 bootstrap / fallback。
- next steps 回到成熟 filesystem MCP / 等价成熟工具的选型与最小接入验证路线。
- 不新增任何代码功能。
- 现有测试继续通过。
