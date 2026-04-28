# Codex Task 027：本地环境依赖检查与 filesystem MCP 快速启动

## 背景

前面已经确定：filesystem MCP 直接走官方 / 主流生态方案，不再继续复杂选型，也不继续扩展本地 `LocalFilesystemReadAdapter`。

现在需要把本地必须安装的工具、验证命令和失败修复路径一次性落清楚，避免继续空转。

## 目标

让用户在 Windows 本地能明确知道：

- 需要安装什么
- 怎么检查是否安装成功
- 怎么启动 filesystem MCP server
- 如果失败，Codex 应该怎么自动修复或给出下一步

## 必须安装 / 确认的工具

### 1. Node.js LTS

用途：运行 `npx` 和官方 filesystem MCP server。

必须验证：

```bash
node -v
npm -v
npx -v
```

要求：

- 能输出版本号即可。
- 推荐 Node.js LTS。
- 不强制安装 nvm。

### 2. nvm-windows，可选

用途：管理多个 Node.js 版本。

要求：

- 如果用户已经有 Node.js LTS，暂时不需要安装 nvm。
- 如果 `node -v` 不存在，或者版本混乱，再建议安装 nvm-windows。

### 3. Python 运行环境

当前项目已有 Python 工程，需确认：

```bash
python --version
pytest --version
```

如果 pytest 不存在，Codex 应根据当前项目依赖文件给出安装命令，不要瞎猜。

### 4. Git

用于仓库操作：

```bash
git --version
```

### 5. filesystem MCP server

采用官方 / 主流方案：

```bash
npx -y @modelcontextprotocol/server-filesystem <ABSOLUTE_PATH_TO_AI_TEST_LAB>
```

注意：

- `<ABSOLUTE_PATH_TO_AI_TEST_LAB>` 必须替换成用户本地 `ai-test-lab` 仓库绝对路径。
- 不要写死用户路径。
- 不要读取 `.env`、`.git/`、`.assistant/` 等敏感内容。
- 第一阶段只验证 read 能力，不开放 write 能力。

## Codex 执行要求

请新增或更新：

- `docs/local-environment-prerequisites.md`
- `docs/filesystem-mcp-quickstart.md`
- `configs/mcp/filesystem-server.example.json`
- `docs/current-status.md`
- `docs/next-steps.md`

## docs/local-environment-prerequisites.md 必须包含

```text
必装工具：
可选工具：
版本检查命令：
Windows 安装建议：
失败时怎么处理：
Codex 可自动修复的范围：
需要用户手动处理的范围：
```

## configs/mcp/filesystem-server.example.json 示例

必须包含：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "<ABSOLUTE_PATH_TO_AI_TEST_LAB>"
      ]
    }
  }
}
```

## 禁止事项

- 不要继续复杂选型。
- 不要扩展本地 `LocalFilesystemReadAdapter`。
- 不要实现多文件读取、目录读取、glob 或自动上下文收集。
- 不要开放 filesystem_write。
- 不要开放 shell。
- 不要写死用户本地路径。
- 不要写 token、secret、password。
- 不要编造本地命令执行结果。

## 验收命令

```bash
pytest
```

本任务只落文档和配置模板，不要求 Codex 在远程环境实际启动 MCP server。用户本地验证命令写入文档即可。

## 完成标准

- 用户能清楚知道要装 Node.js / npm / npx / Python / Git。
- 文档说明 nvm-windows 是可选，不是必装。
- filesystem MCP 最小启动命令明确。
- MCP 配置模板落仓。
- 没有新增自研能力。
- 没有启用高风险工具。
