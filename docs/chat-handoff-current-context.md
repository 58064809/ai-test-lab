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

不要继续拆 Allure 任务。Allure 链路已收口。

下一步优先做：

```text
038：真实任务验证包
```

目标：用 5~10 个真实测试任务验证当前助手是否真的有用。

建议覆盖：

1. 需求分析。
2. 测试用例生成。
3. 日志分析。
4. pytest + Allure 报告总结。
5. Codex 修改结果审查。
6. 接口测试设计。
7. 失败测试结果生成缺陷报告。
8. 成熟工具接入评估。

后续再考虑：

- Playwright MCP 页面只读分析。
- GitHub PR / Issue 只读元数据。
- Schemathesis 接口契约测试。
- Keploy API 测试/Mock。
- 数据库只读 MCP。
- Redis 只读 MCP。
- orchestrator 正式执行分支：计划 → 确认 → 执行 → 汇总。

## 新聊天推荐开场白

可以在新聊天第一条直接发送：

```text
这是 AI-助手 项目的新聊天，请接上之前 ai-test-lab 的上下文。

请先以 docs/chat-handoff-current-context.md 为准，再结合 docs/current-status.md 和 docs/next-steps.md。

当前项目定位：个人专用的 AI 辅助测试执行工作流，不是传统测试平台。

当前已完成到 037：pytest + allure generate + allure report summary 一键链路已经收口。

接下来请不要继续拆 Allure 任务，优先推进 038：真实任务验证包。

要求：
1. 只做 Codex 任务清单，代码实现交给 Codex；
2. 节奏快一点，不要过度谨慎；
3. 不造轮子，优先成熟工具；
4. 不开放 shell / filesystem_write / github_write；
5. 不写死电商业务。
```
