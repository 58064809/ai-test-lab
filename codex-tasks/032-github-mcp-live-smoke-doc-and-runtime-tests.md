# Codex Task 032：GitHub MCP live smoke 收口与 runtime 授权测试补齐

## 背景

031 已完成 GitHub MCP read 最小能力接入，并经过用户本地真实验证：

```powershell
python scripts/run_assistant.py "读取 GitHub README 并分析" --dry-run --github-repo 58064809/ai-test-lab --github-read-file README.md
```

验证结果：

```text
允许读取=是 | 来源=github_mcp | 路径=README.md | 字符数=81 | 已截断=否
结果说明：Read allowed through GitHub MCP.
文件预览：
  successfully downloaded text file (SHA: d158cba4bd47f227961ff37268956ffb46f63eef)
```

另外 `.env` 读取拒绝也已通过：

```text
允许读取=否 | 来源=github_mcp | 路径=.env
结果说明：Sensitive GitHub file path is blocked.
```

本任务不是新增能力，而是把 031 的真实验证结果固化到文档，并补齐 runtime 层授权路径测试，防止后续回归。

## 最高原则

1. 不新增 GitHub 写能力。
2. 不开放 `github_write`。
3. 不开放 `shell`。
4. 不开放 `filesystem_write`。
5. 不自研 GitHub REST API client。
6. 不把 token 写入仓库、配置或日志。
7. 不打印 token。
8. 不新增目录批量读取、搜索全仓库、Issue / PR 写操作。
9. 只补文档和测试，除非测试暴露小问题才做最小修复。
10. Markdown 文档默认中文。

## 必须先阅读

- `docs/github-mcp-quickstart.md`
- `configs/mcp/github-server.example.json`
- `src/ai_test_assistant/github/mcp_client.py`
- `src/ai_test_assistant/runtime/cli.py`
- `src/ai_test_assistant/runtime/output.py`
- `configs/tools.yaml`
- `tests/test_github_mcp_read_client.py`
- `tests/test_runtime_cli.py`
- `docs/current-status.md`
- `docs/next-steps.md`

## 任务一：更新 GitHub MCP quickstart

更新：

```text
docs/github-mcp-quickstart.md
```

新增 “live smoke 验证结果” 小节，必须包含：

```text
验证时间：用户本地已验证
验证命令：python scripts/run_assistant.py "读取 GitHub README 并分析" --dry-run --github-repo 58064809/ai-test-lab --github-read-file README.md
验证结果：允许读取=是，来源=github_mcp，路径=README.md
返回 SHA：d158cba4bd47f227961ff37268956ffb46f63eef
敏感文件验证：.env 被拒绝，原因为 Sensitive GitHub file path is blocked.
```

要求：

- 不记录 token。
- 不写真实 token 示例。
- 不把 GitHub write 写成已接入。
- 明确当前 GitHub MCP read 返回的是下载成功提示和 SHA，不一定直接返回完整文件正文；后续如需完整正文解析，另起任务确认官方返回结构。

## 任务二：更新状态文档

更新：

- `docs/current-status.md`
- `docs/next-steps.md`

要求：

- 明确 `github_read` 已完成最小 read 接入和 live smoke 验证。
- 明确当前只支持显式 repo + 显式单文件读取。
- 明确 `.env` 等敏感路径拒绝已验证。
- 明确 `github_write`、`shell`、`filesystem_write` 仍未开放。
- 下一步建议可以是：GitHub read 返回正文解析增强 / Issue PR 只读元数据 / Allure 报告读取，不要直接进入写操作。

## 任务三：补 runtime 授权路径测试

更新：

```text
tests/test_runtime_cli.py
```

至少新增测试：

1. `--github-read-file README.md` 缺少 `--github-repo` 时返回错误，不启动 `GitHubMcpReadClient`。
2. `github_read` 未授权时返回错误，不启动 `GitHubMcpReadClient`。
3. `github_read` 授权通过时才调用 `GitHubMcpReadClient.read_file()`。
4. GitHub MCP read 输出中包含 `来源=github_mcp`。
5. GitHub MCP read 输出中包含“显式只读外部网络访问”风险提示。
6. `--write-memory` 时 GitHub MCP read 只保存元信息，不保存 content。

测试要求：

- 不真实启动 Docker。
- 不真实访问 GitHub 网络。
- 使用 stub/mock `GitHubMcpReadClient`。
- 确认 token 不会出现在输出里。

## 任务四：补工具边界测试

如已有 `tests/test_tool_registry.py`，补充；如果没有，新增或更新合适的测试文件。

至少确认：

1. `github_read` 为 `enabled`。
2. `github_read` 风险为 `external_network`。
3. `github_write` 为 `disabled`。
4. `shell` 为 `disabled`。
5. `filesystem_write` 为 `disabled`。

## 任务五：保留当前 GitHub MCP client 边界

检查但不要大改：

- `GitHubMcpReadClient` 仍使用 MCP SDK。
- 仍启动官方 `ghcr.io/github/github-mcp-server`。
- 仍只允许 `get_file_contents`。
- 仍保留 `GITHUB_READ_ONLY=1` / `GITHUB_TOOLS=get_file_contents`。
- 仍不自研 GitHub REST API client。
- 仍不打印 token。

## 禁止事项

- 不要实现 GitHub write。
- 不要创建 issue / PR / comment。
- 不要 merge / push / 改文件。
- 不要把 token 写入配置或日志。
- 不要开放 shell。
- 不要自动猜仓库或文件。
- 不要实现目录批量读取。
- 不要实现搜索全仓库。
- 不要为了解析 README 正文而自研 GitHub REST API fallback。

## 验收命令

```bash
pytest
```

手动验证命令保留在文档中：

```powershell
python scripts/run_assistant.py "读取 GitHub README 并分析" --dry-run --github-repo 58064809/ai-test-lab --github-read-file README.md
python scripts/run_assistant.py "读取 GitHub 环境配置" --dry-run --github-repo 58064809/ai-test-lab --github-read-file .env
```

## 完成标准

- GitHub MCP live smoke 成功结果已写入文档。
- runtime 授权路径测试补齐。
- GitHub MCP read 仍只读。
- GitHub write / shell / filesystem_write 仍禁用。
- 所有测试通过。
