# Agentic QA 能力地图

本文根据 `docs/architecture/agentic-qa-blueprint.md` 整理当前仓库的 Agentic QA 能力地图，用于判断能力应沉淀到哪个目录，以及哪些能力仍应保持规划状态。

实现或扩展本文前，必须先阅读 `references/research/agentic-qa-research-guide.md`。非必要情况不得自研，应优先复用成熟工具、官方生态和已有 runtime 能力。

## 能力分层

| 能力模块 | 当前承接目录 | 当前状态 | 关键边界 |
| --- | --- | --- | --- |
| 需求与风险分析 | `skills/requirement-analysis/` | 已沉淀方法 | 不能替代产品确认业务规则 |
| 测试设计 | `skills/test-case-generation/`、`templates/test-case.md` | 已沉淀方法和模板 | 不编造字段、状态、页面或业务规则 |
| 精准回归 | `skills/regression-selection/`、`templates/regression_selection_template.md` | 已沉淀方法和模板 | 不能只依赖代码路径判断影响范围 |
| API 测试生成 | `skills/api-testing/` | 已沉淀方法 | 优先评估 OpenAPI、Schemathesis、Pytest，不自研生成器 |
| UI 自动化辅助 | `skills/ui-automation/` | 已沉淀方法 | 浏览器 Agent 仅辅助探索，自愈建议必须人工审核 |
| 自动化执行 | `src/ai_test_assistant/testing/`、`references/tooling/qa-automation/pytest-allure.md` | 已有受控 pytest / Allure 链路 | 不开放通用 shell，不开放任意参数 |
| 失败智能分析 | `skills/failure-analysis/`、`templates/failure_analysis_template.md` | 已沉淀方法和模板 | 区分事实、推断和待确认项 |
| 缺陷归类 | `skills/bug-report/`、`skills/defect-analysis/`、`templates/bug-report.md` | 已沉淀方法和模板 | 缺陷提交建议由人最终确认 |
| 质量报告 | `templates/test-summary.md` | 已有基础模板 | 发布结论必须绑定证据和质量门禁 |
| AI 输出评估 | `standards/ai_output_evaluation_standard.md` | 已有基础标准 | 评估结果应反哺 Prompt / Skill / Workflow |
| 权限与审计 | `configs/registry/tools.yaml`、`docs/integrations/mcp-security-policy.md` | 已有基础边界 | 生产操作默认禁止，写操作强审批 |

## 优先闭环

当前优先验证三个闭环：

1. 需求到测试用例  
   目标是提升测试设计效率和覆盖完整性。

2. 代码变更到精准回归  
   目标是解决回归范围不清、回归成本过高的问题。当前最推荐优先落地。

3. 自动化失败到根因分析  
   目标是减少自动化失败定位时间，降低误报和维护成本。

## 不做事项

- 不自研复杂测试平台。
- 不自研浏览器 Agent、API 测试生成器、报告平台或 workflow engine。
- 不把商业产品宣传语直接写成仓库事实。
- 不把具体公司业务规则写死进通用能力。
- 不开放 `shell`、`filesystem_write`、`github_write` 作为通用能力。
