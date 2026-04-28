# Next Steps

## 建议顺序

1. 继续用更多真实任务样本验证当前 `memory + intent router + orchestrator dry-run + tool registry` 的联动是否稳定。
2. 在不扩大能力边界的前提下，为 orchestrator 增加正式执行前的确认分支，而不是直接开放真实工具执行。
3. 按 `docs/mcp-selection.md` 的顺序，只优先评估 `filesystem_read`、`database_readonly`、`redis_readonly`、`github_read` 这类低副作用能力。
4. 如果后续评估 `filesystem_read` 真实接入，先让 adapter 严格复用 `docs/filesystem-read-design.md` 和 `FilesystemReadPolicy` 的边界。
5. 在确认真实需求前，不接入 `shell`、`github_write`、`filesystem_write` 这类高风险 MCP 能力。
6. 评估 LangGraph checkpointer 是否值得接入；如果没有明确收益，不提前复杂化。
7. 在确认真实需求前，不引入向量库或复杂多 Agent 机制。

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
- 当前 filesystem_read 策略模型不代表真实文件读取能力，不应包装成已接入的 filesystem MCP。
- 即使继续使用 LangGraph，也不要在 graph 外面再包一层复杂自研状态机。
- 如果后续只需要结构化查询，不应过早引入向量库。
