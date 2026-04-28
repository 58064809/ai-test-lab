# Codex Task 023：成熟 filesystem MCP / 等价成熟工具选型与最小接入验证方案

## 任务背景

当前仓库已经完成：

- `filesystem_read` 接入前安全策略设计
- `FilesystemReadPolicy` 路径安全策略模型
- `LocalFilesystemReadAdapter` 本地白名单单文件只读 adapter
- `--read-file` 显式单文件读取
- 默认预览输出与 `--show-file-content` 显式完整输出
- `021-explicit-multi-file-read-context.md` 已暂停，不继续扩展本地文件上下文能力

当前 `LocalFilesystemReadAdapter` 只能作为 bootstrap / fallback，不应继续扩展成多文件读取、目录读取、自动上下文收集或文件检索系统。

本任务目标：调研成熟 filesystem MCP / 等价成熟工具，形成最小接入验证方案。

注意：本任务只做选型、验证方案和接入计划，不实现 MCP 接入代码。

## 最高原则

1. 不造轮子。
2. 不继续扩展本地 filesystem adapter。
3. 优先选择官方或 GitHub 高 star、维护活跃、社区成熟、文档完整的 filesystem MCP / 等价成熟工具。
4. 不接入 MCP Server。
5. 不调用 MCP SDK。
6. 不执行本地命令。
7. 不访问外部网络，除非 Codex 当前环境明确允许用于调研；如果不能联网，必须标记为“待人工确认”，不能编造。
8. 不开放 filesystem_write。
9. 不读取真实业务敏感文件。
10. 不把未验证能力写成已完成。
11. Markdown 文档默认中文。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/012-industrial-grade-selection-policy.md`
- `codex-tasks/017-mcp-selection-and-security-boundary.md`
- `codex-tasks/018-filesystem-read-design-and-safe-adapter.md`
- `codex-tasks/019-filesystem-read-local-adapter.md`
- `codex-tasks/020-filesystem-read-output-control-and-context.md`
- `codex-tasks/021-explicit-multi-file-read-context.md`
- `codex-tasks/022-pause-021-and-return-to-mature-tooling.md`
- `docs/mcp-selection.md`
- `docs/mcp-security-policy.md`
- `docs/filesystem-read-design.md`
- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/filesystem/README.md`
- `configs/tools.yaml`

## 任务一：新增 filesystem MCP 选型文档

新增：

```text
docs/filesystem-mcp-selection.md
```

文档必须包含：

```text
候选方案：
信息来源：
选择结果：
选择理由：
未选择方案及原因：
Windows 本地运行支持：
只读模式支持：
仓库根目录限制能力：
写能力禁用方式：
与 FilesystemReadPolicy 的协同方式：
最小接入验证步骤：
风险与限制：
待人工确认项：
后续替换策略：
```

至少评估以下候选类别：

1. 官方或主流 MCP filesystem server。
2. 社区高质量 filesystem MCP server。
3. 现有编辑器 / Agent 生态中的 filesystem 工具能力。
4. 继续使用本地 `LocalFilesystemReadAdapter` 作为 fallback。

要求：

- 不能编造 star 数、release 时间、维护状态。
- 如果 Codex 无法联网确认，必须写“待人工确认”，不能假装已确认。
- 如果引用具体 GitHub 仓库，必须写清仓库地址、当前确认方式和确认时间。
- 必须明确第一阶段只接 `filesystem_read`，不接 `filesystem_write`。
- 必须明确本地 adapter 不继续扩展。

## 任务二：新增最小接入验证方案

新增：

```text
docs/filesystem-mcp-minimal-integration-plan.md
```

该文档只写验证方案，不写代码。

必须包含：

```text
目标：
非目标：
前置条件：
验证环境：
验证命令：
安全边界：
成功标准：
失败回滚：
需要人工确认的问题：
```

最小验证目标：

1. 只验证 filesystem MCP 能否在 Windows 本地运行。
2. 只验证仓库根目录内只读文件读取。
3. 只验证读取 `README.md`、`docs/current-status.md` 等低风险文件。
4. 必须验证 `.env`、`.git/config`、`.assistant/memory.sqlite3` 被拒绝。
5. 必须验证 `filesystem_write` 不启用。
6. 必须验证 runtime CLI 不会自动读取文件。
7. 必须验证写文件、shell、网络仍未开放。

## 任务三：更新工具注册与状态文档，但不启用 MCP

允许更新：

- `configs/tools.yaml`
- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/filesystem/README.md`
- `src/ai_test_assistant/tool_registry/README.md`

要求：

- `filesystem_read` 当前仍可保持 `enabled + read_only + local_python`，但必须明确它是本地 fallback，不是 MCP。
- 可以新增 planned 工具项，例如 `filesystem_mcp_read`，但必须是 `planned` 或 `disabled`，不能 enabled。
- `filesystem_write` 必须保持 disabled。
- `shell` 必须保持 disabled。
- 不得把任何 MCP 工具改成 enabled。
- 文档必须说明 023 只是选型与验证方案，不是接入实现。

## 任务四：新增文档一致性测试

新增或更新：

```text
tests/test_filesystem_mcp_selection_docs.py
```

测试重点：

1. `docs/filesystem-mcp-selection.md` 存在。
2. `docs/filesystem-mcp-minimal-integration-plan.md` 存在。
3. 文档明确包含“只读模式支持”“仓库根目录限制能力”“写能力禁用方式”。
4. 文档明确 `LocalFilesystemReadAdapter` 是 fallback。
5. `configs/tools.yaml` 中所有 MCP filesystem 工具都不是 enabled。
6. `filesystem_write` 仍是 disabled。
7. `shell` 仍是 disabled。
8. 文档中不得出现“已接入 filesystem MCP”这类未实现表述。

## 禁止事项

- 不要实现 MCP client。
- 不要调用 MCP SDK。
- 不要运行任何 MCP Server。
- 不要执行 shell 命令。
- 不要访问外部网络，除非当前环境明确允许用于调研；如果不能联网，写待人工确认。
- 不要改 runtime CLI 行为。
- 不要扩展 `LocalFilesystemReadAdapter`。
- 不要实现多文件读取。
- 不要实现目录读取。
- 不要实现 glob / 通配符读取。
- 不要开放 filesystem_write。
- 不要把 planned 工具改成 enabled。

## 验收命令

```bash
pytest
```

## 完成标准

- filesystem MCP 选型文档完成。
- 最小接入验证方案完成。
- 文档明确正式能力应复用成熟 MCP / 等价成熟工具。
- 文档明确本地 adapter 只是 fallback。
- 未实现任何 MCP 接入代码。
- 未启用任何 MCP 工具。
- 所有测试通过。
