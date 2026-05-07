# 039｜Codex 执行任务：真实任务跑测与评分

## 任务目标

请基于 `examples/real_tasks/` 中的 038 真实任务验证包，执行一次真实任务跑测记录整理。

当前阶段不要求自动调用外部 AI，也不要求真正批量执行所有任务。你的目标是整理可执行的跑测流程、评分记录结构和后续沉淀建议，方便人工逐项验证。

## 输入文件

请查看以下文件：

```text
examples/real_tasks/README.md
examples/real_tasks/001_requirement_analysis.md
examples/real_tasks/002_test_case_generation.md
examples/real_tasks/003_log_analysis.md
examples/real_tasks/004_pytest_allure_summary.md
examples/real_tasks/005_codex_change_review.md
examples/real_tasks/006_api_test_design.md
examples/real_tasks/007_failed_test_to_bug_report.md
examples/real_tasks/008_tool_integration_evaluation.md
examples/real_tasks/039_real_task_scorecard.md
```

## 执行要求

1. 不写业务代码；
2. 不新增 runtime 能力；
3. 不接入新工具；
4. 不继续拆 Allure；
5. 不做平台化能力；
6. 不写死当前公司业务；
7. 不开放 `shell` / `filesystem_write` / `github_write`；
8. 只整理真实任务跑测流程和评分记录。

## 建议输出

请在回复中输出：

1. 039 已覆盖的任务清单；
2. 推荐的跑测顺序；
3. 每个任务重点观察项；
4. 评分表是否完整；
5. 哪些任务更适合后续沉淀为 Prompt；
6. 哪些任务更适合后续沉淀为 Skill；
7. 哪些任务更适合后续沉淀为 Workflow；
8. 哪些任务可能需要成熟工具接入；
9. 是否建议进入 040；
10. 如果建议进入 040，请给出 040 的任务名称和目标。

## 推荐跑测顺序

| 顺序 | 文件 | 目的 |
| --- | --- | --- |
| 1 | `004_pytest_allure_summary.md` | 先验证最简单、边界最明确的报告总结能力 |
| 2 | `007_failed_test_to_bug_report.md` | 验证结构化缺陷报告能力 |
| 3 | `003_log_analysis.md` | 验证日志定位和风险判断能力 |
| 4 | `001_requirement_analysis.md` | 验证需求规则拆解能力 |
| 5 | `002_test_case_generation.md` | 验证大表格测试用例生成能力 |
| 6 | `006_api_test_design.md` | 验证接口测试设计和一致性思维 |
| 7 | `005_codex_change_review.md` | 验证工程修改审查能力 |
| 8 | `008_tool_integration_evaluation.md` | 验证成熟工具选型和接入判断能力 |

## 040 建议方向

如果 039 验证通过，建议下一步进入：

```text
040｜高价值任务沉淀为 Prompt 模板
```

目标：

从 038/039 中挑选最稳定、最高频、最有价值的任务，例如测试用例生成、日志分析、缺陷报告、Allure 总结，沉淀为 `agent-assets/prompts/` 下的可复用 Prompt 模板。
