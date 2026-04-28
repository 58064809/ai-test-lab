# Codex Task 028：filesystem MCP 接入 runtime，只开放显式只读读取

## 背景

027 已完成本地环境依赖和 filesystem MCP quickstart。用户本地已经验证：

```powershell
npx -y @modelcontextprotocol/server-filesystem .
```

输出：

```text
Secure MCP Filesystem Server running on stdio
```

说明 Node.js / npm / npx 和 `@modelcontextprotocol/server-filesystem` 已经能跑。

现在不要继续写选型文档，直接做最小 runtime 接入。

## 本任务目标

把官方 / 主流 filesystem MCP server 接入当前 Python runtime，新增一个显式 MCP 只读入口。

第一阶段只支持：

```powershell
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --mcp-read-file README.md
```

要求：

- 只读
- 显式单文件
- 仍经过 `FilesystemReadPolicy`
- 只允许仓库根目录内低风险文件
- 不开放写文件
- 不开放 shell
- 不自动猜测文件
- 不支持目录读取 / glob / 多文件读取

## 最高原则

1. 不再继续复杂选型。
2. 不扩展 `LocalFilesystemReadAdapter`。
3. 使用官方 / 主流 MCP server：`@modelcontextprotocol/server-filesystem`。
4. 使用成熟 MCP SDK / 协议接入，不自研 MCP 协议。
5. 只开放 `filesystem_read`。
6. 不开放 `filesystem_write`。
7. 不执行 shell 任意命令。
8. 不访问外部网络，除了 `npx` 首次拉取官方包这类用户本地明确触发的 MCP server 启动需求。
9. 不读取 `.env`、`.git/`、`.assistant/`、token、secret、password 类文件。
10. 不把未验证能力写成已完成。
11. Markdown 文档默认中文。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/012-industrial-grade-selection-policy.md`
- `codex-tasks/026-official-filesystem-mcp-minimal-setup.md`
- `codex-tasks/027-local-environment-prerequisites-and-mcp-bootstrap.md`
- `docs/local-environment-prerequisites.md`
- `docs/filesystem-mcp-quickstart.md`
- `configs/mcp/filesystem-server.example.json`
- `src/ai_test_assistant/filesystem/policy.py`
- `src/ai_test_assistant/filesystem/adapter.py`
- `src/ai_test_assistant/runtime/cli.py`
- `src/ai_test_assistant/runtime/output.py`
- `configs/tools.yaml`

## 任务一：先修复 027 文档中的本地绝对路径链接

当前 `docs/filesystem-mcp-quickstart.md` 中存在类似：

```text
/D:/TestHome/ai-test-lab/docs/local-environment-prerequisites.md
/D:/TestHome/ai-test-lab/configs/mcp/filesystem-server.example.json
```

这是不应该落入仓库文档的本地绝对路径。

请改成仓库相对链接：

```markdown
[local-environment-prerequisites.md](local-environment-prerequisites.md)
[filesystem-server.example.json](../configs/mcp/filesystem-server.example.json)
```

并补测试，禁止文档中出现 `D:/`、`D:\` 这类本地路径。

## 任务二：引入官方 MCP Python SDK / 成熟客户端依赖

请优先使用官方 / 主流 Python MCP SDK，不要自研 MCP 协议。

允许更新：

- `pyproject.toml`
- 锁文件，如项目已有

要求：

- 如果依赖名是 `mcp`，请写清楚用途。
- 如果当前环境安装失败，Codex 应自行修复依赖声明或给出阻塞原因。
- 不要手写 JSON-RPC stdio 协议。

## 任务三：新增 filesystem MCP client adapter

新增：

```text
src/ai_test_assistant/filesystem/mcp_client.py
```

建议实现：

```python
class FilesystemMcpReadClient:
    def __init__(self, repo_root: Path, policy: FilesystemReadPolicy | None = None): ...
    async def read_text(self, repo_relative_path: str) -> FilesystemReadResult: ...
