# Next Tasks

本文档记录当前 Agentic QA 主线的后续任务优先级。所有任务以 `docs/architecture/agentic-qa-blueprint.md` 为准，实施前必须先阅读 `references/research/agentic-qa-research-guide.md`。

原则：

- 非必要情况不得自研。
- 优先复用成熟工具、官方生态和当前已有 runtime 能力。
- 先验证 1 到 2 个高价值闭环，再考虑工具链扩展。
- 不开放 `shell`、`filesystem_write`、`github_write`。
- 不把具体公司业务规则写死到通用能力中。

## P0

- 代码变更驱动精准回归首轮验证：使用 `skills/regression-selection/` 和 `templates/regression_selection_template.md`，基于模拟 Git diff / PR 信息输出回归清单和风险级别。
- 自动化失败分析首轮验证：使用 `skills/failure-analysis/` 和 `templates/failure_analysis_template.md`，基于 pytest / Allure / 日志样例输出失败摘要、证据链和重跑建议。
- AI 输出评分回收：继续使用 `examples/real_tasks/039_real_task_scorecard.md`，判断哪些任务适合沉淀为 Skill、Template 或 Workflow。
- 文档一致性维护：保持 `README.md`、`AGENTS.md`、`docs/architecture/agentic-qa-capability-map.md`、`docs/architecture/agentic-qa-workflow.md` 与蓝图一致。

## P1

- GitHub PR / Issue 只读评估：只评估官方 GitHub MCP 或成熟只读能力，不开放写操作。
- Playwright MCP 只读页面分析：只评估页面结构、可访问性快照、控制台错误和网络请求，不做高风险业务动作。
- Schemathesis 评估：基于 OpenAPI 文档验证契约测试生成价值，先沉淀样例和边界，再决定是否接入 runtime。
- 质量门禁基础规则：沉淀发布风险判断、阻塞条件、人工确认规则和证据要求。

## P2

- 数据库只读 MCP：评估只读账号、白名单库表、结果脱敏、查询超时和审计输出。
- Redis 只读 MCP：评估 key 检查、TTL、value 摘要、敏感值屏蔽和命名空间限制。
- LangGraph checkpointer / HITL：仅在真实任务验证稳定后评估，不扩展成复杂多 Agent 平台。
- ReportPortal 等质量分析平台调研：只做成熟工具评估，不自研测试报告平台。
