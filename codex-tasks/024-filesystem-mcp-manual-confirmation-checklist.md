# Codex Task 024：filesystem MCP 候选方案人工确认清单

## 任务背景

023 已完成成熟 filesystem MCP / 等价成熟工具的选型文档和最小接入验证方案。

但 023 中大量关键信息仍标记为“待人工确认”，包括：

- 官方或主流 filesystem MCP 的仓库地址、star、release、维护状态
- 社区 filesystem MCP 的质量与维护情况
- Windows 本地运行所需依赖
- 只读模式是否可强制开启
- 仓库根目录限制是否可配置

本任务目标是把这些“待人工确认项”整理成可执行的确认清单，供用户或后续 Codex 在可联网环境中逐项核验。

本任务只做清单和证据记录模板，不实现 MCP 接入代码。

## 最高原则

1. 不造轮子。
2. 不继续扩展本地 filesystem adapter。
3. 不实现 MCP client。
4. 不调用 MCP SDK。
5. 不运行 MCP Server。
6. 不执行 shell 命令。
7. 不访问外部网络，除非当前 Codex 环境明确允许用于调研；如果不能联网，必须写“待人工确认”，不能编造。
8. 不开放 filesystem_write。
9. 不把未验证能力写成已完成。
10. Markdown 文档默认中文。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/012-industrial-grade-selection-policy.md`
- `codex-tasks/017-mcp-selection-and-security-boundary.md`
- `codex-tasks/022-pause-021-and-return-to-mature-tooling.md`
- `codex-tasks/023-filesystem-mcp-selection-and-minimal-integration-plan.md`
- `docs/filesystem-mcp-selection.md`
- `docs/filesystem-mcp-minimal-integration-plan.md`
- `docs/mcp-selection.md`
- `docs/mcp-security-policy.md`
- `docs/current-status.md`
- `docs/next-steps.md`
- `configs/tools.yaml`

## 任务一：新增人工确认清单文档

新增：

```text
docs/filesystem-mcp-manual-checklist.md
```

文档必须包含以下章节：

```text
确认目标：
候选方案列表：
候选方案对比表：
必须确认的问题：
禁止接入条件：
推荐结论模板：
证据记录模板：
下一步决策：
```

## 任务二：候选方案对比表

请在文档中创建候选方案对比表。

每个候选方案至少包含以下字段：

```text
候选名称
仓库地址
是否官方 / 主流
GitHub star
最近 release / commit
维护活跃度
许可证
Windows 支持
运行依赖
是否支持只读模式
是否支持限制根目录
是否可以禁用写能力
是否支持敏感路径过滤
是否适合个人本地 AI 测试助手
证据链接
确认状态
结论
```

要求：

- 如果无法联网确认，所有事实字段写“待人工确认”。
- 不能编造 star 数、release 时间、维护状态、许可证。
- 如果引用具体仓库，必须写清证据链接或“待人工确认”。

## 任务三：必须确认的问题

请把问题拆成用户可以逐项勾选的 checklist。

至少包含：

- [ ] 该工具是否为官方或主流社区维护？
- [ ] GitHub star 是否足够高，是否有持续维护迹象？
- [ ] 是否支持 Windows 本地运行？
- [ ] 是否需要 Node.js / npx / uv / Python 等额外依赖？
- [ ] 是否支持只读模式？
- [ ] 是否能限制访问到指定仓库根目录？
- [ ] 是否能禁用写文件能力？
- [ ] 是否能拒绝 `.env`、`.git/`、`.assistant/`、token、secret、password 等敏感路径？
- [ ] 是否能与当前 `FilesystemReadPolicy` 协同？
- [ ] 是否能只开放 `filesystem_read`，不开放 `filesystem_write`？
- [ ] 是否有明确日志，便于审计读取了哪些文件？
- [ ] 是否适合个人本地执行型 AI 测试助手？

## 任务四：禁止接入条件

必须明确：只要命中以下任意条件，就不能作为第一阶段正式方案：

- 不支持 Windows 本地运行。
- 无法限制仓库根目录。
- 无法强制只读。
- 无法禁用写文件能力。
- 默认开放写能力。
- 需要过大的常驻服务依赖。
- 文档不完整，无法确认安全边界。
- 长期无人维护。
- 许可证不清晰。

## 任务五：推荐结论模板

请提供一个最终决策模板，例如：

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

## 任务六：更新状态文档

更新：

- `docs/current-status.md`
- `docs/next-steps.md`

要求：

- 明确已新增 filesystem MCP 人工确认清单。
- 明确下一步需要先完成候选工具人工确认，再决定是否进入 MCP 最小接入。
- 不得写成已经确认了具体 MCP 工具。
- 不得写成已经接入 MCP。

## 任务七：新增文档一致性测试

新增或更新：

```text
tests/test_filesystem_mcp_manual_checklist.py
```

测试要求：

1. `docs/filesystem-mcp-manual-checklist.md` 存在。
2. 文档包含候选方案对比表字段。
3. 文档包含必须确认的问题 checklist。
4. 文档包含禁止接入条件。
5. 文档包含推荐结论模板。
6. 文档不得出现“已确认官方 filesystem MCP 可用”“已接入 MCP”这类未验证表述。
7. `configs/tools.yaml` 中 `filesystem_mcp_read` 仍不是 enabled。
8. `filesystem_write` 仍是 disabled。
9. `shell` 仍是 disabled。

## 禁止事项

- 不要实现 MCP client。
- 不要调用 MCP SDK。
- 不要运行 MCP Server。
- 不要执行 shell 命令。
- 不要改 runtime CLI 行为。
- 不要扩展 `LocalFilesystemReadAdapter`。
- 不要实现多文件读取。
- 不要实现目录读取。
- 不要实现 glob / 通配符读取。
- 不要开放 filesystem_write。
- 不要把任何 MCP 工具改成 enabled。
- 不要编造未确认事实。

## 验收命令

```bash
pytest
```

## 完成标准

- 人工确认清单完成。
- 候选方案对比表完成。
- 禁止接入条件明确。
- 推荐结论模板明确。
- 状态文档同步。
- 未实现任何 MCP 接入代码。
- 未启用任何 MCP 工具。
- 所有测试通过。
