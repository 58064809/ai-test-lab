# Filesystem 模块说明

## 当前状态

当前模块已实现 **filesystem_read 本地只读 adapter + 路径安全策略模型**。

## 已实现

- 路径白名单设计
- 敏感文件黑名单设计
- 路径穿越拦截
- 结构化策略判断结果
- `LocalFilesystemReadAdapter`
- 单文件文本读取结果模型
- 单文件大小上限控制
- 二进制文件拦截

## 当前限制

- 当前只允许显式读取单个仓库相对路径
- 当前不读取仓库外文件
- 当前不读取 `.env`、`.git/`、`.assistant/`、密钥、token、密码类文件
- 当前不接入 MCP Server
- 当前不调用 MCP SDK
- 当前不实现 filesystem_write
- 当前不自动根据自然语言猜测多个文件
- 当前 adapter 只是本地替代层，不代表 MCP 已接入

## 明确不做

- 不把策略模型包装成真实文件读取器
- 不绕过白名单和敏感模式检查
- 不把本地 adapter 包装成 MCP 已接入
