# Filesystem 模块说明

## 当前状态

当前模块已实现 **filesystem_read 本地只读 adapter + 路径安全策略模型**。

当前定位必须明确：

- `LocalFilesystemReadAdapter` 只是 bootstrap / fallback
- 它不是长期正式 filesystem 能力
- `codex-tasks/021-explicit-multi-file-read-context.md` 已暂停，不继续执行
- `codex-tasks/023-filesystem-mcp-selection-and-minimal-integration-plan.md` 只完成选型与验证方案，不是接入实现

## 已实现

- 路径白名单设计
- 敏感文件黑名单设计
- 路径穿越拦截
- 结构化策略判断结果
- `LocalFilesystemReadAdapter`
- 单文件文本读取结果模型
- 单文件大小上限控制
- 二进制文件拦截
- 默认只用于上下文和预览，不要求完整输出

## 当前限制

- 当前只允许显式读取单个仓库相对路径
- 当前不读取仓库外文件
- 当前不读取 `.env`、`.git/`、`.assistant/`、密钥、token、密码类文件
- 当前不接入 MCP Server
- 当前不调用 MCP SDK
- 当前不实现 filesystem_write
- 当前不自动根据自然语言猜测多个文件
- 当前 adapter 只是本地替代层，不代表 MCP 已接入
- 当前文件完整内容默认不输出，只有显式参数才展示
- 当前不继续扩展为多文件读取、目录读取、自动上下文收集或文件检索系统

## 后续路线

- 后续正式 filesystem 能力优先接入成熟 filesystem MCP 或等价成熟工具
- 当前本地 adapter 只保留为 bootstrap / fallback
- 如果未来接入成熟工具，仍应复用现有 `FilesystemReadPolicy` 边界
- 当前最小接入验证路线见：
  - `docs/filesystem-mcp-selection.md`
  - `docs/filesystem-mcp-minimal-integration-plan.md`

## 明确不做

- 不把策略模型包装成真实文件读取器
- 不绕过白名单和敏感模式检查
- 不把本地 adapter 包装成 MCP 已接入
- 不继续把本地 adapter 扩展成多文件上下文系统
