# 官方 / 主流生态 filesystem MCP 候选确认

## 确认目标

- 只收敛到“官方或主流生态中的 filesystem MCP server”。
- 只确认事实，不写接入代码，不推进 MCP client、MCP SDK、runtime CLI 或真实执行。
- 只有当 Windows、本地只读、根目录限制、禁写边界都足够清晰时，才允许后续进入最小接入验证。

## 优先级原则

1. 优先官方组织维护的 filesystem MCP server。
2. 其次确认主流 AI IDE / Agent 生态是否直接内置或明确推荐同一官方 server。
3. 只有当官方 / 主流生态路线不满足安全边界时，才降级评估社区仓库。
4. 不继续扩展 `LocalFilesystemReadAdapter`；它仍然只是 bootstrap / fallback。

## 官方候选

- `modelcontextprotocol/servers` 仓库中的 filesystem server
- npm 包：`@modelcontextprotocol/server-filesystem`

已确认事实：
- `modelcontextprotocol` 是 GitHub Verified Organization，绑定域名 `modelcontextprotocol.io`。
- 其 `servers` 仓库明确包含 filesystem server。
- 官方 README 明确给出 `@modelcontextprotocol/server-filesystem` 的 NPX 启动方式。
- 官方 README 明确给出 Windows 下使用 `cmd /c npx` 的配置示例。
- 官方 README 明确给出目录访问边界：通过命令行参数或 MCP Roots 限定 allowed directories。

## 主流生态候选

- Anthropic Agent SDK / Claude Code MCP 文档中，直接以 `@modelcontextprotocol/server-filesystem` 作为 filesystem server 示例。
- 官方 filesystem README 中，直接提供 VS Code / VS Code Insiders 的安装按钮和手动配置示例。
- Microsoft Learn 的 MCP 支持文档中，也以 `@modelcontextprotocol/server-filesystem` 作为本地 MCP server 示例。

已确认事实：
- 已确认“主流生态推荐或示例接入”存在。
- 尚未确认“主流 AI IDE 原生内置该 filesystem server”。

## 社区候选降级条件

只有在以下任一情况成立时，才进入社区仓库评估：
- 官方候选不存在
- 官方候选无法在 Windows 本地运行
- 官方候选无法限制仓库根目录
- 官方候选无法满足第一阶段 `filesystem_read only` 的安全要求
- 主流生态没有继续采用官方候选，而是普遍转向其他成熟实现

## 已排除项

- 不把 `LocalFilesystemReadAdapter` 继续扩展成多文件读取、目录读取、glob 或自动上下文收集系统。
- 不把任何 filesystem MCP 工具改成 `enabled`。
- 不把 `filesystem_write` 提前开放。
- 不把“生态里有示例配置”误写成“本仓库已经完成 filesystem MCP 接入”。

## 事实确认表

| 候选名称 | 来源类型：官方 / 主流生态 / 社区 | 仓库地址或包地址 | 证据来源 | 是否确认存在 | star | 最近 release / commit | 维护状态 | 许可证 | Windows 支持 | 安装方式 | 是否支持只读模式 | 是否支持限制仓库根目录 | 是否可以禁用写能力 | 是否支持敏感路径过滤 | 是否适合第一阶段 filesystem_read | 确认状态 | 结论 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `modelcontextprotocol/servers` 中的 filesystem server | 官方 | `https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem` | 官方 GitHub 组织页、官方 filesystem README | 是 | 官方 README 页面可见仓库 star；是否需单独记录数值待人工确认 | 官方 README 页面可见历史入口；具体 release 节点待人工确认 | 官方组织维护 | MIT | 是，官方 README 明确提供 Windows `cmd /c npx` 示例 | `npx` 或 Docker | 部分确认：Docker `ro` mount 可只读；NPX 模式下严格只读开关待人工确认 | 是，支持命令行 allowed directories 与 MCP Roots | 待人工确认：未看到通用 server-side `disable write` 开关；客户端 allowlist 可限制调用 | 待人工确认：官方 README 未声明内置 `.env` / `.git` 黑名单 | 有潜力，但需先补齐禁写与敏感路径边界确认 | 部分确认 | 当前第一优先候选 |
| `@modelcontextprotocol/server-filesystem` | 官方 | `https://www.npmjs.com/package/@modelcontextprotocol/server-filesystem` | npm 包页面、官方 README、Anthropic/Microsoft 示例 | 是 | 待人工确认 | 待人工确认 | 待人工确认 | MIT | 是，Windows 示例已在官方 README 中确认 | `npx -y @modelcontextprotocol/server-filesystem ...` | 部分确认：工具注解明确区分 read-only tools 与 write-capable tools；但 server 默认仍暴露写工具 | 是，包参数可传 allowed directories；Roots 也可覆盖目录边界 | 待人工确认 | 待人工确认 | 有潜力，但仍需安全边界补证 | 部分确认 | 与官方仓库同属同一路线，优先保留 |
| Anthropic Agent SDK / Claude Code 示例中的 official filesystem server | 主流生态 | `https://platform.claude.com/docs/en/agent-sdk/mcp` | Anthropic 官方文档 | 是 | 不适用 | 不适用 | 官方文档活跃度待人工确认 | 待人工确认 | 文档示例未单独声明，结合官方 README 可确认 Windows 示例存在 | `.mcp.json` 或 `mcpServers` 中直接配置 `npx @modelcontextprotocol/server-filesystem` | 客户端层面可通过 `allowedTools` 做工具授权限制 | 通过参数传根目录；是否结合 Roots 仍取决于 server | 客户端可限制可调用工具，但是否等同“禁用写能力”待人工确认 | 待人工确认 | 适合作为主流 Agent 生态采用证据 | 已确认存在 | 证明官方包已被主流 Agent 生态采用 |
| VS Code 生态中的 official filesystem server | 主流生态 | 官方 filesystem README 中的 VS Code 配置段 | 官方 filesystem README | 是 | 不适用 | 不适用 | 待人工确认 | 待人工确认 | 是，README 明确提供 Windows 配置示例 | VS Code `mcp.json` + `npx` 或 Docker | 部分确认：Docker `ro` mount 可只读 | 是，`${workspaceFolder}` 与 Roots/args 可限制 | 待人工确认 | 待人工确认 | 适合作为主流 IDE 生态采用证据 | 部分确认 | 已确认 VS Code 配置入口存在，但是否“内置”待人工确认 |

