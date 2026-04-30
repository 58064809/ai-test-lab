# Codex Task 033：GitHub MCP read 正文解析确认与最小增强

## 背景

031/032 已完成 GitHub MCP read 最小接入和 live smoke 收口。

用户本地真实验证结果：

```text
允许读取=是 | 来源=github_mcp | 路径=README.md | 字符数=81 | 已截断=否
结果说明：Read allowed through GitHub MCP.
文件预览：
  successfully downloaded text file (SHA: d158cba4bd47f227961ff37268956ffb46f63eef)
```

这说明 GitHub MCP read 已经可用，但当前返回内容只是下载成功提示和 SHA，并不是 README 正文。

本任务目标：确认官方 `github/github-mcp-server` 的 `get_file_contents` 返回结构，并在不自研 GitHub REST API fallback 的前提下，尽可能提取正文。

## 最高原则

1. 继续使用官方 GitHub MCP Server：`github/github-mcp-server`。
2. 继续使用 MCP SDK / 协议。
3. 不自研 GitHub REST API client。
4. 不实现 REST fallback。
5. 不开放 GitHub write。
6. 不开放 issue / PR / comment / merge / push / 改文件。
7. 不开放 shell。
8. 不把 token 写入仓库、配置、日志或测试快照。
9. 不打印 token。
10. 不实现目录批量读取。
11. 不实现全仓搜索。
12. 只围绕 `get_file_contents` 的返回结构做正文解析增强。
13. Markdown 文档默认中文。

## 必须先阅读

- `src/ai_test_assistant/github/mcp_client.py`
- `tests/test_github_mcp_read_client.py`
- `docs/github-mcp-quickstart.md`
- `configs/mcp/github-server.example.json`
- `configs/tools.yaml`
- `docs/current-status.md`
- `docs/next-steps.md`

## 任务一：确认官方返回结构，不要猜

请基于官方 `github/github-mcp-server` 文档、工具描述、SDK 返回对象，确认 `get_file_contents` 对文本文件可能返回的结构。

重点检查：

- `tool_result.structuredContent`
- `tool_result.structured_content`
- `tool_result.content`
- content item 是否包含 text
- 返回内容是否可能是：
  - 文件正文
  - 下载成功消息 + SHA
  - 包含 `content` / `text` / `encoding` / `sha` / `download_url` 等字段的 dict

要求：

- 能确认的写入文档。
- 不能确认的明确写“待 live debug 验证”。
- 不要编造官方返回格式。

## 任务二：增强 `_extract_text_content()` 的结构化解析

更新：

```text
src/ai_test_assistant/github/mcp_client.py
```

要求在不破坏现有行为的前提下，增强 `_extract_text_content()`：

1. 如果 `structuredContent` / `structured_content` 是 dict：
   - 优先读取文件正文类字段，例如 `content`、`text`、`file_content`、`data`。
   - 如果字段是字符串，直接返回。
   - 如果字段是 dict/list，安全转为字符串或 JSON 字符串。
2. 如果 dict 中存在 base64 编码标识，例如：
   - `encoding == "base64"`
   - 且 `content` 是字符串
   - 则尝试 base64 decode 为 UTF-8 文本。
3. 如果 `tool_result.content` 是 text chunks：
   - 拼接 text chunk。
   - 如果只有“successfully downloaded text file (SHA: xxx)”这种提示，也保持原样返回，不要伪造正文。
4. 如果没有可读文本，继续返回结构化拒绝错误。
5. 输出内容继续受 128KB 限制。
6. 所有错误信息必须避免 token 泄露。

## 任务三：新增 live debug 入口，但不得默认启用

可以新增一个安全的调试开关，例如 CLI 参数：

```powershell
--github-debug-raw-result
```

或者只在 `GitHubMcpReadClient` 内部提供测试辅助方法。

如果新增 CLI 参数，要求：

- 默认关闭。
- 不打印 token。
- 不打印请求 header。
- 不打印环境变量。
- 只打印 tool_result 的安全结构摘要，例如：字段名、content item 类型、是否存在 structuredContent，不打印完整大内容。
- 不影响正常 `--github-read-file` 输出。

如果不新增 CLI 参数，也可以在文档里写明暂不开放 runtime debug，只通过测试 mock 官方返回结构。

## 任务四：测试覆盖

更新：

```text
tests/test_github_mcp_read_client.py
```

至少覆盖：

1. `structuredContent.content` 为普通字符串时，提取正文。
2. `structured_content.text` 为普通字符串时，提取正文。
3. `structuredContent` 中 `encoding=base64` 且 `content` 为 base64 字符串时，正确解码 UTF-8。
4. `tool_result.content` 为 text chunks 时，继续拼接。
5. `tool_result.content` 只有 `successfully downloaded text file (SHA: xxx)` 时，保持原样，不伪造正文。
6. token 不会出现在错误信息中。
7. `github_write` 仍 disabled。
8. `shell` 仍 disabled。
9. `filesystem_write` 仍 disabled。

如需新增工具函数测试，可以新增测试文件，但不要真实访问 GitHub 网络。

## 任务五：文档更新

更新：

- `docs/github-mcp-quickstart.md`
- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/github/README.md`

必须明确：

- GitHub MCP read 已通过 live smoke。
- 当前已增强正文解析逻辑，但是否能拿到完整正文取决于官方 `get_file_contents` 返回结构。
- 如果官方只返回下载成功提示 + SHA，runtime 不应伪造正文。
- 不允许为了正文解析自研 GitHub REST fallback。
- 后续如果需要完整文件正文，有两条合规路线：
  1. 继续确认官方 MCP 是否支持返回正文；
  2. 使用已经存在的 GitHub connector / 官方 SDK 作为独立 read-only 工具，但需要另起任务、单独授权、单独边界。

## 禁止事项

- 不要自研 GitHub REST API fallback。
- 不要新增 requests/httpx 调 GitHub API。
- 不要开放 GitHub write。
- 不要创建 issue / PR / comment。
- 不要 merge / push / 改文件。
- 不要打印 token。
- 不要把 token 写入配置或日志。
- 不要开放 shell。
- 不要实现目录批量读取。
- 不要实现全仓搜索。
- 不要伪造 README 正文。

## 验收命令

```bash
pytest
```

本地手动验证仍使用：

```powershell
python scripts/run_assistant.py "读取 GitHub README 并分析" --dry-run --github-repo 58064809/ai-test-lab --github-read-file README.md
```

预期：

- 如果官方返回正文，则显示 README 正文预览。
- 如果官方仍只返回下载成功提示 + SHA，则保持原样，并在文档中说明。
- `.env` 等敏感路径仍拒绝。

## 完成标准

- GitHub MCP `get_file_contents` 返回结构解析更稳健。
- 不自研 GitHub REST fallback。
- 不开放任何 GitHub 写能力。
- 工具边界保持不变。
- 所有测试通过。
