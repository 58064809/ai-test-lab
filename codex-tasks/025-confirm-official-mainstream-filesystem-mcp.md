# Codex Task 025：确认官方 / 主流生态 filesystem MCP Server

## 任务背景

用户已明确选择：优先确认 **官方或主流生态中的 filesystem MCP server**。

当前已有：

- `023-filesystem-mcp-selection-and-minimal-integration-plan.md`
- `024-filesystem-mcp-manual-confirmation-checklist.md`
- `docs/filesystem-mcp-selection.md`
- `docs/filesystem-mcp-minimal-integration-plan.md`
- `docs/filesystem-mcp-manual-checklist.md`

本任务目标：在不写接入代码的前提下，把候选范围收敛到“官方 / 主流生态 filesystem MCP server”，并形成推荐结论。

## 最高原则

1. 不造轮子。
2. 不继续扩展本地 `LocalFilesystemReadAdapter`。
3. 不实现 MCP client。
4. 不调用 MCP SDK。
5. 不运行 MCP Server。
6. 不执行 shell 命令。
7. 不开放 filesystem_write。
8. 不把任何 MCP 工具改成 enabled。
9. 不编造 star、release、维护状态、许可证、Windows 支持等事实。
10. 如果无法确认，必须写“待人工确认”。
11. Markdown 文档默认中文。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/012-industrial-grade-selection-policy.md`
- `codex-tasks/017-mcp-selection-and-security-boundary.md`
- `codex-tasks/022-pause-021-and-return-to-mature-tooling.md`
- `codex-tasks/023-filesystem-mcp-selection-and-minimal-integration-plan.md`
- `codex-tasks/024-filesystem-mcp-manual-confirmation-checklist.md`
- `docs/filesystem-mcp-selection.md`
- `docs/filesystem-mcp-minimal-integration-plan.md`
- `docs/filesystem-mcp-manual-checklist.md`
- `docs/mcp-selection.md`
- `docs/mcp-security-policy.md`
- `configs/tools.yaml`

## 已知初步搜索信息

GitHub 初步搜索中出现了以下候选或相关结果，但不能直接视为已确认：

- `cyanheads/filesystem-mcp-server`
- `codemaestroai/filesystem-mcp`
- `modelcontextprotocol/csharp-sdk`，仅说明存在 `modelcontextprotocol` 官方组织，并不等价于 filesystem server
- 其他零散社区仓库

注意：这些只是搜索结果，不代表最终推荐。

优先确认的方向应该是：

1. 是否存在 Model Context Protocol 官方组织维护的 filesystem server。
2. 是否存在官方 npm 包，例如 `@modelcontextprotocol/server-filesystem` 或等价官方包。
3. 是否存在主流 AI IDE / Agent 生态内置或推荐的 filesystem MCP server。
4. 若官方方案存在，优先官方方案。
5. 若官方方案不满足 Windows / 只读 / 根目录限制，再考虑主流社区方案。

## 任务一：更新候选收敛文档

新增：

```text
docs/filesystem-mcp-official-mainstream-confirmation.md
```

文档必须包含：

```text
确认目标：
优先级原则：
官方候选：
主流生态候选：
社区候选降级条件：
已排除项：
事实确认表：
推荐结论：
未确认风险：
下一步是否允许进入最小接入验证：
```

## 任务二：事实确认表

事实确认表字段至少包括：

```text
候选名称
来源类型：官方 / 主流生态 / 社区
仓库地址或包地址
证据来源
是否确认存在
star
最近 release / commit
维护状态
许可证
Windows 支持
安装方式
是否支持只读模式
是否支持限制仓库根目录
是否可以禁用写能力
是否支持敏感路径过滤
是否适合第一阶段 filesystem_read
确认状态
结论
```

要求：

- 如果当前环境不能联网确认，字段写“待人工确认”。
- 不得编造 star、release、commit、许可证。
- 对官方候选和主流生态候选优先整理。
- 社区候选只作为备选，不作为第一推荐，除非官方 / 主流生态不可用。

## 任务三：推荐结论

请在文档中给出阶段性推荐：

```text
推荐方案：
推荐级别：推荐 / 暂缓 / 不推荐
推荐理由：
不能直接接入的原因：
第一阶段允许能力：filesystem_read only
第一阶段禁止能力：filesystem_write / shell / 自动多文件读取 / 目录读取 / glob
需要人工确认的问题：
是否允许进入 026 最小接入验证任务：是 / 否 / 待确认
```

如果官方候选无法确认，推荐结论必须是“暂缓”，不能强行推荐社区仓库。

## 任务四：更新状态文档

更新：

- `docs/current-status.md`
- `docs/next-steps.md`
- `docs/filesystem-mcp-manual-checklist.md`

要求：

- 明确用户选择优先确认官方 / 主流生态 filesystem MCP server。
- 明确 025 只做候选收敛，不做接入。
- 不得写成已经接入 MCP。
- 不得把 `filesystem_mcp_read` 改成 enabled。

## 任务五：新增一致性测试

新增或更新：

```text
tests/test_filesystem_mcp_official_confirmation.py
```

测试要求：

1. `docs/filesystem-mcp-official-mainstream-confirmation.md` 存在。
2. 文档包含“官方候选”“主流生态候选”“事实确认表”“推荐结论”。
3. 文档包含“不继续扩展 LocalFilesystemReadAdapter”或等价表述。
4. 文档不得出现“已接入 filesystem MCP”。
5. `configs/tools.yaml` 中 `filesystem_mcp_read` 仍不是 enabled。
6. `filesystem_write` 仍是 disabled。
7. `shell` 仍是 disabled。

## 禁止事项

- 不要实现 MCP client。
- 不要调用 MCP SDK。
- 不要运行 MCP Server。
- 不要执行 shell 命令。
- 不要改 runtime CLI 行为。
- 不要扩展 `LocalFilesystemReadAdapter`。
- 不要实现多文件读取。
- 不要实现目录读取。
- 不要实现 glob / 通配符读取。
- 不要开放 filesystem_write。
- 不要把任何 MCP 工具改成 enabled。
- 不要编造未确认事实。

## 验收命令

```bash
pytest
```

## 完成标准

- 官方 / 主流生态候选范围收敛完成。
- 文档明确哪些事实已确认，哪些仍待人工确认。
- 不强行推荐未验证社区仓库。
- 未实现任何 MCP 接入代码。
- 未启用任何 MCP 工具。
- 所有测试通过。
