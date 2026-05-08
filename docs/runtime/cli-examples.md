# CLI Examples

本文档记录当前 runtime 已落地能力的命令示例。所有命令都通过 `scripts/run_assistant.py` 入口执行，不开放通用 shell、`filesystem_write` 或 `github_write`。

## intent-only

只做意图识别，不进入 orchestrator，不写 memory。

```bash
python scripts/run_assistant.py "分析这个需求的测试范围" --intent-only
```

## dry-run

生成任务计划、风险提示和工具授权评估，不执行真实工具动作。

```bash
python scripts/run_assistant.py "根据这个登录需求生成测试点" --dry-run
```

## write-memory

显式允许将 orchestrator 任务结果写入 SQLite memory。`--intent-only` 始终不写入。

```bash
python scripts/run_assistant.py "记录这次测试报告总结" --dry-run --write-memory
```

## filesystem MCP read

通过 filesystem MCP 只读入口读取仓库内显式单文件。当前不支持目录读取、glob 或多文件自动扫描。

```bash
python scripts/run_assistant.py "读取 README 并总结当前能力" --mcp-read-file README.md
```

如需要显示允许读取文件的完整内容，显式增加：

```bash
python scripts/run_assistant.py "读取 README" --mcp-read-file README.md --show-file-content
```

## GitHub MCP read

通过 GitHub MCP 只读入口读取显式仓库单文件。当前不开放 PR、Issue、评论或仓库写操作。

```bash
python scripts/run_assistant.py "读取远程 README 并总结" --github-repo owner/repo --github-read-file README.md --github-ref main
```

## run-pytest

通过 `pytest_runner` 受控 adapter 执行 pytest。该入口不是通用 shell，不支持任意命令或任意 pytest 参数。

```bash
python scripts/run_assistant.py "运行测试并总结结果" --run-pytest tests
```

不传 target 时默认运行 `tests`：

```bash
python scripts/run_assistant.py "运行默认测试集" --run-pytest
```

## read-allure-report

读取已有 Allure report 目录下的摘要信息，不生成报告。

```bash
python scripts/run_assistant.py "读取 Allure 报告摘要" --read-allure-report allure-report
```

不传目录时默认读取 `allure-report`：

```bash
python scripts/run_assistant.py "读取默认 Allure 报告摘要" --read-allure-report
```

## generate-allure-report

通过受控 Allure adapter 执行 `allure generate`，从已有 `allure-results` 生成 HTML 报告。该入口不开放 `allure serve` 或任意 Allure 参数。

```bash
python scripts/run_assistant.py "生成 Allure HTML 报告" --generate-allure-report allure-results --allure-output-dir allure-report
```

不传 results 目录时默认读取 `allure-results`：

```bash
python scripts/run_assistant.py "生成默认 Allure 报告" --generate-allure-report
```

## run-test-report

一键执行固定测试报告链路：

```text
pytest --alluredir=allure-results -> allure generate -> allure summary
```

示例：

```bash
python scripts/run_assistant.py "执行测试并输出 Allure 摘要" --run-test-report tests
```

不传 target 时默认运行 `tests`：

```bash
python scripts/run_assistant.py "执行默认测试报告链路" --run-test-report
```

`--run-test-report` 不能与独立的 `--run-pytest`、`--generate-allure-report`、`--read-allure-report` 同时使用。
