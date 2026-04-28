# Orchestrator 模块说明

## 当前状态

当前模块已实现 **LangGraph 最小 orchestrator 骨架**。

正式目标方案选择为 **LangGraph**，详见：

- [docs/orchestrator-selection.md](../../../docs/orchestrator-selection.md)

## 已完成

- 已完成 orchestrator 工业级选型
- 已使用 LangGraph 表达最小流程
- 已落地最小节点：
  - `receive_task`
  - `load_memory`
  - `classify_intent`
  - `select_workflow`
  - `prepare_context`
  - `plan`
  - `review`
  - `write_memory`
- 已支持 dry-run 任务计划生成
- 已明确当前 `intent router` 只是 bootstrap / fallback，不是最终工业级 intent 系统

## 待接入

- checkpointer / persistence 集成
- review 节点后的人工确认机制
- 非 dry-run 执行层
- tool registry 集成
- runtime CLI 集成
- 更细粒度的状态 schema 和风险策略

## 当前限制

- 当前只做最小线性 graph，不做复杂多 Agent 编排
- 当前 dry-run 只生成计划，不执行外部工具
- 当前非 dry-run 仍然只生成计划，不开放真实执行
- 当前不实现 tool registry
- 当前不实现 MCP
- 当前不实现 runtime CLI
- 当前不实现复杂多 Agent 聊天系统

## 选型结论

正式编排层优先选择 LangGraph，原因是：

- 更适合可控的任务状态流
- 支持 durable execution、human-in-the-loop、persistence
- 比 CrewAI 更轻
- 比 LangChain 高层 Agent 更适合显式编排
- 比 LangGraph Supervisor 更适合作为第一步主方案

## 替换策略

- 当前不自研编排框架，直接以 LangGraph graph 作为正式编排表达
- 后续若只需单助手编排，继续沿 LangGraph 演进
- 未来若出现明确多 agent supervisor 需求，再评估 LangGraph Supervisor 或 CrewAI
