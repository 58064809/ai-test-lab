# Next Steps

## 建议顺序

1. 先用真实任务验证 `memory + intent router` 的配合是否足够稳定。
2. 以 LangGraph 为正式目标方案，实现 `orchestrator` 最小状态流，调用现有 `MemoryService` 和 `IntentRouter`。
3. 第一轮 orchestrator 只实现最小 graph skeleton、dry-run 流程和可替换接口，不扩展成自研编排框架。
4. 后续新增 Agent 资产统一放在 `agent-assets/`。
5. 后续工具说明统一放在 `docs/tools/`。

## 待接入项

- 待接入：`orchestrator` 最小状态流
- 待接入：工具注册和权限模型
- 待接入：runtime CLI

## 风险提醒

- 如果后续没有真实复杂流程，不应为了完整感提前引入 LangGraph。
- 即使后续接入 LangGraph，也不要把 graph 外面再包一层复杂自研状态机。
- 如果后续只需要结构化查询，不应过早引入向量库。
