# 新聊天上下文交接说明

## 这份文档的用途

用于在 ChatGPT 项目 `AI-助手` 中开启新聊天时快速接上当前上下文。

新聊天开始后，可以先让助手读取/参考本文件，然后继续推进后续任务。

## 当前项目定位

当前项目不是传统测试平台，也不是团队协作平台，而是：

```text
个人专用的 AI 辅助测试执行工作流 / AI 测试助手底座
```

目标是让用户通过 ChatGPT、Codex、OpenHands、PyCharm、命令行等入口，用自然语言驱动测试工程任务：需求分析、测试范围分析、测试用例生成、接口测试设计、日志分析、代码审查、pytest 执行、Allure 报告生成与摘要分析等。

核心原则：

- 不造轮子。
- 优先使用成熟工业级工具、生态、协议、框架。
- 当前先做个人执行型测试助手，不做团队平台、不做界面。
- 不把电商业务写死进通用架构。
- 高风险能力默认不开放，例如 shell、filesystem_write、github_write。

## 当前已完成主链路

截至 037，已完成：

1. `memory` 最小 SQLite 底座。
2. `intent router` 配置化规则路由。
3. LangGraph 最小 orchestrator dry-run 骨架。
4. tool registry 与权限模型。
5. runtime CLI。
6. filesystem MCP 显式单文件只读读取。
7. GitHub MCP 显式单文件只读读取。
8. pytest_runner 受控 pytest 执行。
9. AllureReportReader 只读读取 Allure report widgets 摘要。
10. AllureReportGenerator 受控调用官方 Allure CLI 生成报告。
11. `--run-test-report [TARGET]` 一键测试报告链路：

```text
pytest --alluredir=allure-results
→ allure generate allure-results -o allure-report --clean
→ 读取 allure-report/widgets/summary.json
→ 输出报告摘要
```

用户本地已验证 Allure 摘要读取成功，示例结果：

```text
total=204
passed=204
failed=0
broken=0
skipped=0
duration_ms=3936
```

## 当前重要 CLI 入口

```powershell
python scripts/run_assistant.py "任务文本" --intent-only
python scripts/run_assistant.py "任务文本" --dry-run
python scripts/run_assistant.py "读取 README" --mcp-read-file README.md
python scripts/run_assistant.py "读取 GitHub README" --github-repo 58064809/ai-test-lab --github-read-file README.md
python scripts/run_assistant.py "运行 pytest" --run-pytest tests
python scripts/run_assistant.py "生成 Allure 报告" --generate-allure-report
python scripts/run_assistant.py "分析 Allure 报告" --read-allure-report allure-report
python scripts/run_assistant.py "运行测试并生成报告" --run-test-report
python scripts/run_assistant.py "运行测试并生成报告" --run-test-report tests/test_runtime_cli.py
```

## 当前明确未开放能力

继续保持禁用：

- `shell`
- `filesystem_write`
- `github_write`
- 任意 pytest 参数
- 任意 Allure 参数
- `allure serve`
- 自动打开浏览器
- 目录批量读取
- glob / 通配符读取
- 自动上下文收集
- 自研 GitHub REST fallback
- 自研 MCP 协议
- 自研测试报告系统

## 当前下一步建议

当前主线已切换为 Agentic QA。后续工作以 `docs/architecture/agentic-qa-blueprint.md` 为准，实施前必须先阅读 `references/research/agentic-qa-research-guide.md`。

不要继续围绕 Allure 拆小任务。Allure 链路已经作为受控测试报告能力保留。

下一步优先验证两个闭环：

1. 代码变更驱动精准回归：使用 `skills/regression-selection/` 和 `templates/regression_selection_template.md`。
2. 自动化失败到根因分析：使用 `skills/failure-analysis/` 和 `templates/failure_analysis_template.md`。

后续再考虑 GitHub PR / Issue 只读、Playwright MCP 只读页面分析、Schemathesis、数据库只读 MCP、Redis 只读 MCP 和 HITL。

## 新聊天推荐开场白

可以在新聊天第一条直接发送：

```text
这是 AI-助手 项目的新聊天，请接上之前 ai-test-lab 的上下文。

请先以 docs/operations/chat-handoff-current-context.md 为准，再结合 docs/runtime/current-status.md 和 docs/roadmap/next-tasks.md。

当前项目定位：个人专用 Agentic QA / AI 辅助测试执行工作流，不是传统测试平台。

当前 Agentic QA 主线以 docs/architecture/agentic-qa-blueprint.md 为准；实现前必须先阅读 references/research/agentic-qa-research-guide.md。

接下来请不要继续拆 Allure 任务，优先推进代码变更驱动精准回归和自动化失败分析两个闭环。

要求：
1. 一切以 Agentic QA 蓝图为准；
2. 实现前必须查阅调研指南；
3. 非必要情况不得自研，优先成熟工具；
4. 不开放 shell / filesystem_write / github_write；
5. 不写死电商业务。
```
