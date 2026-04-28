# Next Steps

## 建议顺序

1. 先用真实任务样本验证当前 `memory + intent router + orchestrator dry-run` 的配合是否足够稳定。
2. 在不扩大能力边界的前提下，为 orchestrator 增加正式执行前的确认分支，而不是直接开放真实工具执行。
3. 让 orchestrator 与 `tool registry` 做更细粒度联动，基于工具状态和风险级别决定“允许 / 拒绝 / 待确认”。
4. 评估 LangGraph checkpointer 是否值得接入；如果没有明确收益，不提前复杂化。
5. 在确认真实需求前，不引入 MCP Server、向量库或复杂多 Agent 机制。

## 待接入项

- 待接入：MCP 真实接入
- 待接入：真实工具执行层
- 待接入：orchestrator 正式执行分支
- 待接入：tool registry 与 orchestrator 的正式授权联动

## 风险提醒

- 当前 `intent router` 仍然只是 bootstrap / fallback 规则路由，不应包装成工业级语义理解系统。
- 当前 `orchestrator` 仍然只是最小 dry-run 骨架，不应包装成完整执行平台。
- 即使继续使用 LangGraph，也不要在 graph 外面再包一层复杂自研状态机。
- 如果后续只需要结构化查询，不应过早引入向量库。
