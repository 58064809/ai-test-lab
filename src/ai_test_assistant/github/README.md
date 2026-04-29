# GitHub MCP read

当前已接入 GitHub MCP read 最小能力，采用官方 `github/github-mcp-server`，通过 MCP SDK / 协议调用，不自研 GitHub API client。

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
