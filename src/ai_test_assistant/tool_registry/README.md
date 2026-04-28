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

本阶段**未实现**：

- MCP 协议
- MCP Server 接入
- 本地命令执行器
- 外部网络访问器
- 真实工具执行

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
- 已在 `configs/tools.yaml` 中补充后续 planned MCP 工具规划：
  - `filesystem_read`
  - `filesystem_write`
  - `github_read`
  - `github_write`
  - `playwright_browser`

## 当前限制

- 当前只是注册与权限底座，不是完整工具执行框架。
- 当前与 orchestrator 的联动只做风险评估和授权建议，不执行工具。
- 当前不自研 MCP 协议。
- 当前不真实接入 MCP Server。
- 当前不执行本地命令。
- 当前不访问外部网络。
- 当前不处理复杂工具参数 schema。

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
- 不把任何 MCP / 网络 / 命令 / 写文件类工具改成默认 `enabled`
