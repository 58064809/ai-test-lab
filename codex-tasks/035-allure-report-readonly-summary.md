# Codex Task 035：Allure 报告只读摘要最小接入

## 背景

当前已完成：

- `filesystem_mcp_read`：官方 filesystem MCP 显式单文件只读读取。
- `pytest_runner`：受控 pytest 最小真实执行。
- `github_read`：官方 GitHub MCP read，支持显式仓库 + 显式单文件读取。
- `explicit_tool_executions`：已区分 CLI 显式工具执行和 orchestrator dry-run 推荐工具，避免输出自相矛盾。

下一步接入 `allure_report` 的只读摘要能力，用于后续“运行 pytest 后分析 Allure 报告”。

注意：Allure 是成熟报告工具。本任务不是自研测试报告系统，不生成 HTML，不解析自定义测试框架，只做 Allure 官方报告目录的只读摘要读取。

## 目标

新增一个显式只读入口：

```powershell
python scripts/run_assistant.py "分析 Allure 报告" --read-allure-report allure-report
```

第一阶段只读取已经存在的 Allure 报告目录，不负责生成报告。

优先读取官方 Allure report 目录中的 JSON 文件，例如：

```text
allure-report/widgets/summary.json
allure-report/widgets/suites.json
allure-report/widgets/categories.json
allure-report/widgets/duration.json
```

如果不存在 `allure-report`，返回结构化失败原因，不自动生成报告。

## 最高原则

1. 使用 Allure 官方报告目录和 JSON 结构，不自研报告系统。
2. 不生成 Allure HTML 报告。
3. 不调用 shell 通用命令。
4. 不开放任意命令执行。
5. 不修改项目文件。
6. 不开放 filesystem_write。
7. 不开放 shell。
8. 不访问外部网络。
9. 只读仓库内相对路径。
10. 不读取仓库外路径。
11. 不读取 `.env`、token、secret、password 类文件。
12. Markdown 文档默认中文。

## 必须先阅读

- `configs/tools.yaml`
- `src/ai_test_assistant/runtime/cli.py`
- `src/ai_test_assistant/runtime/output.py`
- `src/ai_test_assistant/orchestrator/nodes.py`
- `src/ai_test_assistant/orchestrator/state.py`
- `src/ai_test_assistant/testing/pytest_runner.py`
- `tests/test_runtime_cli.py`
- `tests/test_tool_registry.py`
- `docs/current-status.md`
- `docs/next-steps.md`

## 任务一：新增 Allure 报告只读 adapter

新增：

```text
src/ai_test_assistant/reporting/
  __init__.py
  allure_reader.py
  README.md

tests/test_allure_report_reader.py
```

建议模型：

```python
@dataclass(slots=True)
class AllureReportSummary:
    allowed: bool
    report_dir: str
    total: int | None
    passed: int | None
    failed: int | None
    broken: int | None
    skipped: int | None
    unknown: int | None
    duration_ms: int | None
    top_failures: list[str]
    reason: str
```

建议 reader：

```python
class AllureReportReader:
    def __init__(self, repo_root: Path): ...
    def read_summary(self, report_dir: str = "allure-report") -> AllureReportSummary: ...
```

实现要求：

1. `report_dir` 必须是仓库内相对路径。
2. 禁止绝对路径。
3. 禁止 `..` 路径穿越。
4. 禁止 glob。
5. 禁止读取 `.env`、token、secret、password 类路径。
6. 只读取 Allure report widgets 下的 JSON 文件。
7. 如果 `widgets/summary.json` 不存在，返回 `allowed=False` 和明确原因。
8. 对 JSON 读取做异常处理，返回结构化失败原因。
9. 输出摘要即可，不要输出完整大 JSON。
10. top failures 最多保留 10 条。
11. 不生成报告、不执行 allure 命令。

## 任务二：runtime CLI 新增显式入口

更新：

```text
src/ai_test_assistant/runtime/cli.py
src/ai_test_assistant/runtime/output.py
```

新增参数：

```powershell
--read-allure-report [REPORT_DIR]
```

要求：

- 不传 REPORT_DIR 时默认 `allure-report`。
- 只做显式只读读取。
- 执行前通过 tool registry 检查 `allure_report`。
- `allure_report` 属于 read-only 报告读取，不需要执行本地命令。
- 输出必须包含：
  - report_dir
  - total
  - passed
  - failed
  - broken
  - skipped
  - unknown
  - duration_ms
  - top_failures
  - reason
