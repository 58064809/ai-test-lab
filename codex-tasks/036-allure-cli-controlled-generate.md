# Codex Task 036：官方 Allure CLI 受控生成报告

## 背景

035 已接入 `allure_report` 只读摘要能力：读取已有 `allure-report/widgets/*.json`，不生成报告。

但完整闭环还缺一步：如果本地只有 pytest/allure 产生的 `allure-results`，当前 runtime 不能生成 `allure-report`，因此 `--read-allure-report` 会提示缺少 `widgets/summary.json`。

本任务目标：接入官方 Allure CLI 的**受控生成能力**，从已有 `allure-results` 生成 `allure-report`。

这不是自研报告系统，不解析 HTML，不开放 shell，只是受控执行官方命令：

```powershell
allure generate allure-results -o allure-report --clean
```

## 目标

新增显式 CLI 入口：

```powershell
python scripts/run_assistant.py "生成 Allure 报告" --generate-allure-report
```

可指定输入输出目录：

```powershell
python scripts/run_assistant.py "生成 Allure 报告" --generate-allure-report allure-results --allure-output-dir allure-report
```

第一阶段只允许：

```text
allure generate <results_dir> -o <report_dir> --clean
```

不支持任意 allure 参数，不支持 shell，不支持打开浏览器，不支持 serve。

## 最高原则

1. 使用官方 Allure CLI，不自研报告生成器。
2. 不解析或生成 HTML 内容。
3. 不开放 shell 通用执行器。
4. 不使用 `shell=True`。
5. 不拼接命令字符串。
6. 不支持任意用户自定义 Allure 参数。
7. 不支持 `allure serve`。
8. 不自动打开浏览器。
9. 不访问外部网络。
10. 只允许仓库内相对路径。
11. `results_dir` 必须存在。
12. `report_dir` 必须在仓库内。
13. 禁止绝对路径、`..`、glob。
14. 禁止 `.env`、token、secret、password 类路径。
15. `filesystem_write` 仍保持 disabled。
16. `shell` 仍保持 disabled。
17. `github_write` 仍保持 disabled。
18. Markdown 文档默认中文。

## 必须先阅读

- `src/ai_test_assistant/reporting/allure_reader.py`
- `src/ai_test_assistant/reporting/README.md`
- `src/ai_test_assistant/testing/pytest_runner.py`
- `src/ai_test_assistant/runtime/cli.py`
- `src/ai_test_assistant/runtime/output.py`
- `src/ai_test_assistant/orchestrator/nodes.py`
- `src/ai_test_assistant/orchestrator/state.py`
- `configs/tools.yaml`
- `tests/test_allure_report_reader.py`
- `tests/test_pytest_runner.py`
- `tests/test_runtime_cli.py`
- `tests/test_tool_registry.py`
- `docs/local-environment-prerequisites.md`
- `docs/current-status.md`
- `docs/next-steps.md`

## 任务一：新增 Allure CLI generator adapter

新增或更新：

```text
src/ai_test_assistant/reporting/allure_generator.py

tests/test_allure_report_generator.py
```

建议模型：

```python
@dataclass(slots=True)
class AllureGenerateResult:
    command: list[str]
    results_dir: str
    report_dir: str
    exit_code: int | None
    duration_seconds: float
    stdout: str
    stderr: str
    generated: bool
    reason: str
```

建议 adapter：

```python
class AllureReportGenerator:
    def __init__(self, repo_root: Path, executable: str = "allure"): ...
    def generate(self, results_dir: str = "allure-results", report_dir: str = "allure-report") -> AllureGenerateResult: ...
```

实现要求：

1. 命令必须是 args list：

```python
["allure", "generate", normalized_results_dir, "-o", normalized_report_dir, "--clean"]
```

2. `subprocess.run(..., shell=False)`。
3. `results_dir` 必须是仓库内相对路径。
4. `results_dir` 必须存在且是目录。
5. `report_dir` 必须是仓库内相对路径。
6. `report_dir` 可以不存在，由 Allure CLI 生成。
7. 禁止绝对路径。
8. 禁止 `..` 路径穿越。
9. 禁止 glob。
10. 禁止敏感路径。
11. stdout/stderr 做长度限制，例如各 20000 字符。
12. 如果 Allure CLI 不存在，返回结构化失败，例如 `Allure CLI executable not found.`。
13. 不自动安装 Allure CLI。
14. 不执行 `allure serve`。
15. 不打开浏览器。

## 任务二：新增 runtime CLI 显式入口

更新：

```text
src/ai_test_assistant/runtime/cli.py
src/ai_test_assistant/runtime/output.py
```

新增参数：

```powershell
--generate-allure-report [RESULTS_DIR]
--allure-output-dir REPORT_DIR
```

要求：

