# Tool Registry 模块说明

## 当前状态

当前模块已实现 **工具注册表与权限模型底座**。

本阶段只完成：

- 工具配置加载
- 工具状态建模
- 风险等级建模
- 权限判定策略

本阶段**未实现**：

- MCP 协议
- MCP Server 接入
- 本地命令执行器
- 外部网络访问器
- runtime CLI

## 已实现

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

## 当前限制

- 当前只是注册与权限底座，不是完整工具执行框架。
- 当前不自研 MCP 协议。
- 当前不真实接入 MCP Server。
- 当前不执行本地命令。
- 当前不访问外部网络。
- 当前不处理复杂工具参数 schema。

## 待接入

- 正式 MCP 工具生态评估与接入
- 真实执行器层
- 与 orchestrator 的调用集成
- runtime CLI

## 明确不做

- 不把 `planned` 工具包装成已可执行
- 不让 `restricted_action` 默认开放
- 不把注册表误写成自研 MCP 协议

