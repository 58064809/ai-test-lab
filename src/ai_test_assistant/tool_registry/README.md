# Tool Registry 模块说明

## 当前状态

当前模块已实现 **工具注册表与权限模型底座**。

本阶段只完成：

- 工具配置加载
- 工具状态建模
- 风险等级建模
- 权限判定策略
- dry-run 阶段与 orchestrator 的最小授权联动
- MCP 接入前置选型与安全边界文档
- filesystem_read 接入前安全策略模型

本阶段**未实现**：

- MCP 协议
- 除 `filesystem_mcp_read` 外的其他 MCP Server 接入
- 本地命令执行器
- 外部网络访问器
- 写文件、shell、浏览器、数据库等真实工具执行

## 已实现

- memory 工具权限已拆分：
  - `memory_read`
  - `memory_write`
- 工具状态区分：
  - `enabled`
  - `disabled`
  - `planned`
  - `unavailable`
- 风险等级区分：
  - `read_only`
  - `write_project_files`
  - `execute_local_command`
  - `external_network`
  - `restricted_action`
- 未启用工具不可执行
- `restricted_action` 默认禁止
- `write_project_files`、`execute_local_command`、`external_network` 需要显式审批上下文
- orchestrator 可读取注册表并在 dry-run 结果里展示工具授权判断
- `memory_read` 是只读能力，可用于读取 memory 辅助上下文
- `memory_write` 用于更新长期记忆，当前默认不开放
- 已新增 MCP 规划文档：
  - `docs/mcp-selection.md`
  - `docs/mcp-security-policy.md`
- 已新增 filesystem_read 设计与策略模型：
  - `docs/filesystem-read-design.md`
  - `src/ai_test_assistant/filesystem/policy.py`
- 已新增 filesystem_read 本地只读 adapter：
  - `src/ai_test_assistant/filesystem/adapter.py`
- 已新增 filesystem MCP 只读 client：
  - `src/ai_test_assistant/filesystem/mcp_client.py`
- 已新增成熟 filesystem MCP 选型与最小接入验证方案：
  - `docs/filesystem-mcp-selection.md`
  - `docs/filesystem-mcp-minimal-integration-plan.md`
- 已新增官方 filesystem MCP quickstart 与最小配置模板：
  - `docs/filesystem-mcp-quickstart.md`
  - `configs/mcp/filesystem-server.example.json`
- 已在 `configs/tools.yaml` 中补充后续 planned MCP 工具规划：
  - `filesystem_mcp_read`
  - `filesystem_write`
  - `github_read`
  - `github_write`
  - `playwright_browser`
- `filesystem_read` 当前已作为本地只读 adapter 启用，但它不是 MCP Server 接入
- `filesystem_mcp_read` 当前已启用为 `enabled + read_only`
- `filesystem_mcp_read` 的正式 runtime 入口是显式 `--mcp-read-file`
- `filesystem_mcp_read` 固定采用官方 `mcp` Python SDK + `@modelcontextprotocol/server-filesystem`
- `filesystem_write` 仍然保持 `disabled`
- `shell` 仍然保持 `disabled`

## 当前限制

- 当前只是注册与权限底座，不是完整工具执行框架。
- 当前与 orchestrator 的联动只做风险评估和授权建议，不执行工具。
- 当前不自研 MCP 协议。
- 当前除 `filesystem_mcp_read` 外，不真实接入其他 MCP Server。
- 当前不执行本地命令。
- 当前不访问外部网络。
- 当前不处理复杂工具参数 schema。
- 当前 filesystem_read 虽然已同时支持本地只读 adapter 与 MCP 只读入口，但仍然只支持显式单文件读取。
- 当前不开放目录读取、glob、多文件读取、自动上下文收集、filesystem_write 或 shell。

## 待接入

- 正式 MCP 工具生态评估与接入
- 真实执行器层
- 与 orchestrator 的正式执行联动
- 更复杂的工具参数 schema

## 明确不做

- 不把 `planned` 工具包装成已可执行
- 不把 `memory_write` 包装成默认可执行
- 不让 `restricted_action` 默认开放
- 不把注册表误写成自研 MCP 协议
- 不把 `filesystem_write`、`shell`、`github_write` 这类高风险工具改成默认 `enabled`
