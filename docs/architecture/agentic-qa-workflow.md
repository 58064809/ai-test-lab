# Agentic QA 工作流

本文根据 `docs/architecture/agentic-qa-blueprint.md` 定义当前仓库的 Agentic QA 工作流。实现或扩展前必须先阅读 `references/research/agentic-qa-research-guide.md`。

## 总体流程

```text
需求 / 用户故事 / PR / 缺陷 / 测试报告
        ↓
Agent 读取上下文并识别任务类型
        ↓
Agent 分析风险、范围和缺口
        ↓
Agent 生成测试计划、测试点或执行建议
        ↓
受控工具链读取、执行或汇总结果
        ↓
Agent 分析失败、整理证据链和缺陷草稿
        ↓
人审核关键判断、确认风险和发布建议
        ↓
沉淀用例、规则、评估结果和审计记录
```

## 任务入口

| 输入 | 推荐主 Agent / Skill | 主要输出 |
| --- | --- | --- |
| PRD / 用户故事 / 验收标准 | `skills/requirement-analysis/` | 测试范围、风险点、疑问清单 |
| 需求或变更说明 | `skills/test-case-generation/` | 测试用例、边界场景、异常场景 |
| Git diff / PR 信息 | `skills/regression-selection/` | 精准回归清单、风险级别、执行建议 |
| OpenAPI / 接口文档 | `skills/api-testing/` | API 测试点、接口用例、契约测试建议 |
| 页面说明 / UI 失败截图 | `skills/ui-automation/` | UI 场景、locator 建议、自愈建议 |
| 日志 / 堆栈 / Allure / 请求响应 | `skills/failure-analysis/` | 失败摘要、证据链、根因判断、重跑建议 |
| 测试失败信息 | `skills/bug-report/` | 缺陷草稿、优先级、补充排查信息 |
| 测试执行结果 | `templates/test-summary.md` | 测试总结、风险结论、后续建议 |

## Human-in-the-loop 规则

| 风险级别 | Agent 行为 | 人工要求 |
| --- | --- | --- |
| 低风险 | 可直接生成分析、用例、报告草稿 | 人抽检 |
| 中风险 | 生成执行建议或变更建议 | 人审核后执行 |
| 高风险 | 只输出建议和风险说明 | 人必须确认 |

高风险包括但不限于：写数据、生产环境操作、缺陷自动提交、发布拦截、资金/库存/权限类操作、不可逆操作。

## 工具链原则

- 读、跑、查、报应优先复用成熟工具和官方生态。
- 当前 runtime 只开放受控 pytest、Allure、filesystem MCP read、GitHub MCP read 等既有能力。
- 新增工具前必须先进入 `docs/` 或 `references/` 完成调研和边界设计。
- 不为单个场景自研通用平台或复杂执行器。

## 结果沉淀

| 输出类型 | 沉淀位置 |
| --- | --- |
| 可复用方法 | `skills/` |
| 固定输出格式 | `templates/` |
| 质量评估标准 | `standards/` |
| 外部资料和背景 | `references/` |
| 方案、路线图、治理说明 | `docs/` |
| 真实任务样例 | `examples/` |
