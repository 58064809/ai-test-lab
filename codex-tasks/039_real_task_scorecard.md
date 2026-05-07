# 039｜Codex 任务：真实任务跑测与评分表

## 任务目标

基于 `examples/real_tasks/` 中的 038 真实任务验证包，生成或确认 `039｜真实任务跑测与评分表`，用于人工逐项验证当前个人 AI 测试助手的输出质量。

当前阶段不要求自动调用外部 AI，也不要求真正批量执行所有任务。目标是整理可执行的跑测流程、评分记录结构和后续沉淀建议。

## 前置输入

请查看以下文件，如果不存在，请先根据 `codex-tasks/038_real_task_validation_pack.md` 创建 038：

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
```

## 需要创建或确认的文件

请确保以下文件存在；如果不存在则创建，如果已存在则检查内容是否完整，必要时补齐：

```text
examples/real_tasks/039_real_task_scorecard.md
```

## 039 文件内容要求

`examples/real_tasks/039_real_task_scorecard.md` 必须包含：

1. 任务目标；
2. 跑测范围；
3. 使用方式；
4. 评分规则；
5. 单任务评分表；
6. 字段说明；
7. 结论判定标准；
8. 后续动作判断；
9. 跑测记录模板；
10. 验收标准。

## 跑测范围

必须覆盖 038 的 8 个任务：

| 编号 | 任务文件 | 验证能力 |
| --- | --- | --- |
| 1 | `001_requirement_analysis.md` | 需求分析 |
| 2 | `002_test_case_generation.md` | 测试用例生成 |
| 3 | `003_log_analysis.md` | 日志分析 |
| 4 | `004_pytest_allure_summary.md` | pytest + Allure 报告总结 |
| 5 | `005_codex_change_review.md` | Codex 修改结果审查 |
| 6 | `006_api_test_design.md` | 接口测试设计 |
| 7 | `007_failed_test_to_bug_report.md` | 失败测试结果生成缺陷报告 |
| 8 | `008_tool_integration_evaluation.md` | 成熟工具接入评估 |

## 评分规则

每项 0～5 分：

| 分数 | 含义 |
| --- | --- |
| 0 | 完全不可用，偏题或无法执行 |
| 1 | 基本不可用，只有少量相关内容 |
| 2 | 勉强可参考，但缺失明显、需要大量人工改写 |
| 3 | 基本可用，需要少量人工调整 |
| 4 | 比较好，可直接使用或轻微修改后使用 |
| 5 | 很好，专业、完整、结构清晰、可直接沉淀 |

评分项建议包含：

1. 任务理解；
2. 结构化输出；
3. 专业性；
4. 可执行性；
5. 边界遵守；
6. 反空泛能力。

总分建议满分 30 分。

## 结论判定标准

| 总分 | 结论 | 处理建议 |
| --- | --- | --- |
| 27～30 | 优秀 | 可以沉淀为 Prompt、Skill 或模板 |
| 22～26 | 可用 | 可以继续使用，后续小幅优化 |
| 16～21 | 需优化 | 需要调整任务描述或输出约束 |
| 0～15 | 不可用 | 暂不沉淀，先分析失败原因 |

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

## 后续动作判断

| 现象 | 建议动作 |
| --- | --- |
| 多次输出稳定、格式统一、质量高 | 沉淀为 Prompt 或模板 |
| 需要固定角色、规则、步骤、检查清单 | 沉淀为 Skill |
| 涉及多步骤执行、读取文件、运行测试、总结报告 | 沉淀为 Workflow |
| 明显依赖外部能力，例如接口扫描、浏览器操作、Mock、报告生成 | 评估接入成熟工具 |
| 输出经常偏题或泛泛而谈 | 优先优化任务描述，不急着接工具 |

## 项目边界

必须遵守：

1. 不写业务代码；
2. 不新增 runtime 能力；
3. 不接入新工具；
4. 不继续拆 Allure；
5. 不做平台化能力；
6. 不写死当前公司业务；
7. 不开放 `shell` / `filesystem_write` / `github_write`；
8. 只整理真实任务跑测流程和评分记录。

## 验收标准

完成后请输出：

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
