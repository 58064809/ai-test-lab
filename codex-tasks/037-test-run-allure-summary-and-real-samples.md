# Codex Task 037：测试执行链路一键收口 + 真实任务样本扩展

## 背景

当前已完成并验证：

- `pytest_runner`：受控执行 pytest。
- `allure_generate`：受控调用官方 Allure CLI 生成 `allure-report`。
- `allure_report`：只读读取 `allure-report/widgets/*.json` 摘要。

用户本地已验证：

```text
Allure report generated successfully.
Allure 报告摘要读取成功：total=204, passed=204, failed=0, broken=0, skipped=0, duration_ms=3936
```

本任务目标：把测试执行链路收口成一个显式组合入口，并补一批真实任务样本，验证助手是否真能做测试工程任务。

## 目标一：新增一键测试链路入口

新增 CLI 参数：

```powershell
--run-test-report [TARGET]
```

默认行为等价于：

```powershell
python -m pytest tests --alluredir=allure-results
allure generate allure-results -o allure-report --clean
读取 allure-report 摘要
```

支持指定测试目标：

```powershell
python scripts/run_assistant.py "运行测试并生成报告" --run-test-report tests/test_runtime_cli.py
```

## 实现要求

1. 不开放 shell。
2. 不支持任意 pytest 参数。
3. 不支持任意 allure 参数。
4. 复用现有 `PytestRunner` / `AllureReportGenerator` / `AllureReportReader`。
5. 如现有 `PytestRunner` 不支持 `--alluredir`，新增受控参数支持：只允许追加固定 `--alluredir=allure-results`。
6. 仍使用 args list，`shell=False`。
7. 路径仍必须是仓库内相对路径。
8. 执行顺序固定：pytest → allure generate → allure report summary。
9. 任一步失败，都输出结构化结果，不继续伪造成成功。
10. 输出必须包含：pytest 结果、Allure 生成结果、Allure 摘要。
11. 写 memory 时只保存摘要元信息，不保存 stdout/stderr 全量、不保存完整 JSON。

## 工具授权

执行前必须检查：

- `pytest_runner`
- `allure_generate`
- `allure_report`

显式执行结果记录：

- `pytest_runner`
- `allure_generate`
- `allure_report`

普通 dry-run 没有 `--run-test-report` 时，不得真实执行。

## 目标二：扩展真实任务样本

更新：

```text
validation/real-task-samples.yaml
```

新增 8~10 条真实测试工程任务样本，覆盖：

1. 运行 pytest 并生成 Allure 报告。
2. 分析 Allure 报告并输出测试总结。
3. 读取 README 分析项目状态。
4. 读取 GitHub README 分析项目状态。
5. 读取日志文件定位异常。
6. 根据需求生成测试用例。
7. 根据接口文档设计接口测试点。
8. 根据失败测试结果生成缺陷报告。
9. 审查 Codex 修改结果。
10. 评估是否需要接入某个成熟工具。

样本只做验证，不要引入公司业务硬编码。

## 测试要求

至少覆盖：

1. CLI 支持 `--run-test-report` 默认 target。
2. CLI 支持 `--run-test-report tests/test_xxx.py`。
3. 执行顺序是 pytest → allure generate → allure read。
4. pytest 失败时仍输出 pytest 结果，并不伪造 Allure 成功。
5. pytest 成功但 Allure 生成失败时输出失败原因。
6. 三步都成功时输出 Allure 摘要。
7. 普通 dry-run 不执行组合链路。
8. 不支持额外 pytest 参数注入。
9. `shell` 仍 disabled。
10. `filesystem_write` 仍 disabled。
11. `github_write` 仍 disabled。
12. validation 样本测试通过。

测试中 mock subprocess / adapters，不依赖本机真实 Allure CLI。

## 文档更新

更新：

- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/runtime/README.md`
- `src/ai_test_assistant/reporting/README.md`

说明：

- 已支持显式一键测试报告链路 `--run-test-report`。
- 该入口只组合已有受控工具。
- 不开放 shell、不开放任意参数。
- Allure 线到此收口，后续不继续拆小任务。

## 禁止事项

- 不要开放 shell。
- 不要支持任意 pytest 参数。
- 不要支持任意 allure 参数。
- 不要执行 `allure serve`。
- 不要打开浏览器。
- 不要开放 filesystem_write。
- 不要开放 github_write。
- 不要写死电商业务。

## 验收命令

```bash
pytest
```

手动验证：

```powershell
python scripts/run_assistant.py "运行测试并生成报告" --run-test-report
python scripts/run_assistant.py "运行测试并生成报告" --run-test-report tests/test_runtime_cli.py
```

## 完成标准

- 一键测试报告链路可用。
- 真实任务样本增加并通过验证。
- Allure 链路正式收口。
- 所有测试通过。
