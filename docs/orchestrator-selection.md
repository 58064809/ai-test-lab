# Orchestrator 选型说明

更新时间：2026-04-28

## 背景

当前仓库已经完成：

- `memory` 最小底座
- `intent router` bootstrap / fallback 级规则路由

接下来进入 `004 orchestrator` 阶段时，必须遵守 [codex-tasks/012-industrial-grade-selection-policy.md](../codex-tasks/012-industrial-grade-selection-policy.md)，优先评估成熟方案，而不是直接手写复杂状态机。

本说明只做工业级选型，不代表已经接入 orchestrator。

## 候选方案

### 1. LangGraph

- 官方定位：低层 agent orchestration framework and runtime，强调 long-running、stateful agents、durable execution、human-in-the-loop、persistence。
- 生态成熟度：
  - GitHub `langchain-ai/langgraph` 约 29.3k stars
  - 2026-04-17 仍有最新 release
  - 官方文档完整
- 能力特点：
  - 明确的 graph / node / state / checkpoint 模型
  - 适合“确定性工作流 + agentic 节点”混合编排
  - 可做 dry-run、人工确认、恢复执行、状态持久化

### 2. LangGraph Supervisor

- 官方定位：用于 hierarchical multi-agent system 的 supervisor library。
- 生态成熟度：
  - GitHub `langchain-ai/langgraph-supervisor-py` 约 1.6k stars
  - 官方 README 仍可用
  - 需要 Python >= 3.10
- 能力特点：
  - 适合 supervisor 管理多个子 agent
  - 基于 LangGraph 之上构建

### 3. CrewAI

- 官方定位：组合 Crews 与 Flows 来构建 production-ready multi-agent system。
- 生态成熟度：
  - GitHub `crewAIInc/crewAI` 约 49k stars
  - 2026-04-17 仍有更新
  - 官方文档完整，社区较活跃
- 能力特点：
  - 多 agent 协作、角色化分工、Flow 编排都比较成熟
  - 偏向“crew + flow”工作方式

### 4. LangChain Runnable / Agent 生态

- 官方定位：高层框架，适合快速搭建 agent；官方文档明确说明更高级的 orchestration / controllable workflow 应看 LangGraph。
- 生态成熟度：
  - GitHub `langchain-ai/langchain` 约 134k stars
  - 2026-04-17 仍有 release
  - 文档、社区、生态都很成熟
- 能力特点：
  - 上手快
  - 适合快速做 agent loop
  - 高层抽象较多，编排控制粒度不如 LangGraph

## 选择结果

正式 orchestrator 目标方案选择：**LangGraph**

当前不接入代码，只确定后续正式编排层以 LangGraph 为主方案。

## 选择理由

### 1. 最贴合当前目标

本项目要做的是“个人执行型 AI 测试助手”的任务编排，不是先做多 agent 聊天系统。

需要的正式能力是：

- 状态明确
- 节点可控
- 可插人工确认
- 可做 checkpoint / resume
- 可与 memory、intent、后续 tool registry 集成

LangGraph 的 graph/state/checkpoint 模型与这个目标最贴合。

### 2. 官方推荐路径本身就指向 LangGraph

LangChain 官方文档明确区分：

- 想快速做 agent，可先用 LangChain agent
- 想做更高级、可控、混合 deterministic + agentic workflow，则使用 LangGraph

这意味着 LangGraph 是当前需求下更直接的正式编排层，而不是旁路方案。

### 3. 比直接用 LangChain Agent 更可控

当前仓库后续要落的最小流程并不是一个单纯的 agent loop，而是类似：

`receive_task -> load_memory -> classify_intent -> select_workflow -> prepare_context -> plan -> review -> write_memory`

这种流程天然更适合显式 graph，而不是隐藏在高层 agent runtime 里的多轮循环。

### 4. 比 CrewAI 更轻、更贴近当前阶段

CrewAI 虽然成熟，但它的“Crews + Flows + 多 agent 协作”范式更偏团队式 agent system。

当前项目阶段：

- 还没有正式 tool registry
- 还没有 runtime CLI
- 还没有真实多 agent 分工需求

如果现在直接引入 CrewAI，容易把问题提升成多 agent 系统设计，超出当前最小正式编排目标。

### 5. 比 LangGraph Supervisor 更适合当前第一步

LangGraph Supervisor 的官方 README 已明确说明：对于大多数场景，现在更推荐直接使用 supervisor pattern via tools，而不是优先使用该 library。

这意味着：

- Supervisor 适合后续真的出现多 agent 分层调度需求时再评估
- 当前第一步不应把它当作基础 orchestrator 主方案

## 未选择方案及原因

### LangGraph Supervisor

未作为主方案选择，原因：

- 官方 README 已明确说大多数场景更推荐直接用 supervisor pattern，而不是该库本身
- 当前项目还没有明确的多 agent 分层调度需求
- 现在引入会过早把问题升级为“多 agent supervisor architecture”

保留结论：

- 未来如果确实出现“测试设计 agent / 日志分析 agent / 执行 agent”分层协作，再二次评估
- 当前不是第一阶段主选

### CrewAI

未作为主方案选择，原因：

- 很成熟，但范式更偏 crew / role / collaborative agents
- 对当前“个人执行型测试助手”的第一步正式编排来说偏重
- 容易引入过多多 agent 结构设计，而当前真正缺的是“单助手可控编排”