- `--generate-allure-report` 不传值时默认 `allure-results`。
- `--allure-output-dir` 默认 `allure-report`。
- 执行前通过 tool registry 检查新增工具 `allure_generate`。
- `allure_generate` 属于受控本地命令 + 写报告目录，不能伪装成只读。
- 授权上下文必须显式允许：
  - `allow_execute_local_command=True`
  - 如权限模型已有 `allow_write_project_files`，也应传 True；否则保留工具风险说明。
- 生成结果应写入 `explicit_tool_executions`：
  - tool_name=`allure_generate`
  - source=`allure_cli`
  - operation=`generate_report`
  - risk_level=`execute_local_command`
  - allowed 根据 generated
- 输出必须包含：
  - command
  - results_dir
  - report_dir
  - exit_code
  - generated
  - duration_seconds
  - stdout 预览
  - stderr 预览
  - reason

## 任务三：工具注册表更新

更新：

```text
configs/tools.yaml
```

新增或更新工具：

```yaml
- name: allure_generate
  description: Generate Allure HTML report from existing allure-results using official Allure CLI.
  status: enabled
  risk_level: execute_local_command
  category: reporting
  implementation: local_command_adapter
  notes: 只允许受控执行 allure generate <results_dir> -o <report_dir> --clean；不开放 allure serve，不开放任意参数，不开放 shell。
```

要求：

- `allure_report` 保持 enabled + read_only。
- `shell` 保持 disabled。
- `filesystem_write` 保持 disabled。
- `github_write` 保持 disabled。

## 任务四：intent 与 dry-run 行为

任务文本：

```text
生成 Allure 报告
用 allure-results 生成 allure-report
生成测试报告
```

可归类到已有 `pytest_execution` 或新增轻量 `report_generation` intent。

如果新增 intent，必须简单配置化，不引入外部 LLM，不搞复杂语义系统。

普通 dry-run 未显式传 `--generate-allure-report` 时，不得真实生成报告，只能推荐工具和展示风险。

显式传 `--generate-allure-report` 时，执行受控 Allure CLI，并避免同一工具出现 dry-run 拒绝矛盾。

## 任务五：测试要求

新增或更新测试，至少覆盖：

1. `AllureReportGenerator` 默认 results_dir=`allure-results`，report_dir=`allure-report`。
2. 使用命令 args list：`allure generate allure-results -o allure-report --clean`。
3. `subprocess.run` 使用 `shell=False`。
4. 禁止 results_dir 绝对路径。
5. 禁止 report_dir 绝对路径。
6. 禁止 `..` 路径穿越。
7. 禁止 glob。
8. 禁止敏感路径。
9. results_dir 不存在时结构化失败，不调用 subprocess。
10. Allure CLI 不存在时结构化失败。
11. CLI 支持 `--generate-allure-report` 默认目录。
12. CLI 支持 `--generate-allure-report custom-results --allure-output-dir custom-report`。
13. CLI 输出包含 Allure 生成结果。
14. 显式执行后包含 `显式工具执行结果：allure_generate`。
15. 普通 dry-run 未显式执行时，不生成报告。
16. `allure_generate` 为 enabled + execute_local_command。
17. `allure_report` 仍 enabled + read_only。
18. `shell` 仍 disabled。
19. `filesystem_write` 仍 disabled。
20. `github_write` 仍 disabled。

测试中必须 mock subprocess，不要依赖本机真实 Allure CLI。

## 任务六：文档更新

更新：

- `docs/local-environment-prerequisites.md`
- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/reporting/README.md`
- `src/ai_test_assistant/runtime/README.md`
- `src/ai_test_assistant/tool_registry/README.md`

必须说明：

- `allure_report`：只读已有 report 摘要。
- `allure_generate`：受控调用官方 Allure CLI 生成 report。
- 生成命令固定为 `allure generate <results_dir> -o <report_dir> --clean`。
- 不支持 `allure serve`。
- 不自动安装 Allure CLI。
- Windows 需要用户自行安装 Allure CLI 并确保 `allure --version` 可用。
- shell 仍未开放。

## 禁止事项

- 不要自研 HTML 报告。
- 不要解析或拼装 HTML。
- 不要执行 `allure serve`。
- 不要打开浏览器。
- 不要使用 `shell=True`。
- 不要拼接命令字符串。
- 不要支持任意 Allure 参数。
- 不要自动安装 Allure CLI。
- 不要开放 shell。
- 不要开放 filesystem_write。
- 不要开放 github_write。
- 不要访问外部网络。

## 验收命令

```bash
pytest
```

手动验证，前提：用户本地已安装 Allure CLI 且存在 `allure-results`：

```powershell
allure --version
python scripts/run_assistant.py "生成 Allure 报告" --generate-allure-report
python scripts/run_assistant.py "分析 Allure 报告" --read-allure-report allure-report
```

## 完成标准

- 受控 Allure CLI 生成能力可用。
- 只支持固定 `allure generate` 命令。
- 不开放 shell。
- 不开放任意命令。
- 不开放 GitHub write / filesystem_write。
- 所有测试通过。
