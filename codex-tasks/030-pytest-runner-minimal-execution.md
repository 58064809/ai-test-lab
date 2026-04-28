# Codex Task 030：接入 pytest_runner 最小真实执行能力

## 背景

当前已经完成：

- `filesystem_mcp_read` runtime 最小接入
- `--mcp-read-file` 显式单文件只读读取
- `.env` 等敏感路径安全拒绝
- Python 依赖环境收口，`pyproject.toml` 作为唯一主依赖源
- filesystem MCP live smoke 文档

下一步开始接第二个真实工具能力：`pytest_runner`。

注意：pytest 是成熟工业级测试工具，本任务不是自研测试框架，也不是自研执行器。只做一个很薄的 runtime adapter，用于显式触发 pytest，并把结果结构化输出。

## 目标

新增一个显式命令入口：

```powershell
python scripts/run_assistant.py "请运行 pytest" --run-pytest
```

或指定测试目标：

```powershell
python scripts/run_assistant.py "请运行 pytest" --run-pytest tests
python scripts/run_assistant.py "请运行 pytest" --run-pytest tests/test_runtime_cli.py
```

第一阶段只允许运行当前仓库内 pytest 测试，不允许任意 shell 命令。

## 最高原则

1. 使用成熟 pytest，不自研测试执行框架。
2. 不实现 shell 通用执行器。
3. 不开放任意命令执行。
4. 不开放用户自定义 shell 参数拼接。
5. 不执行仓库外路径。
6. 不接 Allure 生成，不接报告服务。
7. 不访问外部网络。
8. 不开放 filesystem_write。
9. 不修改业务文件。
10. 只做 pytest 最小执行与结构化结果输出。
11. Markdown 文档默认中文。

## 必须先阅读

- `pyproject.toml`
- `configs/tools.yaml`
- `configs/intents.yaml`
- `src/ai_test_assistant/runtime/cli.py`
- `src/ai_test_assistant/runtime/output.py`
- `src/ai_test_assistant/tool_registry/README.md`
- `docs/local-environment-prerequisites.md`
- `docs/current-status.md`
- `docs/next-steps.md`

## 任务一：新增 pytest runner adapter

新增：

```text
src/ai_test_assistant/testing/
  __init__.py
  pytest_runner.py
  README.md

tests/test_pytest_runner.py
```

建议模型：

```python
class PytestRunResult:
    command: list[str]
    target: str
    exit_code: int
    duration_seconds: float
    stdout: str
    stderr: str
    passed: bool
    reason: str
```

建议 adapter：

```python
class PytestRunner:
    def __init__(self, repo_root: Path): ...
    def run(self, target: str = "tests") -> PytestRunResult: ...
```

实现要求：

1. 使用当前 Python 解释器执行 pytest：

```python
[sys.executable, "-m", "pytest", target]
```

2. 使用 `subprocess.run` 时必须传 `args` list，不允许拼接 shell 字符串。
3. 必须 `shell=False`。
4. `target` 只能是仓库内相对路径。
5. 默认 target 是 `tests`。
6. 禁止 `..` 路径穿越。
7. 禁止绝对路径。
8. 禁止通配符 / glob。
9. 禁止额外 shell 参数。
10. 输出要做长度限制，避免 stdout/stderr 过长，例如每个最多 20000 字符。
11. 不生成 Allure 报告。
12. 不自动修改文件。

## 任务二：runtime CLI 新增显式 pytest 执行入口

更新：

```text
src/ai_test_assistant/runtime/cli.py
src/ai_test_assistant/runtime/output.py
```

新增参数：

```powershell
--run-pytest [TARGET]
```

要求：

- `--run-pytest` 不传 target 时默认 `tests`。
- `--run-pytest tests/test_runtime_cli.py` 运行指定仓库内测试文件。
- 这是显式真实执行，不应伪装成 dry-run。
- 如果同时传 `--dry-run`，允许保留 task/orchestrator dry-run，但 pytest 执行结果必须明确标记为“真实 pytest 执行”。
- 输出必须包含：
  - pytest 命令
  - target
  - exit_code
  - passed
  - duration_seconds
  - stdout 预览
  - stderr 预览

## 任务三：工具状态更新

更新：

```text
configs/tools.yaml
```

要求：

- `pytest_runner` 可以从 `planned` 改为 `enabled`。
- `risk_level` 保持 `execute_local_command`。
- notes 明确：只允许通过受控 adapter 执行 `python -m pytest <repo-relative-target>`，不是 shell 通用执行器。
- `shell` 必须保持 `disabled`。
- `filesystem_write` 必须保持 `disabled`。
- GitHub / Playwright / database / redis 不得因为本任务被启用。

## 任务四：intent 与输出优化

当前 `pytest_execution` intent 已存在。

要求：

- `请运行 pytest`、`运行 pytest`、`执行 pytest` 应识别为 `pytest_execution`。
- runtime 输出中如果执行了 pytest，需要显示 pytest 执行结果。
- 不要引入外部 LLM。

## 任务五：测试要求

新增或更新测试，至少覆盖：

1. `PytestRunner` 默认 target 为 `tests`。
2. `PytestRunner` 使用 `sys.executable -m pytest target`。
3. 禁止绝对路径。
4. 禁止 `..` 路径穿越。
5. 禁止 glob，例如 `tests/*.py`。
6. 禁止额外参数注入，例如 `tests --maxfail=1`。
7. CLI 支持 `--run-pytest` 默认 target。
8. CLI 支持 `--run-pytest tests/test_runtime_cli.py`。
9. CLI 输出包含真实 pytest 执行结果。
10. `pytest_runner` 为 `enabled + execute_local_command`。
11. `shell` 仍为 `disabled`。
12. `filesystem_write` 仍为 `disabled`。

测试中如果不想真的跑完整 pytest，可以 mock `PytestRunner.run`，但 adapter 单测必须验证 subprocess 参数安全。

## 任务六：文档更新

更新：

- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/testing/README.md`
- `src/ai_test_assistant/runtime/README.md`
- `src/ai_test_assistant/tool_registry/README.md`

必须明确：

- 已接入 pytest_runner 最小真实执行能力。
- 这是受控 pytest 执行，不是 shell 通用执行。
- 只允许仓库内相对路径 target。
- 当前不接 Allure。
- 当前不开放 shell。
- 当前不开放 filesystem_write。

## 禁止事项

- 不要自研测试框架。
- 不要实现 shell 通用执行器。
- 不要用 `shell=True`。
- 不要拼接命令字符串。
- 不要支持任意 pytest 参数。
- 不要支持仓库外路径。
- 不要支持 glob。
- 不要生成 Allure 报告。
- 不要访问网络。
- 不要开放 filesystem_write。

## 验收命令

自动测试：

```bash
pytest
```

手动验证：

```powershell
python scripts/run_assistant.py "请运行 pytest" --run-pytest
python scripts/run_assistant.py "请运行 pytest" --run-pytest tests/test_runtime_cli.py
python scripts/run_assistant.py "请运行 pytest" --run-pytest ..
```

预期：

- 前两条执行 pytest 并输出结构化结果。
- 第三条拒绝路径穿越。

## 完成标准

- pytest_runner 最小真实执行能力可用。
- 不开放 shell。
- 不开放任意命令。
- 不支持危险 target。
- 所有测试通过。
