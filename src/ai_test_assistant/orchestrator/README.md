# Orchestrator 模块说明

## 当前状态

当前模块**尚未实现 orchestrator 代码**。

本阶段只完成工业级选型说明，正式目标方案选择为 **LangGraph**，详见：

- [docs/orchestrator-selection.md](../../../docs/orchestrator-selection.md)

## 已完成

- 已完成 orchestrator 工业级选型
- 已明确第一阶段不手写复杂状态机
- 已明确当前 `intent router` 只是 bootstrap / fallback，不是最终工业级 intent 系统

## 待接入

- LangGraph 依赖
- 最小 state schema
- 最小 graph skeleton
- dry-run 编排流
- review / checkpoint / write_memory 等后续节点

## 当前限制

- 不实现 orchestrator 代码
- 不实现 tool registry
- 不实现 MCP
- 不实现 runtime CLI
- 不实现复杂多 Agent 聊天系统

## 选型结论

正式编排层优先选择 LangGraph，原因是：

- 更适合可控的任务状态流
- 支持 durable execution、human-in-the-loop、persistence
- 比 CrewAI 更轻
- 比 LangChain 高层 Agent 更适合显式编排
- 比 LangGraph Supervisor 更适合作为第一步主方案

## 替换策略

- 当前不自研编排框架
- 后续若只需单助手编排，继续沿 LangGraph 演进
- 未来若出现明确多 agent supervisor 需求，再评估 LangGraph Supervisor 或 CrewAI
