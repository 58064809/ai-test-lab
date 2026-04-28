# filesystem MCP 选型

## 候选方案

1. 官方或主流 MCP filesystem server
2. 社区高质量 filesystem MCP server
3. 现有编辑器 / Agent 生态中的 filesystem 工具能力
4. 继续使用本地 `LocalFilesystemReadAdapter` 作为 fallback

## 信息来源

- `docs/mcp-selection.md`
- `docs/mcp-security-policy.md`
- `docs/filesystem-read-design.md`
- `docs/tools/mcp.md`
- `docs/tools/sources.md`
- 当前仓库内 `configs/tools.yaml`
- GitHub 仓库 star、release、维护状态：当前未联网确认，统一标记为“待人工确认”
- 当前确认时间：2026-04-28

## 选择结果

- 正式 filesystem 能力优先选择成熟 filesystem MCP / 等价成熟工具
- 第一阶段目标能力只限 `filesystem_read`
- 当前 `LocalFilesystemReadAdapter` 只保留为 bootstrap / fallback
- 当前不继续扩展本地 adapter 为多文件、目录、glob、自动上下文或文件检索能力

## 选择理由

- 项目最高原则是不造轮子，正式能力应优先复用成熟协议和成熟工具
- filesystem 属于通用基础能力，长期自研会逐步演化为文件上下文系统，不符合当前路线
- 现有本地 adapter 已足以支撑 bootstrap / fallback，后续应把投入转向成熟工具接入验证

## 未选择方案及原因

- 继续扩展 `LocalFilesystemReadAdapter`
  - 原因：会持续走向自研文件能力，不符合 022 的收口结论
- 直接推进 `021-explicit-multi-file-read-context.md`
  - 原因：该任务已暂停，不应继续执行
- 先接 `filesystem_write`
  - 原因：风险高，不适合作为首批能力

## Windows 本地运行支持

- 官方或主流 filesystem MCP server 的 Windows 支持：待人工确认
- 社区 filesystem MCP server 的 Windows 支持：待人工确认
- 现有编辑器 / Agent 生态 filesystem 工具的 Windows 支持：待人工确认
- 本地 `LocalFilesystemReadAdapter`：当前已可运行

## 只读模式支持

- 成熟 filesystem MCP 是否支持显式只读模式：待人工确认
- 如果不支持只读模式，则不应作为第一阶段正式方案
- 第一阶段成功标准必须包含“只开放 `filesystem_read`，不开放 `filesystem_write`”

## 仓库根目录限制能力

- 成熟 filesystem MCP 是否能限制到仓库根目录：待人工确认
- 如果不能限制仓库根目录，则不能作为第一阶段正式方案
- 即使未来接入成熟工具，也必须与当前 `FilesystemReadPolicy` 的白名单 / 黑名单边界协同

## 写能力禁用方式

- 第一阶段不接 `filesystem_write`
- 即使未来引入成熟 filesystem MCP，也必须先验证写能力是否能显式关闭
- 当前 `configs/tools.yaml` 中：
  - `filesystem_mcp_read` 当前已接入为显式单文件只读入口
  - `filesystem_write` 必须保持 `disabled`

## 与 FilesystemReadPolicy 的协同方式

- 当前 `FilesystemReadPolicy` 继续作为本地 fallback 的路径安全边界
- 未来最小接入时，应优先验证成熟 filesystem MCP 是否能：
  - 只读
  - 限仓库根目录
  - 拒绝敏感路径
- 如果成熟工具边界不足，仍需由本地策略层补足

## 最小接入验证步骤

1. 先人工确认候选 filesystem MCP 的官方来源、Windows 支持、只读模式和根目录限制能力
2. 在隔离环境中验证能否只读取仓库根目录内低风险文件
3. 验证 `.env`、`.git/config`、`.assistant/memory.sqlite3` 被拒绝
4. 验证 `filesystem_write` 未启用
5. 验证 runtime CLI 不会自动触发 MCP 读取

## 风险与限制

- 当前未联网，无法确认具体 GitHub star、release 时间和维护活跃度
- 如果成熟 filesystem MCP 无法限制根目录或只读模式，第一阶段就不应接入
- 即使未来接入成熟工具，也不能绕过当前安全边界

## 待人工确认项

- 官方或主流 filesystem MCP 的仓库地址、star、release、维护状态
- 社区 filesystem MCP 的质量与维护情况
- Windows 本地运行所需依赖
- 只读模式是否可强制开启
- 仓库根目录限制是否可配置

## 后续替换策略

- 正式 filesystem 能力优先替换为成熟 filesystem MCP / 等价成熟工具
- `LocalFilesystemReadAdapter` 保留为 bootstrap / fallback
- 替换时不改变当前 runtime 的安全边界：
  - 不自动猜测文件
  - 不批量读取
  - 不开放写能力
