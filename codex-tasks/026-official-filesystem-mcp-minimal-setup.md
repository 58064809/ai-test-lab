# Codex Task 026：直接落地官方 / 主流 filesystem MCP Server 最小配置

## 背景

前面 filesystem MCP 选型已经过度拉长。现在不再继续写复杂选型文档。

用户已拍板：优先使用官方 / 主流生态中的 filesystem MCP server。

本任务目标是直接落地最小可用配置与验证步骤，优先采用：

```text
@modelcontextprotocol/server-filesystem
```

如果当前环境无法确认或安装该包，不要编造结果，直接写清阻塞原因和用户需要执行的命令。

## 最高原则

1. 不再新增选型清单。
2. 不再扩展 `LocalFilesystemReadAdapter`。
3. 不自研 filesystem server。
4. 优先使用官方 / 主流生态 filesystem MCP server。
5. 第一阶段只做只读仓库目录能力验证。
6. 不开放 filesystem_write。
7. 不开放 shell。
8. 不访问仓库外目录。
9. 不读取 `.env`、`.git/`、`.assistant/`、token、secret、password 文件。
10. 不能确认的事实必须写“待用户本地验证”，不要编。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/012-industrial-grade-selection-policy.md`
- `codex-tasks/017-mcp-selection-and-security-boundary.md`
- `docs/mcp-security-policy.md`
- `docs/filesystem-mcp-selection.md`
- `docs/current-status.md`
- `configs/tools.yaml`

## 任务一：新增最小配置文档

新增：

```text
docs/filesystem-mcp-quickstart.md
```

文档只写最小落地，不要再写长篇选型。

必须包含：

```text
采用方案：@modelcontextprotocol/server-filesystem
目标：只允许读取 ai-test-lab 仓库目录
不做：写文件、shell、网络、业务操作
Windows 前置条件：Node.js / npx
最小配置示例：
本地验证命令：
安全边界：
失败处理：
下一步：
```

## 任务二：新增 MCP 配置示例

新增：

```text
configs/mcp/filesystem-server.example.json
```

示例内容必须是配置模板，不包含用户真实绝对路径。

例如：

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

注意：

- 这里的 `<ABSOLUTE_PATH_TO_AI_TEST_LAB>` 是占位符。
- 不要写死用户本机路径。
- 不要写 token。
- 不要写 `.env`。

## 任务三：更新工具状态，但不要假装已接入 runtime

更新：

- `configs/tools.yaml`
- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/tool_registry/README.md`

要求：

- `filesystem_mcp_read` 可以保持 `planned`，不要改成 `enabled`，因为当前 runtime 还没有 MCP client。
- 文档明确：已经确定最小 MCP Server 方案与配置模板，但尚未接入当前 Python runtime。
- `filesystem_read` 仍然是 `local_python` fallback。
- `filesystem_write` 仍然是 `disabled`。
- `shell` 仍然是 `disabled`。

## 任务四：新增配置一致性测试

新增或更新：

```text
tests/test_filesystem_mcp_quickstart.py
```

测试要求：

1. `docs/filesystem-mcp-quickstart.md` 存在。
2. `configs/mcp/filesystem-server.example.json` 存在。
3. 配置示例包含 `@modelcontextprotocol/server-filesystem`。
4. 配置示例包含 `<ABSOLUTE_PATH_TO_AI_TEST_LAB>` 占位符。
5. 配置示例不得包含真实 Windows 盘符路径。
6. 配置示例不得包含 token、secret、password。
7. `filesystem_mcp_read` 仍不是 `enabled`。
8. `filesystem_write` 仍是 `disabled`。
9. `shell` 仍是 `disabled`。

## 禁止事项

- 不要继续写复杂选型表。
- 不要实现 MCP client。
- 不要调用 MCP SDK。
- 不要运行 MCP Server。
- 不要执行 shell 命令。
- 不要改 runtime CLI 行为。
- 不要扩展 `LocalFilesystemReadAdapter`。
- 不要实现多文件读取、目录读取、glob、自动上下文收集。
- 不要把 `filesystem_mcp_read` 改成 enabled。
- 不要开放 `filesystem_write`。

## 验收命令

```bash
pytest
```

用户本地验证命令写入文档即可，不在测试里执行。

## 完成标准

- 官方 / 主流 filesystem MCP server 最小方案已落文档。
- MCP 配置模板已落仓。
- 没有继续搞复杂选型。
- 没有新增自研能力。
- 没有启用真实 MCP runtime。
- 所有测试通过。
