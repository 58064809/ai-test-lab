# Codex Task 031：接入 GitHub MCP read 最小能力

## 背景

当前已经完成两个真实工具能力：

- `filesystem_mcp_read`：官方 filesystem MCP 只读单文件读取
- `pytest_runner`：受控 pytest 最小真实执行

下一步接入 GitHub read 能力，用于读取仓库、文件、Issue / PR 元数据，辅助后续审查和任务推进。

本任务优先采用官方 GitHub MCP Server：

```text
github/github-mcp-server
https://github.com/github/github-mcp-server
```

这不是自研 GitHub API client，也不是自研 MCP Server。

## 目标

落地 GitHub MCP read 的最小准备与 runtime 只读入口。

第一阶段只支持只读能力：

- 读取仓库基本信息
- 读取文件内容或文件元数据
- 读取 Issue / PR 元数据，如后续工具暴露且可安全确认

禁止写操作：

- 不创建 Issue
- 不评论 PR
- 不改文件
- 不 push
- 不 merge
- 不改 label / milestone / assignee

## 最高原则

1. 使用官方 GitHub MCP Server：`github/github-mcp-server`。
2. 使用成熟 MCP SDK / 协议，不自研 MCP 协议。
3. 不自研 GitHub API client。
4. 第一阶段只开放 `github_read`。
5. `github_write` 保持 disabled。
6. 不执行 shell 通用命令。
7. 不把 token 写入仓库。
8. 不把 token 打印到日志。
9. 不访问非用户明确指定的仓库。
10. 不开放任意 GitHub 写操作。
11. Markdown 文档默认中文。

## 必须先阅读

- `pyproject.toml`
- `configs/tools.yaml`
- `configs/mcp/filesystem-server.example.json`
- `src/ai_test_assistant/filesystem/mcp_client.py`
- `src/ai_test_assistant/runtime/cli.py`
- `src/ai_test_assistant/runtime/output.py`
- `src/ai_test_assistant/tool_registry/README.md`
- `docs/current-status.md`
- `docs/next-steps.md`
- `docs/local-environment-prerequisites.md`

## 任务一：新增 GitHub MCP quickstart 文档

新增：

```text
docs/github-mcp-quickstart.md
```

文档必须包含：

```text
采用方案：github/github-mcp-server
目标：只读 GitHub 仓库信息
不做：写 Issue、写 PR、改文件、merge、push
前置条件：GitHub Token / GitHub CLI 或 Docker，如官方方案要求
Token 权限建议：最小只读权限
Windows 注意事项：
最小配置示例：
runtime 入口：
安全边界：
失败处理：
下一步：
```

要求：

- 如果官方 server 需要 `GITHUB_PERSONAL_ACCESS_TOKEN` 或等价环境变量，只写环境变量名，不写真实 token。
- 文档必须明确 token 不进仓库、不进日志。
- 文档必须明确第一阶段只读。
- 不要写复杂选型。

## 任务二：新增 GitHub MCP 配置模板

新增：

```text
configs/mcp/github-server.example.json
```

要求：

- 只写模板。
- 不包含真实 token。
- 不写死用户账号。
- 不写死私有仓库敏感信息。
- 如官方 server 推荐 Docker，按官方方式写模板。
- 如官方 server 推荐二进制或其他方式，按官方方式写模板。
- 如果 Codex 无法确认官方启动命令，可以保守写“待用户按官方 README 补充”，但不要编。

## 任务三：新增 GitHub MCP read client

新增：

```text
src/ai_test_assistant/github/
  __init__.py
  mcp_client.py
  README.md
```

建议模型：

```python
class GitHubReadResult:
    allowed: bool
    operation: str
    repository: str | None
    target: str | None
    content: str | None
    reason: str
```

建议 client：

```python
class GitHubMcpReadClient:
    async def read_repository_info(self, repository: str) -> GitHubReadResult: ...
    async def read_file(self, repository: str, path: str, ref: str | None = None) -> GitHubReadResult: ...
```

要求：

