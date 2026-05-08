# Skills Index

本文件索引 `skills/` 中可复用的测试工程能力方法。每个子目录代表一个明确能力，优先使用 `SKILL.md` 作为入口。

当前能力：

| 目录 | 用途 |
| --- | --- |
| `requirement-analysis/` | 需求分析、规则拆解、风险识别 |
| `test-case-generation/` | 测试用例生成 |
| `log-analysis/` | 日志分析和问题定位 |
| `bug-report/` | 缺陷报告整理 |
| `api-testing/` | API 测试设计工作流 |
| `defect-analysis/` | 缺陷分析工作流 |
| `ui-automation/` | UI 自动化测试设计工作流 |
| `regression-selection/` | 代码变更驱动精准回归 |
| `failure-analysis/` | 自动化失败归因、证据链和重跑建议 |

边界：

- Skill 只沉淀方法、步骤、输入输出和检查清单。
- 不在 Skill 中写死具体公司业务规则。
- 不在 Skill 中开放 `shell`、`filesystem_write` 或 `github_write`。
- 新增或修改 Skill 前必须先阅读 `docs/architecture/agentic-qa-blueprint.md` 和 `references/research/agentic-qa-research-guide.md`。
- 非必要情况不得把 Skill 扩展成自研平台或执行器。
