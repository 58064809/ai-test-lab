# filesystem MCP 人工确认清单

## 确认目标

- 在不接入 MCP Server、不调用 MCP SDK、不改 runtime CLI 的前提下，把 filesystem MCP 候选方案整理成可人工核验的清单。
- 在真实联网调研前，不编造 GitHub star、release、维护状态、许可证、Windows 支持或只读能力。
- 在人工确认完成前，不把任何 filesystem MCP 工具改成 `enabled`。
- 当前用户已明确选择：优先确认“官方或主流生态中的 filesystem MCP server”。
- 本轮事实收敛见：`docs/filesystem-mcp-official-mainstream-confirmation.md`

## 候选方案列表

- 官方或主流生态中的 filesystem MCP server：待人工确认
- 社区维护、文档完整、Windows 兼容的 filesystem MCP server：待人工确认
- 编辑器或 Agent 生态中可替代 filesystem MCP 的成熟只读 filesystem 工具：待人工确认

## 候选方案对比表

| 候选名称 | 仓库地址 | 是否官方 / 主流 | GitHub star | 最近 release / commit | 维护活跃度 | 许可证 | Windows 支持 | 运行依赖 | 是否支持只读模式 | 是否支持限制根目录 | 是否可以禁用写能力 | 是否支持敏感路径过滤 | 是否适合个人本地 AI 测试助手 | 证据链接 | 确认状态 | 结论 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 官方或主流生态中的 filesystem MCP server | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 未确认 | 待人工确认 |
| 社区维护、文档完整、Windows 兼容的 filesystem MCP server | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 未确认 | 待人工确认 |
| 编辑器 / Agent 生态中的成熟只读 filesystem 工具 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 待人工确认 | 未确认 | 待人工确认 |

## 必须确认的问题

- [ ] 该工具是否为官方或主流社区维护？
- [ ] GitHub star 是否达到可接受水平，且维护记录不是长期停滞？
- [ ] 是否支持 Windows 本地运行？
- [ ] 是否需要额外运行时依赖，例如 `Node.js`、`npx`、`uv`、`Python`？
- [ ] 是否支持显式只读模式？
- [ ] 是否能限制访问到指定仓库根目录？
- [ ] 是否能禁用写文件能力？
- [ ] 是否能拒绝 `.env`、`.git/`、`.assistant/`、`token`、`secret`、`password` 等敏感路径？
- [ ] 是否能与当前 `FilesystemReadPolicy` 协同，而不是绕过安全边界？
- [ ] 是否可以只开放 `filesystem_read`，不开放 `filesystem_write`？
- [ ] 是否有可审计的读取日志或等价证据？
- [ ] 是否适合个人本地执行型 AI 测试助手，而不是依赖复杂平台？

## 禁止接入条件

- 不支持 Windows 本地运行
- 无法限制仓库根目录
- 无法强制只读
- 无法禁用写文件能力
- 默认开放写能力
- 需要过重的常驻服务依赖
- 文档不足，无法确认安全边界
- 长期无人维护
- 许可证状态不清晰

## 推荐结论模板

```text
最终推荐方案：
推荐级别：推荐 / 暂缓 / 不推荐
推荐理由：
不可接受风险：
第一阶段允许能力：filesystem_read only
第一阶段禁止能力：filesystem_write / shell / external network write
需要保留的本地安全策略：FilesystemReadPolicy
是否可以进入最小接入任务：是 / 否
```

## 证据记录模板

```text
候选名称：
确认时间：
仓库地址：
官方文档地址：
GitHub 主页：
Windows 支持证据：
只读模式证据：
根目录限制证据：
禁用写能力证据：
敏感路径过滤证据：
许可证证据：
运行依赖证据：
人工结论：
备注：
```

## 下一步决策

1. 先人工补齐每个候选项的真实证据。
2. 只要有任一关键安全项无法确认，就不进入 filesystem MCP 最小接入。
3. 只有在候选方案明确满足只读、限根目录、禁写、Windows 可用后，才继续执行 `filesystem MCP` 最小接入验证。
4. 在正式 MCP 方案落地前，当前 `LocalFilesystemReadAdapter` 仍只作为 bootstrap / fallback。
