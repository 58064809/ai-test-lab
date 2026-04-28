# Next Steps

## 026 filesystem MCP quickstart 之后

- 下一步不再继续写复杂选型文档，继续围绕 `@modelcontextprotocol/server-filesystem` 保持最小接入准备。
- 本地环境前置依赖和验证命令已经落文档，当前 Node.js / npm / npx 已完成本地验证。
- 用户本地已验证 `npx -y @modelcontextprotocol/server-filesystem .` 可启动，后续不再重复做选型分支。
- 在 Python runtime 还没有 MCP client 之前，`filesystem_mcp_read` 继续保持 `planned`。
- 不扩展 `LocalFilesystemReadAdapter`，不实现多文件读取、目录读取或 `glob`，不开放 `filesystem_write`，不修改 runtime CLI。

## 025 filesystem MCP 官方 / 主流确认后的下一步

- 先补齐 `docs/filesystem-mcp-official-mainstream-confirmation.md` 中剩余待人工确认项，重点是只读模式、禁写能力和敏感路径边界。
- 在这些关键安全项没有确认前，不进入 026 的最小接入代码实现。
- 如果官方 / 主流生态路线最终无法满足第一阶段 `filesystem_read only`，再降级评估社区方案，而不是直接扩展本地 adapter。

## 建议顺序

1. 继续用更多真实任务样本验证当前 `memory + intent router + orchestrator dry-run + tool registry` 的联动是否稳定。
2. 在不扩大能力边界的前提下，为 orchestrator 增加正式执行前的确认分支，而不是直接开放真实工具执行。
3. `021-explicit-multi-file-read-context.md` 已暂停，不继续扩展本地 filesystem 读取能力。
4. 下一步 filesystem 正式能力优先回到成熟 filesystem MCP / 等价成熟工具的前置调研与最小接入验证路线。
5. 在最小接入前，必须先按 `docs/filesystem-mcp-manual-checklist.md` 完成人工确认，不得跳过。
6. 调研重点应放在：
   - 是否支持 Windows 本地运行
   - 是否支持只读模式
   - 是否可以限制仓库根目录
   - 是否可以与 `FilesystemReadPolicy` 协同
   - 是否能只开放 `filesystem_read`，不开放 `filesystem_write`
7. 按 `docs/filesystem-mcp-minimal-integration-plan.md` 先做成熟工具的最小接入验证，不继续扩展本地 adapter。
8. 在确认真实需求前，不接入 `shell`、`github_write`、`filesystem_write` 这类高风险 MCP 能力。
9. 评估 LangGraph checkpointer 是否值得接入；如果没有明确收益，不提前复杂化。
10. 在确认真实需求前，不引入向量库或复杂多 Agent 机制。

## 待接入项

- 待接入：MCP 真实接入
- 待接入：真实工具执行层
- 待接入：orchestrator 正式执行分支
- 待接入：tool registry 与 orchestrator 的正式执行授权联动
- 待接入：更系统化的真实任务样本库扩展

## 风险提醒

- 当前 `intent router` 仍然只是 bootstrap / fallback 规则路由，不应包装成工业级语义理解系统。
- 当前 `orchestrator` 仍然只是最小 dry-run 骨架，即使已经接入 tool registry 授权联动，也不应包装成完整执行平台。
- 当前 MCP 规划文档不代表真实接入，不应把 planned 工具包装成 enabled。
- 当前 filesystem_read 本地 adapter 不代表已接入 filesystem MCP，也不应扩展成通用文件管理器。
- 当前 filesystem MCP server 方案已经收敛到 `@modelcontextprotocol/server-filesystem`，但这不代表 Python runtime 已完成真实 MCP 接入。
- 当前文件读取上下文只支持显式单文件输入，不应扩展成自然语言自动多文件读取。
- 当前不应继续开发多文件读取、目录读取、glob / 通配符读取、自动上下文收集或文件检索。
- 当前 023 只完成选型与验证方案，不应误读为“已接入成熟 filesystem MCP”。
- 即使继续使用 LangGraph，也不要在 graph 外面再包一层复杂自研状态机。
- 如果后续只需要结构化查询，不应过早引入向量库。
