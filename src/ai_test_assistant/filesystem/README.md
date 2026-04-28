# Filesystem 模块说明

## 当前状态

当前模块已实现 **filesystem_read 本地只读 adapter + filesystem MCP 只读 client + 路径安全策略模型**。

当前定位必须明确：

- `LocalFilesystemReadAdapter` 只是 bootstrap / fallback
- `FilesystemMcpReadClient` 是当前正式的 runtime MCP 只读接入点
- `codex-tasks/021-explicit-multi-file-read-context.md` 已暂停，不继续执行
- `LocalFilesystemReadAdapter` 继续保留为 fallback，不是唯一实现

## 已实现

- 路径白名单设计
- 敏感文件黑名单设计
- 路径穿越拦截
- 结构化策略判断结果
- `LocalFilesystemReadAdapter`
- `FilesystemMcpReadClient`
- 单文件文本读取结果模型
- 单文件大小上限控制
- 二进制文件拦截
- 默认只用于上下文和预览，不要求完整输出
- MCP 读取前先做 `FilesystemReadPolicy` 判断
- policy 拒绝敏感路径时不启动 MCP server

## 当前限制

- 当前只允许显式读取单个仓库相对路径
- 当前不读取仓库外文件
- 当前不读取 `.env`、`.git/`、`.assistant/`、密钥、token、密码类文件
- 当前 MCP server 固定为 `@modelcontextprotocol/server-filesystem`
- 当前 Python client 固定为官方 `mcp` SDK
- 当前不实现 filesystem_write
- 当前不开放 shell
- 当前不自动根据自然语言猜测多个文件
- 当前 `LocalFilesystemReadAdapter` 只是本地替代层，不代表所有读取都走本地
- 当前文件完整内容默认不输出，只有显式参数才展示
- 当前不继续扩展为多文件读取、目录读取、自动上下文收集或文件检索系统

## 后续路线

- 当前正式 filesystem 只读能力优先走成熟 filesystem MCP
- 当前本地 adapter 只保留为 bootstrap / fallback
- 如果未来接入成熟工具，仍应复用现有 `FilesystemReadPolicy` 边界
- 当前最小接入验证路线见：
  - `docs/filesystem-mcp-selection.md`
  - `docs/filesystem-mcp-minimal-integration-plan.md`

## 明确不做

- 不把策略模型包装成真实文件读取器
- 不绕过白名单和敏感模式检查
- 不把 fallback adapter 包装成唯一正式能力
- 不继续把本地 adapter 扩展成多文件上下文系统