## 推荐结论

- 推荐方案：继续以官方 `modelcontextprotocol` filesystem server / `@modelcontextprotocol/server-filesystem` 作为唯一优先候选。
- 推荐级别：暂缓
- 推荐理由：
  - 官方组织和官方包都已确认存在。
  - Anthropic Agent SDK 与 VS Code 配置入口都已出现该官方包，说明它至少属于主流生态推荐路径。
  - Windows 本地启动方式、根目录限制能力已能从官方 README 直接确认。
- 不能直接接入的原因：
  - 尚未从官方文档中确认通用的 server-side “禁用写能力”开关。
  - 严格只读模式目前只明确看到了 Docker `ro` mount 路线；NPX / stdio 路线下是否可稳定满足第一阶段 `filesystem_read only`，仍需人工确认。
  - 官方文档未直接声明内置 `.env`、`.git/`、`.assistant/` 级别的敏感路径黑名单。
- 第一阶段允许能力：`filesystem_read` only
- 第一阶段禁止能力：`filesystem_write` / `shell` / 自动多文件读取 / 目录读取 / `glob`
- 需要人工确认的问题：
  - NPX / stdio 模式下，是否存在明确的 no-write 或 read-only 开关
  - 官方路线下，是否需要额外依赖 Docker 才能拿到真正只读边界
  - 敏感路径过滤应完全依赖 server 还是仍需本地策略层补足
- 是否允许进入 026 最小接入验证任务：待确认

## 未确认风险

- star、最近 release / commit、维护状态的精确数值仍应在联网人工核验后补录。
- “主流生态内置”与“主流生态推荐配置”不是一回事；当前确认到的是推荐 / 示例，不是内置。
- 如果官方路线最终不能满足第一阶段只读和禁写边界，就必须暂停接入，而不是直接切到社区仓库。

## 下一步是否允许进入最小接入验证

- 当前结论：暂不直接进入。
- 放行条件：
  - 明确 Windows 本地可跑
  - 明确可以只读
  - 明确可以限制仓库根目录
  - 明确可以禁用写能力，或至少能在客户端和部署层组合出可审计的禁写边界
  - 明确不会绕过当前 `FilesystemReadPolicy` 的安全要求

## 参考来源

- Model Context Protocol GitHub 组织：<https://github.com/modelcontextprotocol>
- 官方 filesystem README：<https://github.com/modelcontextprotocol/servers/blob/main/src/filesystem/README.md>
- npm 包：<https://www.npmjs.com/package/@modelcontextprotocol/server-filesystem>
- Anthropic Agent SDK MCP 文档：<https://platform.claude.com/docs/en/agent-sdk/mcp>
- Microsoft Learn MCP 支持：<https://learn.microsoft.com/en-us/powershell/utility-modules/aishell/how-to/mcp-support?view=ps-modules>
