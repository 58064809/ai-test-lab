# Codex Task 034：显式工具执行与 orchestrator dry-run 授权展示对齐

## 背景

033 已完成 GitHub MCP read 正文解析增强，并经过用户本地复测：

```powershell
python scripts/run_assistant.py "读取 GitHub README 并分析" --dry-run --github-repo 58064809/ai-test-lab --github-read-file README.md
```

当前已经能通过 `github_mcp` 读取 README 正文：

```text
允许读取=是 | 来源=github_mcp | 路径=README.md | 字符数=2250 | 已截断=否
结果说明：Read allowed through GitHub MCP.
```

但输出中存在一个展示层矛盾：

1. CLI 显式参数 `--github-read-file` 已经真实执行 GitHub read，并且输出：

```text
工具风险提示：本次通过 github_read 进行了显式只读外部网络访问。
```

2. 但 orchestrator dry-run 的工具授权结果仍显示：

```text
github_read | 状态=enabled | 风险=external_network | 允许执行=否 | 需要确认=是
拒绝原因：Tool 'github_read' needs external network approval.
```

这会误导用户，以为 GitHub read 没有授权或没有执行。

本任务目标：对齐“显式 CLI 工具执行结果”和“orchestrator dry-run 推荐工具授权展示”，避免输出自相矛盾。

## 最高原则

1. 不新增工具能力。
2. 不开放 GitHub write。
3. 不开放 shell。
4. 不开放 filesystem_write。
5. 不改变 GitHub MCP read 的安全边界。
6. 不让 orchestrator 自动执行工具。
7. 不把 dry-run 普通推荐工具误标为已执行。
8. 只对显式 CLI 参数触发的工具执行做展示对齐。
9. Markdown 文档默认中文。

## 必须先阅读

- `src/ai_test_assistant/runtime/cli.py`
- `src/ai_test_assistant/runtime/output.py`
- `src/ai_test_assistant/orchestrator/graph.py`
- `src/ai_test_assistant/orchestrator/nodes.py`
- `src/ai_test_assistant/tool_registry/permissions.py`
- `tests/test_runtime_cli.py`
- `tests/test_tool_registry.py`
- `docs/current-status.md`
- `docs/next-steps.md`

## 任务一：设计显式工具执行元信息

请在 runtime/orchestrator 输入上下文中增加最小元信息，用于表示本次 CLI 显式执行过的工具。

建议形式之一：

```python
explicit_tool_executions = [
    {
        "tool_name": "github_read",
        "source": "github_mcp",
        "operation": "read_file",
        "allowed": True,
        "risk_level": "external_network",
        "reason": "Executed explicitly by CLI argument --github-read-file.",
    }
]
```

也可以用更合适的现有 state 字段，但必须满足：

- 能区分 orchestrator dry-run 推荐工具和 CLI 显式执行工具。
- 能在 output 中避免同一工具同时显示“已执行成功”和“授权拒绝”。
- 不影响普通 dry-run 推荐工具授权判断。

## 任务二：GitHub read 展示对齐

当用户显式传入：

```powershell
--github-repo 58064809/ai-test-lab --github-read-file README.md
```

并且 CLI 已经通过 `ToolPermissionContext(allow_external_network=True)` 授权并执行成功时：

输出中不应再出现下面这种误导性授权拒绝：

```text
github_read | 状态=enabled | 风险=external_network | 允许执行=否
拒绝原因：Tool 'github_read' needs external network approval.
```

推荐处理方式：

- 在工具授权结果中将 `github_read` 标记为“已通过显式 CLI 授权执行”；或
- 过滤掉 orchestrator dry-run 对同一工具的未授权推荐结果；或
- 添加单独区块“显式工具执行结果”，并避免重复展示同一工具的 dry-run 拒绝。

输出应明确：

```text
显式工具执行结果：
- github_read | 来源=github_mcp | 风险=external_network | 已执行=是 | 授权方式=CLI explicit approval
```

具体措辞可以中文化，但不能再自相矛盾。

## 任务三：pytest_runner 展示不要被破坏

`--run-pytest` 已经是显式真实执行。

要求：

- 保留当前 pytest 执行结果区块。
- 如果任务文本同时推荐 `pytest_runner`，不要出现“已执行 pytest”和“pytest_runner dry-run 禁止执行”的矛盾。
- pytest 仍不能变成通用 shell。

## 任务四：普通 dry-run 行为保持不变

对于没有显式工具参数的命令，例如：

```powershell
python scripts/run_assistant.py "请运行 pytest 并分析 Allure 结果" --dry-run
```

仍然应该显示：

```text
pytest_runner | 状态=enabled | 风险=execute_local_command | 允许执行=否
拒绝原因：Tool 'pytest_runner' cannot run local commands during dry-run.
```

也就是说：只有 CLI 显式执行过的工具才做展示对齐，普通 dry-run 推荐工具仍然应该提示风险和拒绝原因。

## 任务五：测试覆盖

更新：

```text
tests/test_runtime_cli.py
```

至少覆盖：

1. 显式 `--github-read-file README.md` 成功时：
   - 输出包含 `来源=github_mcp`；
   - 输出包含“显式只读外部网络访问”；
   - 输出不包含 `Tool 'github_read' needs external network approval.`；
   - 输出包含“显式工具执行”或等价说明。
2. `--github-read-file .env` 被 policy/client 拒绝时：
   - 仍不应显示 orchestrator dry-run 的 `github_read needs external network approval` 矛盾提示；
   - 文件读取结果应显示拒绝原因。
3. `--run-pytest` 成功时：
   - 输出包含真实 pytest 执行结果；
   - 如果推荐工具包含 pytest_runner，不应同时显示 `cannot run local commands during dry-run` 的矛盾提示。
4. 普通 dry-run 未显式执行工具时：
   - `pytest_runner` 仍因 dry-run 被拒绝；
   - `github_read` 仍需要 external network approval。
5. `--write-memory` 时仍只保存元信息，不保存 file content。

测试中使用 stub/mock：

- 不真实启动 Docker。
- 不真实访问 GitHub。
- 不真实跑完整 pytest，除非已有轻量 stub。

## 任务六：文档更新

更新：

- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/runtime/README.md`

必须说明：

- runtime 已区分“orchestrator dry-run 推荐工具”和“CLI 显式工具执行”。
- `--github-read-file`、`--mcp-read-file`、`--read-file`、`--run-pytest` 属于显式入口。
- dry-run 本身仍不代表自动执行推荐工具。
- GitHub read / pytest_runner 仍需要显式参数触发。

## 禁止事项

- 不要开放 GitHub write。
- 不要开放 shell。
- 不要开放 filesystem_write。
- 不要让 orchestrator 自动执行推荐工具。
- 不要把普通 dry-run 推荐工具标成已执行。
- 不要删除工具授权评估能力。
- 不要自研 GitHub REST fallback。

## 验收命令

```bash
pytest
```

手动验证：

```powershell
python scripts/run_assistant.py "读取 GitHub README 并分析" --dry-run --github-repo 58064809/ai-test-lab --github-read-file README.md
python scripts/run_assistant.py "请运行 pytest" --run-pytest tests/test_runtime_cli.py
python scripts/run_assistant.py "请运行 pytest 并分析 Allure 结果" --dry-run
```

## 完成标准

- 显式 GitHub read 成功时，输出不再显示 github_read dry-run 授权拒绝矛盾。
- 显式 pytest 执行时，输出不再显示 pytest_runner dry-run 授权拒绝矛盾。
- 普通 dry-run 推荐工具风险提示仍保留。
- 没有开放任何写能力。
- 所有测试通过。
