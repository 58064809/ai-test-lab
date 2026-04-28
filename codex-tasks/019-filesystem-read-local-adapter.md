# Codex Task 019：filesystem_read 本地只读适配器与 orchestrator dry-run 联动

## 任务背景

018 已完成 `filesystem_read` 接入前设计与路径安全策略模型，但当前仍然没有任何文件读取能力。

如果继续只写设计文档，底座会停留在“规划阶段”。本任务开始落地第一个低风险真实能力：**仓库内白名单文件的本地只读读取适配器**。

注意：本任务不是接入 MCP Server，也不是实现通用文件系统工具，更不是开放写文件能力。它只是用现有 `FilesystemReadPolicy` 对仓库相对路径做安全判断后，读取允许范围内的文本文件内容，为后续 MCP filesystem adapter 提供可替换的本地 adapter。

## 最高原则

1. 不接入 MCP Server。
2. 不调用 MCP SDK。
3. 不执行本地命令。
4. 不访问外部网络。
5. 不开放 filesystem write。
6. 不读取黑名单文件。
7. 不读取仓库外文件。
8. 不读取真实业务敏感文件。
9. 不把本地 adapter 包装成 MCP 已接入。
10. 不写死任何电商业务规则。
11. 本地 adapter 必须保持可替换，后续可替换为成熟 filesystem MCP Server。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/012-industrial-grade-selection-policy.md`
- `codex-tasks/017-mcp-selection-and-security-boundary.md`
- `codex-tasks/018-filesystem-read-design-and-safe-adapter.md`
- `docs/filesystem-read-design.md`
- `docs/mcp-security-policy.md`
- `src/ai_test_assistant/filesystem/policy.py`
- `src/ai_test_assistant/tool_registry/README.md`
- `src/ai_test_assistant/orchestrator/README.md`
- `configs/tools.yaml`

## 任务一：实现本地只读 adapter

新增或更新：

```text
src/ai_test_assistant/filesystem/
  adapter.py
  README.md

tests/test_filesystem_read_adapter.py
```

要求：

1. 实现 `LocalFilesystemReadAdapter` 或等价命名。
2. 构造参数至少包含：
   - `repo_root: Path`
   - `policy: FilesystemReadPolicy | None = None`
3. 提供方法：

```python
read_text(repo_relative_path: str) -> FilesystemReadResult
```

4. `FilesystemReadResult` 至少包含：

```python
allowed: bool
path: str | None
content: str | None
reason: str
truncated: bool
```

5. 必须先调用 `FilesystemReadPolicy.evaluate()`。
6. policy 不允许时，不得读取文件。
7. 必须阻止仓库外路径。
8. 只读取文本文件。
9. 对单文件大小做上限限制，例如 128KB；超出时可以拒绝或截断，但必须在结果中标记。
10. 不要读取二进制文件。
11. 不要执行任何命令。

## 任务二：工具状态调整但保持安全边界

`configs/tools.yaml` 中：

- `filesystem_read` 可以从 `planned` 调整为 `enabled`，但必须保持 `risk_level: read_only` 或更保守级别。
- `filesystem_write` 必须仍为 `disabled`。
- `filesystem` 兼容别名如果保留，必须仍不是 `enabled`。
- `shell` 必须仍为 `disabled`。
- GitHub / Playwright / database / redis / pytest 等不得因为本任务被启用。

说明：这是本地白名单只读 adapter，不是 MCP Server 已接入。

## 任务三：orchestrator 支持只读文件读取计划，不默认读取

当前 orchestrator 只做 dry-run 计划和工具授权评估。

本任务中，orchestrator 不需要自动读取文件内容。

但可以新增以下能力之一，优先选择简单方案：

方案 A：只在 runtime CLI 增加 `--read-file` 参数

```bash
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --read-file README.md
```

要求：

- 只有显式传 `--read-file` 才读取。
- 仍然必须经过 `FilesystemReadPolicy`。
- 读取结果只作为 dry-run 上下文展示，不触发真实工具执行链。
- 不允许一次读取多个文件，第一版只支持一个路径。

方案 B：先不改 CLI，只提供 adapter 单测和文档

如果认为 CLI 参数会扩大范围，可以选择方案 B，但必须在 README 说明下一步如何接入 CLI。

优先建议实现方案 A，因为它能验证真实只读能力，但必须严格限制。

## 任务四：更新输出与文档

如果实现方案 A，请更新：

- `src/ai_test_assistant/runtime/cli.py`
- `src/ai_test_assistant/runtime/output.py`
- `tests/test_runtime_cli.py`
- `src/ai_test_assistant/runtime/README.md`

CLI 输出必须明确：

- 是否请求读取文件
- 文件读取是否被允许
- 读取路径
- 是否被截断
- 拒绝原因

更新：

- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/filesystem/README.md`
- `src/ai_test_assistant/tool_registry/README.md`

必须明确：

- 当前已实现本地白名单只读 adapter。
- 当前仍未接入 MCP Server。
- 当前仍不开放写文件。
- 当前只允许显式读取单个仓库相对路径。

## 测试要求

新增测试至少覆盖：

1. 允许读取临时仓库内 `README.md`。
2. 允许读取 `docs/example.md`。
3. 禁止读取 `.env`。
4. 禁止读取 `.git/config`。
5. 禁止读取 `../outside.txt`。
6. 禁止读取包含 `secret` / `token` / `password` 的路径。
7. 文件不存在时返回结构化拒绝结果。
8. 二进制文件被拒绝或安全处理。
9. 大文件被拒绝或截断，并标记 `truncated`。
10. 如果实现 `--read-file`，CLI 明确展示读取结果或拒绝原因。

## 禁止事项

- 不要接入 MCP Server。
- 不要调用 MCP SDK。
- 不要实现 filesystem_write。
- 不要读仓库外文件。
- 不要读 `.env`、`.git/`、`.assistant/`、密钥、token、密码类文件。
- 不要执行 shell 命令。
- 不要访问外部网络。
- 不要自动根据自然语言猜测并读取多个文件。
- 不要把本地 adapter 写成通用文件管理器。

## 验收命令

```bash
pytest
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --read-file README.md
python scripts/run_assistant.py "请读取环境配置" --dry-run --read-file .env
python scripts/run_assistant.py "请修改仓库配置并更新工作流" --dry-run
```

## 完成标准

- 本地只读 adapter 可用。
- 所有读取都经过 `FilesystemReadPolicy`。
- `filesystem_read` 可作为 enabled read_only 工具存在，但不是 MCP 接入。
- `filesystem_write`、`shell`、MCP/network 类工具仍未启用。
- CLI 如实现 `--read-file`，必须只支持显式单文件读取。
- 所有测试通过。
- 文档真实说明当前状态。