1. 只允许 repository 明确传入，例如 `58064809/ai-test-lab`。
2. repository 格式必须校验为 `owner/repo`。
3. path 必须是仓库相对路径。
4. 禁止 path 绝对路径。
5. 禁止 `..` 路径穿越。
6. 禁止 token / secret / password / `.env` 类路径。
7. 只允许选择只读 GitHub MCP tool。
8. 如果无法确认只读工具，返回结构化拒绝结果。
9. 不调用写工具。
10. 不实现 GitHub REST API 兜底。
11. 不打印 token。
12. 输出内容要限制长度，例如 128KB。

如果官方 GitHub MCP server 在本地测试环境不方便启动，单测可以 mock MCP SDK session，但代码结构必须真实使用 MCP SDK / 协议，不要手写 GitHub API。

## 任务四：runtime CLI 新增显式 GitHub read 入口

更新：

```text
src/ai_test_assistant/runtime/cli.py
src/ai_test_assistant/runtime/output.py
```

新增参数：

```powershell
--github-repo 58064809/ai-test-lab
--github-read-file README.md
```

可选：

```powershell
--github-ref master
```

第一阶段只要求支持读取文件。

示例：

```powershell
python scripts/run_assistant.py "读取 GitHub README 并分析" --dry-run --github-repo 58064809/ai-test-lab --github-read-file README.md
```

要求：

- 必须显式提供 `--github-repo`。
- 必须显式提供 `--github-read-file`。
- 不自动根据自然语言猜仓库或文件。
- 输出来源标记为 `github_mcp`。
- 默认只展示预览。
- `--show-file-content` 才展示完整允许内容。
- 读取结果进入 orchestrator dry-run context。
- memory 仍只写元信息，不写 content。

## 任务五：工具状态更新

更新：

```text
configs/tools.yaml
```

要求：

- `github_read` 可以改成 `enabled`，但 risk_level 保持 `external_network` 或更保守。
- `github_write` 必须保持 `disabled`。
- `shell` 必须保持 `disabled`。
- `filesystem_write` 必须保持 `disabled`。
- notes 明确：只读 GitHub MCP，不开放写操作。

## 任务六：测试要求

新增或更新：

```text
tests/test_github_mcp_read_client.py
tests/test_runtime_cli.py
tests/test_tool_registry.py
```

至少覆盖：

1. repository 格式必须是 `owner/repo`。
2. 禁止空 repository。
3. 禁止文件 path 绝对路径。
4. 禁止 `..` 路径穿越。
5. 禁止 `.env`、token、secret、password 路径。
6. 只选择只读 MCP 工具。
7. CLI 缺少 `--github-repo` 时拒绝。
8. CLI 缺少 `--github-read-file` 时不触发 GitHub read。
9. CLI 输出来源为 `github_mcp`。
10. memory 只保存元信息，不保存 content。
11. `github_read` 为 enabled。
12. `github_write` 仍 disabled。
13. `shell` 仍 disabled。
14. `filesystem_write` 仍 disabled。

## 任务七：文档更新

更新：

- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/github/README.md`
- `src/ai_test_assistant/runtime/README.md`
- `src/ai_test_assistant/tool_registry/README.md`

必须明确：

- 已接入 GitHub MCP read 最小能力。
- 只支持显式仓库和显式文件读取。
- 不支持写操作。
- 不保存 token。
- 不打印 token。
- `github_write` 未开放。

## 禁止事项

- 不要自研 GitHub API client。
- 不要实现 GitHub write。
- 不要创建 issue / PR / comment。
- 不要 merge / push / 改文件。
- 不要把 token 写入配置文件。
- 不要把 token 打印到输出。
- 不要开放 shell。
- 不要自动猜仓库或文件。
- 不要实现目录批量读取。
- 不要实现搜索全仓库。

## 验收命令

自动测试：

```bash
pytest
```

手动验证，需用户本地配置 GitHub Token 后执行：

```powershell
python scripts/run_assistant.py "读取 GitHub README 并分析" --dry-run --github-repo 58064809/ai-test-lab --github-read-file README.md
```

## 完成标准

- GitHub MCP read client 结构落地。
- runtime 有显式 GitHub read 入口。
- 不开放 GitHub write。
- 不自研 GitHub API client。
- 工具边界测试通过。
- 所有测试通过。
