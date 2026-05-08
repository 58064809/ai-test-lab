# Agent Catalog

本文件索引 Agentic QA 场景下的 Agent 分身和职责边界。

当前只沉淀角色定义，不实现复杂多 Agent 平台，也不默认同时启用全部 Agent。实际任务应优先选择一个主 Agent，只有风险跨多个测试场景时才引入协同。

## 角色清单

| Agent | 文件 | 负责内容 |
| --- | --- | --- |
| Requirement Analysis Agent | `requirement-analysis-agent.md` | 分析需求、识别风险、提出疑问、判断可测试性 |
| Test Design Agent | `test-design-agent.md` | 生成测试点、测试用例、边界场景、异常场景 |
| API Test Agent | `api-test-agent.md` | 根据接口文档生成 API 测试、契约测试和接口断言 |
| UI Test Agent | `ui-test-agent.md` | 根据页面或流程生成 UI 测试建议和自动化脚本草稿 |
| Failure Analysis Agent | `failure-analysis-agent.md` | 分析日志、截图、报告、堆栈和请求响应 |
| Defect Triage Agent | `defect-triage-agent.md` | 归类缺陷、判断优先级、生成 Bug 草稿 |
| Regression Selection Agent | `regression-selection-agent.md` | 根据代码变更、历史缺陷和风险选择回归范围 |
| Report Agent | `report-agent.md` | 输出测试报告、风险结论和发布建议 |
| Orchestrator | `orchestrator.md` | 负责任务路由、上下文编排、工具调用和结果汇总 |

## 使用规则

1. Agent 只负责专业判断和结构化输出，不替代最终质量负责人。
2. 高风险判断必须进入 Human-in-the-loop。
3. 写操作、生产操作、缺陷提交和发布拦截必须有人确认。
4. 不为了完整感创建复杂多 Agent 平台。
5. 新增 Agent 前必须先阅读 `docs/architecture/agentic-qa-blueprint.md` 和 `references/research/agentic-qa-research-guide.md`。
