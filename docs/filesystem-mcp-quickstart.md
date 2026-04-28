# filesystem MCP Quickstart

## 采用方案

采用官方 / 主流方案：

- filesystem server：`@modelcontextprotocol/server-filesystem`
- Python client SDK：`mcp`

## 目标

把 filesystem MCP 只读能力接入当前 runtime，并且只开放显式单文件读取入口：

```powershell
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --mcp-read-file README.md
```

## 不做

- 不开放 `filesystem_write`
- 不开放 `shell`
- 不扩展 `LocalFilesystemReadAdapter`
- 不做多文件读取、目录读取、`glob` 或自动上下文收集
- 不自动根据自然语言猜文件
- 不写死用户本地路径

## Windows 前置条件

详细前置条件见：[local-environment-prerequisites.md](local-environment-prerequisites.md)

本阶段至少需要本机可直接使用：

- `Git`
- `Python`
- `pytest`
- `Node.js`
- `npm`
- `npx`

`nvm-windows` 是可选，不是必装。

当前已完成的本地验证结果：

- `node -v`：`v24.15.0`
- `npm -v`：`11.12.1`
- `npx -v`：`11.12.1`

## 最小配置示例

示例文件见：[filesystem-server.example.json](../configs/mcp/filesystem-server.example.json)

核心思路：

- 使用 `@modelcontextprotocol/server-filesystem`
- 只传一个仓库根目录参数
- Python runtime 通过官方 `mcp` SDK 走 stdio client
- 示例配置保留 `<ABSOLUTE_PATH_TO_AI_TEST_LAB>` 占位符
- 不写死用户本机真实路径

## runtime 入口

当前 runtime 已支持两个显式单文件读取入口：

- `--read-file`：走本地 fallback `LocalFilesystemReadAdapter`
- `--mcp-read-file`：走 `filesystem_mcp_read`，通过 filesystem MCP server 读取

要求：

- 两者都只支持单个显式仓库相对路径文件
- 读取前都必须经过 `FilesystemReadPolicy`
- 默认只展示预览
- 只有显式传 `--show-file-content` 才展示完整允许内容
- 写入 memory 时只保存文件元信息，不保存 `content`

## 本地验证命令

先验证官方 server 本身可启动：

```powershell
npx -y @modelcontextprotocol/server-filesystem .
```

当前已完成的本地验证结果：

- 命令：`npx -y @modelcontextprotocol/server-filesystem .`
- 输出：`Secure MCP Filesystem Server running on stdio`

runtime 手动验证命令：

```powershell
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --mcp-read-file README.md
python scripts/run_assistant.py "请读取环境配置" --dry-run --mcp-read-file .env
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --mcp-read-file README.md --show-file-content
```

## live smoke 验证

建议在项目独立 `.venv` 中执行下面三条命令：

```powershell
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --mcp-read-file README.md
python scripts/run_assistant.py "请读取环境配置" --dry-run --mcp-read-file .env
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --mcp-read-file README.md --show-file-content
```

预期：

- 第一条会通过 `filesystem_mcp` 读取 `README.md`，且不再识别为 `unknown`
- 第二条会被 `FilesystemReadPolicy` 拒绝，原因包含 `Sensitive file is blocked.`
- 第三条只有显式传 `--show-file-content` 时才展示完整允许内容

如果用于 MCP 客户端配置，继续使用绝对路径占位符：

```powershell
npx -y @modelcontextprotocol/server-filesystem <ABSOLUTE_PATH_TO_AI_TEST_LAB>
```

说明：

- `.` 只适合当前目录已经是仓库根目录的场景。
- `<ABSOLUTE_PATH_TO_AI_TEST_LAB>` 需要替换为用户本机仓库绝对路径。
- 本仓库文档和示例配置不写死任何用户本地盘符绝对路径。

## 安全边界

- `filesystem_mcp_read` 当前已启用，但只开放 `read_only`
- `filesystem_write` 继续保持 `disabled`
- `shell` 继续保持 `disabled`
- 第一阶段只考虑显式单文件 `filesystem_read`
- 读取前先走 `FilesystemReadPolicy`
- policy 拒绝 `.env`、`.git/`、`.assistant/`、token、secret、password 类路径时，不启动 MCP server

关于根目录限制：

- MCP server 启动时只传入一个根目录参数：`repo_root`
- 不访问仓库外目录

关于只读边界：

- 只调用单文件读取相关工具
- 不调用写文件、删文件、建目录类工具
- 不实现多文件读取、目录读取、`glob` 或自动上下文收集

## 失败处理

如果本地验证失败，先检查：

1. `Node.js`、`npm`、`npx` 是否已安装。
2. Python 环境是否已安装项目依赖，包含官方 MCP SDK `mcp`。
3. `npx` 是否能拉起 `@modelcontextprotocol/server-filesystem`。
4. 当前目录是否就是仓库根目录，或者绝对路径是否正确。
5. 是否被 npm 源、代理或网络访问问题阻断。

如果 `--mcp-read-file .env`、`--mcp-read-file .git/config` 这类路径被拒绝，属于预期安全行为，不应绕过 policy。

## 下一步

下一步继续保持最小边界：

- 保留 `LocalFilesystemReadAdapter` 作为 fallback
- 不开放 `filesystem_write`
- 不开放 `shell`
- 不改成多文件、目录读取或自动上下文收集
