# Docs Index

`docs/` 只放当前项目的设计、运行、接入、操作和路线图文档。外部工具资料放在 `references/tooling/`，调研资料放在 `references/research/`。

## 分层

| 目录 | 用途 |
| --- | --- |
| `architecture/` | Agentic QA 蓝图、能力地图、工作流、基础架构和 orchestrator 选型 |
| `runtime/` | CLI 示例、当前 runtime 状态、环境前置条件、filesystem read 设计 |
| `integrations/` | MCP、GitHub、filesystem MCP、安全策略和工具接入方案 |
| `operations/` | 交接上下文、人工检查、运行过程记录 |
| `roadmap/` | 后续任务、阶段计划和优先级 |

## 维护规则

- 架构设计进入 `docs/architecture/`。
- runtime 使用与当前能力说明进入 `docs/runtime/`。
- 外部系统或工具接入方案进入 `docs/integrations/`。
- 临时任务记录不进入 `docs/`，完成后应删除或沉淀为正式文档。
- 外部官方资料索引进入 `references/tooling/`。
- Agentic QA 相关实现前必须先读取 `docs/architecture/agentic-qa-blueprint.md` 和 `references/research/agentic-qa-research-guide.md`。