```

要求：

1. 读取前必须先调用 `FilesystemReadPolicy.evaluate()`。
2. policy 拒绝时，不启动 MCP server、不读取文件。
3. 只启动 `@modelcontextprotocol/server-filesystem`，根目录限制为 `repo_root`。
4. 只调用读取文件相关工具。
5. 不调用写文件、删除文件、创建目录等工具。
6. 如果 MCP server 暴露的工具名与预期不同，Codex 应通过 SDK list_tools 探测并适配，但只能选择只读工具。
7. 如果无法确认只读工具，返回结构化拒绝结果，不要猜。
8. 复用现有 `FilesystemReadResult`，避免重复模型。
9. 保持 Windows 可运行。

## 任务四：runtime CLI 新增显式 MCP 读取参数

更新：

```text
src/ai_test_assistant/runtime/cli.py
src/ai_test_assistant/runtime/output.py
```

新增参数：

```powershell
--mcp-read-file README.md
```

要求：

- `--mcp-read-file` 只支持一个文件。
- 不允许和未来多文件读取混用；当前没有多文件读取。
- `--mcp-read-file` 与现有 `--read-file` 并存：
  - `--read-file` 使用本地 fallback adapter
  - `--mcp-read-file` 使用 filesystem MCP server
- 输出必须标明来源：`local_adapter` 或 `filesystem_mcp`
- 默认仍只展示预览。
- `--show-file-content` 才展示完整允许内容。
- 读取结果进入 orchestrator dry-run context。
- memory 仍只写文件元信息，不写 content。

## 任务五：工具状态更新

更新：

```text
configs/tools.yaml
```

要求：

- `filesystem_mcp_read` 可以改成 `enabled`，但必须是 `read_only`。
- `filesystem_write` 必须保持 `disabled`。
- `shell` 必须保持 `disabled`。
- GitHub / Playwright / database / redis / pytest 等不得因为本任务被启用。
- 文档必须说明：只启用 MCP read，不启用 write。

## 任务六：测试要求

新增或更新：

```text
tests/test_filesystem_mcp_runtime_read.py
tests/test_runtime_cli.py
tests/test_filesystem_mcp_quickstart.py
```

至少覆盖：

1. policy 拒绝 `.env` 时，不启动 MCP server。
2. policy 拒绝 `.git/config` 时，不启动 MCP server。
3. `--mcp-read-file README.md` 会进入 MCP 读取路径。
4. `--mcp-read-file .env` 被拒绝。
5. `--mcp-read-file` 输出来源为 `filesystem_mcp`。
6. 默认只展示预览。
7. `--show-file-content` 才展示完整内容。
8. `--write-memory` 时 memory 只保存元信息，不保存 content。
9. `filesystem_mcp_read` 为 enabled + read_only。
10. `filesystem_write` 仍 disabled。
11. `shell` 仍 disabled。
12. quickstart 文档不含本地绝对路径。

如果测试中不方便真的启动 MCP server，可以对 `FilesystemMcpReadClient` 做 mock，但必须至少保留一个可手动运行的本地验证命令写入文档。

## 任务七：文档更新

更新：

- `docs/filesystem-mcp-quickstart.md`
- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/filesystem/README.md`
- `src/ai_test_assistant/runtime/README.md`
- `src/ai_test_assistant/tool_registry/README.md`

必须明确：

- 已接入 `filesystem_mcp_read` runtime 入口。
- 只支持显式单文件只读。
- 仍保留 `LocalFilesystemReadAdapter` 作为 fallback。
- `filesystem_write` 未开放。
- shell 未开放。
- 不支持目录读取、glob、多文件、自动上下文收集。

## 禁止事项

- 不要实现 filesystem_write。
- 不要执行 shell 任意命令。
- 不要开放命令执行工具。
- 不要访问仓库外路径。
- 不要读 `.env`、`.git/`、`.assistant/`、密钥、token、password 类文件。
- 不要自动根据自然语言猜文件。
- 不要实现多文件读取。
- 不要实现目录读取。
- 不要实现 glob。
- 不要把完整文件内容写入 memory。
- 不要自研 MCP 协议。

## 验收命令

自动测试：

```bash
pytest
```

本地手动验证：

```powershell
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --mcp-read-file README.md
python scripts/run_assistant.py "请读取环境配置" --dry-run --mcp-read-file .env
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --mcp-read-file README.md --show-file-content
```

## 完成标准

- runtime 已有 `--mcp-read-file` 最小入口。
- filesystem MCP read 使用成熟 MCP SDK / 协议接入，不自研协议。
- 读取前经过 `FilesystemReadPolicy`。
- `filesystem_mcp_read` 为 enabled + read_only。
- `filesystem_write`、`shell` 仍 disabled。
- 所有测试通过。
- 手动验证命令写入文档。