- 将本次读取记录到 `explicit_tool_executions`：
  - tool_name=`allure_report`
  - source=`allure_report`
  - operation=`read_summary`
  - risk_level=`read_only`
- 不要和 pytest_result 混淆。

## 任务三：工具状态更新

更新：

```text
configs/tools.yaml
```

要求：

- `allure_report` 可以从 `planned` 改为 `enabled`。
- `risk_level` 为 `read_only`。
- notes 明确：只读已有 Allure report 目录，不生成报告，不执行 allure CLI。
- `shell` 必须保持 disabled。
- `filesystem_write` 必须保持 disabled。
- GitHub write 必须保持 disabled。

## 任务四：intent 与普通 dry-run 保持一致

当前任务：

```text
分析 Allure 报告
读取 Allure 报告
查看 Allure 结果
```

应识别为已有 `pytest_execution` 或更合适的现有 intent。如果已有 Allure 专门 intent，可以使用；不要新建复杂 intent 体系。

普通 dry-run 未显式传 `--read-allure-report` 时，只能推荐工具和展示授权评估，不应真实读取报告。

显式传 `--read-allure-report` 时，读取结果应显示在输出中，并且不再出现同一 `allure_report` 的误导性 dry-run 拒绝。

## 任务五：测试要求

新增或更新测试，至少覆盖：

1. `AllureReportReader` 默认读取 `allure-report`。
2. 禁止绝对路径。
3. 禁止 `..` 路径穿越。
4. 禁止 glob。
5. 缺少 `widgets/summary.json` 时结构化失败。
6. 能从 `summary.json` 提取 total / passed / failed / broken / skipped / unknown。
7. 能从 `duration.json` 或 summary 中提取 duration_ms，如不存在则为 None。
8. 能从 `categories.json` 或 suites 中提取 top_failures，最多 10 条。
9. CLI 支持 `--read-allure-report` 默认目录。
10. CLI 支持 `--read-allure-report custom-report`。
11. CLI 输出包含 Allure 摘要。
12. CLI 显式读取后包含“显式工具执行结果：allure_report”。
13. `--write-memory` 时只保存摘要元信息，不保存完整 JSON。
14. `allure_report` 为 enabled + read_only。
15. `shell` 仍 disabled。
16. `filesystem_write` 仍 disabled。
17. `github_write` 仍 disabled。

测试中用临时目录构造最小 Allure report JSON，不依赖真实 Allure CLI。

## 任务六：memory 安全

如果 `--write-memory`，只允许写入 Allure 摘要字段：

```text
report_dir, total, passed, failed, broken, skipped, unknown, duration_ms, top_failures_count, allowed, reason
```

不要写入完整 `summary.json`、`suites.json`、`categories.json` 原文。

## 任务七：文档更新

更新：

- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/reporting/README.md`
- `src/ai_test_assistant/runtime/README.md`
- `src/ai_test_assistant/tool_registry/README.md`

必须说明：

- 已接入 Allure 报告只读摘要。
- 只读取已经存在的 `allure-report` 目录。
- 不生成报告。
- 不执行 Allure CLI。
- 不开放 shell。
- 后续如需生成 Allure 报告，应单独任务接官方 Allure CLI，并保持受控命令边界。

## 禁止事项

- 不要自研 HTML 报告。
- 不要生成 Allure 报告。
- 不要执行 allure CLI。
- 不要开放 shell。
- 不要开放 filesystem_write。
- 不要访问外部网络。
- 不要读取仓库外路径。
- 不要读取敏感文件。
- 不要写完整 JSON 到 memory。

## 验收命令

```bash
pytest
```

手动验证：

```powershell
python scripts/run_assistant.py "分析 Allure 报告" --read-allure-report allure-report
python scripts/run_assistant.py "分析 Allure 报告" --read-allure-report ..
```

预期：

- 第一条如果 report 存在，则输出摘要；如果不存在，则结构化说明缺少 `widgets/summary.json`。
- 第二条拒绝路径穿越。

## 完成标准

- `allure_report` 最小只读摘要能力可用。
- 不生成报告。
- 不开放 shell。
- 不开放 filesystem_write。
- 不访问外部网络。
- 所有测试通过。
