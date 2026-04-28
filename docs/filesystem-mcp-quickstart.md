# filesystem MCP Quickstart

## 采用方案

采用官方 / 主流方案：`@modelcontextprotocol/server-filesystem`

## 目标

只允许读取 `ai-test-lab` 仓库目录，用于后续最小 MCP 接入验证。

## 不做

- 不开放 `filesystem_write`
- 不开放 `shell`
- 不扩展 `LocalFilesystemReadAdapter`
- 不做多文件读取、目录读取、`glob` 或自动上下文收集
- 不写死用户本地路径
- 不改当前 runtime CLI

## Windows 前置条件

详细前置条件见：[local-environment-prerequisites.md](/D:/TestHome/ai-test-lab/docs/local-environment-prerequisites.md)

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

示例文件见：[filesystem-server.example.json](/D:/TestHome/ai-test-lab/configs/mcp/filesystem-server.example.json)

核心思路：

- 使用 `@modelcontextprotocol/server-filesystem`
- 只传一个仓库根目录参数
- 示例配置保留 `<ABSOLUTE_PATH_TO_AI_TEST_LAB>` 占位符
- 不写死用户本机真实路径

## 本地验证命令

如果直接在仓库根目录执行，最小启动命令如下：

```powershell
npx -y @modelcontextprotocol/server-filesystem .
```

当前已完成的本地验证结果：

- 命令：`npx -y @modelcontextprotocol/server-filesystem .`
- 输出：`Secure MCP Filesystem Server running on stdio`

如果用于 MCP 客户端配置，继续使用绝对路径占位符：

```powershell
npx -y @modelcontextprotocol/server-filesystem <ABSOLUTE_PATH_TO_AI_TEST_LAB>
```

说明：

- `.` 只适合当前目录已经是仓库根目录的场景。
- `<ABSOLUTE_PATH_TO_AI_TEST_LAB>` 需要替换为用户本机仓库绝对路径。
- 本阶段只验证官方 server 是否存在、是否可启动。
- 本仓库当前不会在测试或 runtime 中自动运行该命令。

## 安全边界

- 当前 Python runtime 还没有 MCP client，因此 `filesystem_mcp_read` 仍保持 `planned`
- 当前可用的真实读文件能力仍然是本地 `filesystem_read` fallback
- `filesystem_write` 继续保持 `disabled`
- `shell` 继续保持 `disabled`
- 第一阶段只考虑 `filesystem_read`

关于根目录限制：

- 示例配置只向 server 传入一个仓库根目录参数
- 不访问仓库外目录

关于只读边界：

- 本阶段不开放任何写能力
- 不继续扩展 `LocalFilesystemReadAdapter`
- 不实现多文件读取、目录读取、`glob` 或自动上下文收集

## 失败处理

如果本地验证失败，先检查：

1. `Node.js`、`npm`、`npx` 是否已安装。
2. `npx` 是否能拉起 `@modelcontextprotocol/server-filesystem`。
3. 当前目录是否就是仓库根目录，或者绝对路径是否正确。
4. 是否被 npm 源、代理或网络访问问题阻断。

如果仍失败，记录错误信息，并回到“本地前置条件待补齐”状态，不继续复杂选型，也不回退为扩展本地 adapter。

## 下一步

下一步只保持最小边界：

- 继续保持 `filesystem_mcp_read=planned`，直到真实 MCP client 接入代码存在。
- 不扩展 `LocalFilesystemReadAdapter`。
- 不开放 `filesystem_write`。
- 不修改 runtime CLI。
