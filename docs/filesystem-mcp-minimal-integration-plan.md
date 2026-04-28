# filesystem MCP 最小接入验证方案

## 目标

- 验证成熟 filesystem MCP / 等价成熟工具是否能在 Windows 本地以只读方式运行
- 验证其是否能限制仓库根目录
- 验证其是否只读取低风险工程文件

## 非目标

- 不实现 MCP 接入代码
- 不运行 MCP Server
- 不调用 MCP SDK
- 不开放 `filesystem_write`
- 不扩展本地 `LocalFilesystemReadAdapter`

## 前置条件

- 候选成熟工具信息已完成人工确认
- 已确认 Windows 运行依赖
- 已确认只读模式和仓库根目录限制能力
- 已准备隔离测试仓库

## 验证环境

- Windows 本地开发环境
- 当前仓库根目录
- 低风险文件样本：
  - `README.md`
  - `docs/current-status.md`
  - `configs/intents.yaml`

## 验证命令

- 当前阶段不写具体运行命令
- 原因：未联网确认成熟工具选型，具体命令待人工确认后补充

## 安全边界

- 只验证 `filesystem_read`
- 不验证 `filesystem_write`
- 必须验证 `.env`、`.git/config`、`.assistant/memory.sqlite3` 被拒绝
- 必须验证 runtime CLI 不会自动读取文件
- 必须验证 shell、网络、写文件仍未开放

## 成功标准

- 候选成熟工具可在 Windows 本地启动：待人工确认
- 只读模式可用：待人工确认
- 可限制仓库根目录：待人工确认
- 允许读取低风险文件：
  - `README.md`
  - `docs/current-status.md`
- 拒绝敏感文件：
  - `.env`
  - `.git/config`
  - `.assistant/memory.sqlite3`
- `filesystem_write` 仍未启用

## 失败回滚

- 不接入成熟工具
- 继续保留当前 `LocalFilesystemReadAdapter` 作为 bootstrap / fallback
- 不改变现有 runtime CLI 行为

## 需要人工确认的问题

- 候选成熟 filesystem MCP 的官方仓库与维护状态
- Windows 下的真实依赖安装方式
- 只读模式是否可强制启用
- 仓库根目录限制是否可靠
- 与当前 `FilesystemReadPolicy` 协同的最小方案
