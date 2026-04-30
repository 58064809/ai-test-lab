# GitHub MCP read

当前已接入 GitHub MCP read 最小能力，采用官方 `github/github-mcp-server`，通过 MCP SDK / 协议调用，不自研 GitHub API client。

GitHub MCP read 已通过用户本地 live smoke。当前已增强正文解析逻辑，但能否拿到完整正文取决于官方 `get_file_contents` 返回结构以及 MCP SDK 是否透传 embedded resource。

当前只开放显式单文件读取：

```powershell
python scripts/run_assistant.py "读取 GitHub README 并分析" --dry-run --github-repo 58064809/ai-test-lab --github-read-file README.md
```

安全边界：

- 必须显式传入 `--github-repo owner/repo` 和 `--github-read-file repo-relative-path`。
- 不根据自然语言自动猜仓库或文件。
- 不支持目录批量读取，不支持全仓库搜索。
- 禁止绝对路径、`..` 路径穿越、`.env`、`token`、`secret`、`password` 类路径。
- 不保存 token，不打印 token。
- 不开放 issue / PR / comment / merge / push / 改文件。
- `github_write`、`shell`、`filesystem_write` 保持 disabled。

正文解析边界：

- 优先解析 `structuredContent` / `structured_content` 中的正文类字段。
- 支持 `encoding=base64` 的结构化正文解码。
- 支持 MCP embedded resource 的 `text` 和 base64 `blob`。
- 如果官方只返回 `successfully downloaded text file (SHA: xxx)`，保持原样，不伪造正文。
- 不开放 runtime raw debug；如需 live debug，另起任务并只输出安全结构摘要。
- 不自研 GitHub REST API fallback，不新增 `requests` / `httpx` 直连 GitHub API。

后续如必须稳定读取完整正文，合规路线只有两类：

1. 继续确认官方 MCP 是否支持稳定返回正文。
2. 另起任务评估已有 GitHub connector / 官方 SDK 作为独立 read-only 工具，并单独授权、单独边界。
