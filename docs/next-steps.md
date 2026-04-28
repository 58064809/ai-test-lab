# Next Steps

## 028 filesystem MCP runtime 只读接入之后

- 下一步不再继续写复杂选型文档，直接围绕已接入的 `filesystem_mcp_read` 做边界内验证和稳定性补充。
- 用户本地已验证 `npx -y @modelcontextprotocol/server-filesystem .` 可启动；后续重点是 runtime 手动验证，而不是再开选型分支。
- 当前 runtime 已有 `--mcp-read-file` 入口，下一步只验证它在用户本地环境中的依赖和可运行性。
- 继续保留 `LocalFilesystemReadAdapter` fallback，不扩展它。
- 不实现多文件读取、目录读取或 `glob`，不开放 `filesystem_write`，不开放 `shell`。

## 仍需补充验证的点

- 在用户本地 Python 环境确认 `mcp` SDK 已正确安装并可被 runtime 导入。
- 在用户本地实际运行 `--mcp-read-file README.md`、`--mcp-read-file .env` 和 `--show-file-content` 三条命令。
- 继续观察官方 filesystem server 的只读工具名是否稳定；如果上游变更，优先适配只读读取，不新增写能力。

## 建议顺序

1. 继续用更多真实任务样本验证当前 `memory + intent router + orchestrator dry-run + tool registry` 的联动是否稳定。
2. 在不扩大能力边界的前提下，为 orchestrator 增加正式执行前的确认分支，而不是直接开放真实工具执行。
3. `021-explicit-multi-file-read-context.md` 已暂停，不继续扩展本地 filesystem 读取能力。
4. 下一步 filesystem 能力只围绕显式单文件只读入口做稳定性验证，不继续扩展成本地文件管理器。
5. 如需继续演进，先验证 `FilesystemReadPolicy` 与官方 server 工具名探测在用户本地是否稳定，再讨论更细粒度适配。
6. 在确认真实需求前，不接入 `shell`、`github_write`、`filesystem_write` 这类高风险能力。
7. 评估 LangGraph checkpointer 是否值得接入；如果没有明确收益，不提前复杂化。
8. 在确认真实需求前，不引入向量库或复杂多 Agent 机制。

## 待接入项

- 待接入：除 `filesystem_mcp_read` 之外的其他 MCP 真实接入
- 待接入：真实工具执行层
- 待接入：orchestrator 正式执行分支
- 待接入：tool registry 与 orchestrator 的正式执行授权联动
- 待接入：更系统化的真实任务样本库扩展

## 风险提醒

- 当前 `intent router` 仍然只是 bootstrap / fallback 规则路由，不应包装成工业级语义理解系统。
- 当前 `orchestrator` 仍然只是最小 dry-run 骨架，即使已经接入 tool registry 授权联动，也不应包装成完整执行平台。
- 当前除 `filesystem_mcp_read` 之外，其余 MCP 规划文档不代表真实接入，不应把 planned 工具包装成 enabled。
- 当前 filesystem_read 本地 adapter 只是 fallback，不应扩展成通用文件管理器。
- 当前文件读取上下文只支持显式单文件输入，不应扩展成自然语言自动多文件读取。
- 当前不应继续开发多文件读取、目录读取、glob / 通配符读取、自动上下文收集或文件检索。
- 当前虽然已接入成熟 filesystem MCP 的只读读取入口，但不代表任何写能力或 shell 能力已开放。
- 即使继续使用 LangGraph，也不要在 graph 外面再包一层复杂自研状态机。
- 如果后续只需要结构化查询，不应过早引入向量库。
