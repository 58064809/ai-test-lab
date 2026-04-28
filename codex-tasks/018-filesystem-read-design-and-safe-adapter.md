# Codex Task 018：filesystem_read 接入前设计与安全适配方案

## 任务背景

017 已完成 MCP 接入前置选型与安全边界。下一步可以围绕首批低风险工具 `filesystem_read` 做接入前设计。

本任务仍然不真实接入 MCP Server，不读取真实业务文件，不开放真实工具执行。目标是先把 filesystem 只读能力的安全边界、路径白名单、敏感文件拦截、未来 adapter 接口和测试边界设计清楚。

## 最高原则

1. 不真实接入 MCP Server。
2. 不调用 MCP SDK。
3. 不执行本地命令。
4. 不访问外部网络。
5. 不开放 filesystem write。
6. 不读取真实业务敏感文件。
7. 不读取 `.env`、token、密钥、证书、数据库连接信息等敏感内容。
8. 不把设计文档或 dry-run adapter 包装成真实 MCP 接入。
9. 不写死任何电商业务规则。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/012-industrial-grade-selection-policy.md`
- `codex-tasks/017-mcp-selection-and-security-boundary.md`
- `docs/mcp-selection.md`
- `docs/mcp-security-policy.md`
- `docs/current-status.md`
- `src/ai_test_assistant/tool_registry/README.md`
- `src/ai_test_assistant/orchestrator/README.md`
- `configs/tools.yaml`

## 任务一：新增 filesystem_read 设计文档

新增：

```text
docs/filesystem-read-design.md
```

必须包含：

```text
目标：
非目标：
候选成熟方案：
选择策略：
权限等级：
路径白名单：
敏感文件黑名单：
读取限制：
dry-run 行为：
真实接入前置条件：
Windows 注意事项：
后续替换策略：
```

要求明确：

- `filesystem_read` 只允许读取仓库内低风险工程文件。
- 第一阶段建议白名单仅允许：
  - `README.md`
  - `AGENTS.md`
  - `docs/`
  - `agent-assets/`
  - `configs/*.yaml`
  - `src/ai_test_assistant/`
  - `tests/`
  - `validation/`
- 第一阶段必须禁止：
  - `.env`
  - `.assistant/`
  - `.git/`
  - `*.pem`
  - `*.key`
  - `*.crt`
  - `*token*`
  - `*secret*`
  - `*password*`
  - 数据库连接配置
  - 任何真实业务导出数据
- 当前仍不真实读取文件，只设计安全边界。

## 任务二：新增安全策略模型，但不真实读取文件

新增：

```text
src/ai_test_assistant/filesystem/
  __init__.py
  policy.py
  README.md

tests/test_filesystem_read_policy.py
```

要求：

1. 只实现路径安全策略，不实现真实文件读取。
2. 提供 `FilesystemReadPolicy` 或等价命名。
3. 能判断给定仓库相对路径是否允许作为未来 `filesystem_read` 读取目标。
4. 必须阻止路径穿越，例如：
   - `../.env`
   - `docs/../../.env`
5. 必须阻止敏感文件模式。
6. 必须允许白名单路径。
7. 必须返回结构化决策，例如：

```python
allowed: bool
reason: str
normalized_path: str | None
```

## 任务三：工具注册表保持 planned，不启用真实工具

检查并保持：

- `filesystem_read` 仍为 `planned`。
- `filesystem_write` 仍为 `disabled`。
- `filesystem` 兼容别名如果保留，也必须不是 enabled。

不要把任何 filesystem MCP 工具改成 enabled。

## 任务四：文档与状态同步

更新：

- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/tool_registry/README.md`

必须明确：

- 已完成 filesystem_read 接入前安全策略设计。
- 已新增路径安全策略模型。
- 当前仍未真实接入 MCP。
- 当前仍未真实读取文件。
- 当前 runtime CLI 仍不执行真实工具。

## 测试要求

新增测试至少覆盖：

1. 允许读取 `README.md`。
2. 允许读取 `docs/mcp-selection.md`。
3. 允许读取 `agent-assets/prompts/test-case-generation.md`。
4. 允许读取 `src/ai_test_assistant/orchestrator/README.md`。
5. 禁止读取 `.env`。
6. 禁止读取 `.assistant/memory.sqlite3`。
7. 禁止读取 `.git/config`。
8. 禁止路径穿越 `../.env`。
9. 禁止 `docs/../../.env`。
10. 禁止 `secret-token.txt` 或包含 secret/token/password 的路径。

## 禁止事项

- 不要真实读取文件内容。
- 不要接入 MCP Server。
- 不要调用 MCP SDK。
- 不要启用 filesystem_read。
- 不要开放 filesystem_write。
- 不要执行本地命令。
- 不要访问外部网络。
- 不要把策略模型包装成真实工具执行。

## 验收命令

```bash
pytest
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run
python scripts/run_assistant.py "请修改仓库配置并更新工作流" --dry-run
```

## 完成标准

- filesystem_read 设计文档完成。
- 路径安全策略模型完成。
- 测试覆盖白名单、黑名单和路径穿越。
- filesystem_read 仍未 enabled。
- 所有文档真实反映当前仍未接入 MCP、仍未真实读取文件。