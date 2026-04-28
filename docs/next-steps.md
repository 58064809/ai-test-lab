# Next Steps

## 建议顺序

1. 继续用更多真实任务样本验证当前 `memory + intent router + orchestrator dry-run + tool registry` 的联动是否稳定。
2. 在不扩大能力边界的前提下，为 orchestrator 增加正式执行前的确认分支，而不是直接开放真实工具执行。
3. `021-explicit-multi-file-read-context.md` 已暂停，不继续扩展本地 filesystem 读取能力。
4. 下一步 filesystem 正式能力优先回到成熟 filesystem MCP / 等价成熟工具的前置调研与最小接入验证路线。
5. 调研重点应放在：
   - 是否支持 Windows 本地运行
   - 是否支持只读模式
   - 是否可以限制仓库根目录
   - 是否可以与 `FilesystemReadPolicy` 协同
   - 是否能只开放 `filesystem_read`，不开放 `filesystem_write`
6. 按 `docs/filesystem-mcp-minimal-integration-plan.md` 先做成熟工具的最小接入验证，不继续扩展本地 adapter。
7. 在确认真实需求前，不接入 `shell`、`github_write`、`filesystem_write` 这类高风险 MCP 能力。
8. 评估 LangGraph checkpointer 是否值得接入；如果没有明确收益，不提前复杂化。
9. 在确认真实需求前，不引入向量库或复杂多 Agent 机制。

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
- 当前文件读取上下文只支持显式单文件输入，不应扩展成自然语言自动多文件读取。
- 当前不应继续开发多文件读取、目录读取、glob / 通配符读取、自动上下文收集或文件检索。
- 当前 023 只完成选型与验证方案，不应误读为“已接入成熟 filesystem MCP”。
- 即使继续使用 LangGraph，也不要在 graph 外面再包一层复杂自研状态机。
- 如果后续只需要结构化查询，不应过早引入向量库。