保留结论：

- 如果未来项目发展为显式多 agent 协作系统，可重新评估
- 当前不作为第一阶段正式 orchestrator 方案

### LangChain Runnable / Agent 生态

未作为主方案选择，原因：

- 它更适合快速启动 agent，而不是作为显式任务编排底座
- 官方文档本身也说明更高级 orchestration 应优先看 LangGraph
- 当前我们需要明确节点、状态和 checkpoint，而不是只需要一个 agent loop

保留结论：

- 可以作为 LangGraph 节点内的辅助构件
- 不作为顶层 orchestrator 主方案

## 当前接入状态

- **已完成**：工业级选型说明
- **待接入**：LangGraph 依赖与最小 graph 骨架
- **未实现**：
  - orchestrator 代码
  - tool registry
  - MCP
  - runtime CLI
  - 复杂多 agent 聊天系统

## 风险与限制

### 1. 当前 intent 只是 fallback

当前 `intent router` 只是 bootstrap / fallback 级规则路由，不应被包装成最终工业级 intent 系统。

这意味着后续 orchestrator 接入时：

- 可以调用当前 intent router
- 但必须明确它是临时上游能力，不是最终语义意图系统

### 2. LangGraph 是低层框架

优点是可控，缺点是：

- 需要自己定义 state schema
- 需要自己设计节点边界
- 需要自己约束 graph 演化

如果没有边界 discipline，仍可能写出“披着 LangGraph 外壳的自研状态机”。

### 3. 依赖新增要克制

本阶段只做选型，不新增依赖。

下一阶段若实现最小代码，优先只引入：

- `langgraph`

是否同时引入 `langchain-core` 或更高层 LangChain 包，需要按最小实现再判断，不预先扩大依赖面。

## 后续替换策略

### 当前策略

- 正式 orchestrator 目标方案：LangGraph
- 当前不写复杂自研状态机
- 当前不把 fallback 方案包装成正式编排框架

### 未来替换 / 升级策略

1. 如果后续只是单助手可控流程，继续以 LangGraph 为主。
2. 如果后续出现明确 supervisor 层级需求，再评估 LangGraph Supervisor 或直接手工 supervisor pattern。
3. 如果后续真的转向重度多 agent 协作系统，再评估 CrewAI 是否更合适。
4. 如果未来只需要某些节点内快速 agent loop，可在 LangGraph 节点内部局部使用 LangChain agent / runnable，而不是替代顶层 graph。

## 是否需要新增依赖

本阶段：**不新增依赖**

下一阶段预期最小新增依赖：

- 候选：`langgraph`

当前不计划新增：

- CrewAI
- LangGraph Supervisor
- LangChain 高层 agent 全家桶

除非下一步最小实现证明必须使用。

## 是否支持 Windows / Python 本地运行

### LangGraph

- 官方文档和 GitHub README 都以 Python 包安装方式提供
- 当前未看到官方文档对 Windows 的限制说明
- 结论：**适合本地 Python / Windows 运行**

说明：Windows 结论基于官方安装方式和无显式限制做出的工程判断，后续仍需本地实际验证。

### LangGraph Supervisor

- README 明确要求 Python >= 3.10
- 也是 Python 包形态
- 结论：**技术上可本地运行，但当前不建议第一阶段接入**

### CrewAI

- 官方文档与 GitHub 都显示其为 Python 生态框架，支持本地安装与运行
- 结论：**可在本地 Python 环境使用，但对当前阶段偏重**

### LangChain Runnable / Agent

- 官方文档明确是 Python 框架并支持本地安装
- 结论：**适合本地运行，但不作为顶层 orchestrator 主方案**

## 是否适合个人执行型 AI 测试助手

### LangGraph：适合

原因：

- 可保持单助手主流程
- 可逐步引入 checkpoint / review / HITL
- 可在不实现复杂平台的前提下，把测试工程任务流程显式化

### LangGraph Supervisor：暂不适合当前第一步

原因：

- 适合分层多 agent
- 当前项目还没到这一步

### CrewAI：当前阶段不适合第一步

原因：

- 适合更重的多 agent 协作
- 当前问题规模还不足以 justify 它的范式重量

### LangChain Runnable / Agent：适合作为局部能力，不适合顶层编排

原因：

- 更适合快速 agent loop
- 不适合作为当前顶层正式编排主方案

## 最终结论

本项目 `004 orchestrator` 阶段的正式工业级目标方案选择为：

**LangGraph**

但当前仅完成选型说明，尚未接入。

后续最小代码实现应只做：

- 最小 state schema
- 最小 graph skeleton
- 最小 dry-run 编排流

而不是手写复杂任务编排框架。

## 参考来源

- LangGraph 官方文档：https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph GitHub：https://github.com/langchain-ai/langgraph
- LangGraph Supervisor GitHub：https://github.com/langchain-ai/langgraph-supervisor
- CrewAI 文档：https://docs.crewai.com/en/introduction
- CrewAI Flows 文档：https://docs.crewai.com/en/concepts/flows
- CrewAI GitHub 组织页：https://github.com/orgs/crewAIInc/repositories
- LangChain 官方文档：https://docs.langchain.com/oss/python/langchain/overview
- LangChain GitHub：https://github.com/langchain-ai/langchain
