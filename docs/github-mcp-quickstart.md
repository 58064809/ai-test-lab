# GitHub MCP quickstart

## 采用方案

采用官方 GitHub MCP Server：`github/github-mcp-server`。

本项目第一阶段只接入 GitHub read 最小能力，通过 MCP SDK / 协议调用官方 server，不自研 GitHub API client。

## 目标

只读 GitHub 仓库信息，当前 runtime 入口优先支持显式读取单个仓库文件。

## 不做

不写 Issue，不写 PR，不评论，不改文件，不 merge，不 push，不改 label / milestone / assignee。

## 前置条件

- GitHub Token，例如环境变量 `GITHUB_PERSONAL_ACCESS_TOKEN`。
- Docker，使用官方容器镜像 `ghcr.io/github/github-mcp-server`。
- Python 项目依赖中已包含 `mcp` SDK。

## Token 权限建议

使用最小只读权限。Token 只放在本机环境变量中，不写入仓库配置文件，不写入日志，不在 CLI 输出中打印。

## Windows 注意事项

PowerShell 中只设置环境变量名和值到当前用户环境或当前进程环境。配置模板只引用 `GITHUB_PERSONAL_ACCESS_TOKEN` 这个变量名，不包含真实 token。

## 最小配置示例

见 [configs/mcp/github-server.example.json](../configs/mcp/github-server.example.json)。

关键边界：

- `GITHUB_READ_ONLY=1`
- `GITHUB_TOOLS=get_file_contents`
- 只传环境变量名 `GITHUB_PERSONAL_ACCESS_TOKEN`，不写真实 token。

## runtime 入口

```powershell
python scripts/run_assistant.py "读取 GitHub README 并分析" --dry-run --github-repo 58064809/ai-test-lab --github-read-file README.md
```

可选指定 ref：

```powershell
python scripts/run_assistant.py "读取 GitHub README 并分析" --dry-run --github-repo 58064809/ai-test-lab --github-read-file README.md --github-ref master
```

必须显式提供 `--github-repo` 和 `--github-read-file`。不根据自然语言自动猜仓库或文件。

默认只展示预览，只有显式传入 `--show-file-content` 才展示完整允许内容。内容最大限制为 128KB。

## live smoke 验证结果

- 验证时间：用户本地已验证。
- 验证命令：`python scripts/run_assistant.py "读取 GitHub README 并分析" --dry-run --github-repo 58064809/ai-test-lab --github-read-file README.md`
- 验证结果：允许读取=是，来源=github_mcp，路径=README.md。
- 返回 SHA：`d158cba4bd47f227961ff37268956ffb46f63eef`
- 敏感文件验证：`.env` 被拒绝，原因为 `Sensitive GitHub file path is blocked.`

当前 GitHub MCP read 返回的是下载成功提示和 SHA，不一定直接返回完整文件正文。后续如需完整正文解析，应另起任务确认官方返回结构；不得为了正文解析自研 GitHub REST API fallback。

## get_file_contents 返回结构确认

已基于官方 `github/github-mcp-server` 源码确认：

- `get_file_contents` 仍是只读工具，`readOnlyHint=true`。
- 小于 1MB 的文本文件会通过 MCP resource 返回，外层 text chunk 形如 `successfully downloaded text file (SHA: xxx)`，正文在嵌入 resource 的 `text` 字段中。
- 空文件会返回空文本 resource 和 `successfully downloaded empty file (SHA: xxx)`。
- 大文件会返回 resource link 和下载提示，不直接返回完整正文。
- 二进制文件会返回 resource blob。
- 目录内容会以 JSON text 返回。

当前 `_extract_text_content()` 已增强解析：

- 支持 `structuredContent` / `structured_content` 中的 `content`、`text`、`file_content`、`data`、`message`。
- 支持 `encoding=base64` 且 `content` 为字符串时解码 UTF-8。
- 支持 MCP embedded resource 的 `text` 和 base64 `blob`。
- 支持普通 text chunks 拼接。

如果官方返回中只有 `successfully downloaded text file (SHA: xxx)`，runtime 会保持原样，不伪造 README 正文。当前不开放 runtime raw debug 参数；返回结构通过单元测试 mock 覆盖，后续需要 live debug 时只能输出字段名和类型摘要，不得打印 token、header 或环境变量。

## 安全边界

- `github_read` 可 enabled，但属于 `external_network`。
- `github_write` 必须 disabled。
- `shell` 必须 disabled。
- `filesystem_write` 必须 disabled。
- 不保存 token。
- 不打印 token。
- 不开放 issue / PR / comment / merge / push / 改文件。
- 不实现目录批量读取。
- 不实现搜索全仓库。

## 失败处理

- 缺少 `--github-repo`：拒绝执行 GitHub read。
- 缺少 `--github-read-file`：不触发 GitHub read。
- 仓库不是 `owner/repo`：返回结构化拒绝。
- 文件路径为绝对路径、包含 `..`、指向 `.env` / `token` / `secret` / `password`：返回结构化拒绝。
- MCP SDK、Docker、token 或官方 server 不可用：返回结构化失败原因，不打印 token。

## 下一步

- 继续用真实 token 在本地手工验证正文 resource 是否能被当前 MCP SDK 透传。
- 如需完整文件正文，优先继续确认官方 MCP 是否支持返回正文；也可以另起任务评估已有 GitHub connector / 官方 SDK 作为独立 read-only 工具，但必须单独授权、单独边界。
- 后续如需读取 issue / PR 元数据，必须先确认官方 read-only tool 名称和参数，再单独加白名单。
- `github_write` 继续保持不开放。
