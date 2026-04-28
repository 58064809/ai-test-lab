# Codex Task 017：MCP 接入前置选型与安全边界

## 任务背景

当前底座已经完成：

- memory 最小持久化底座
- intent router bootstrap / fallback 规则路由
- LangGraph 最小 orchestrator dry-run 骨架
- tool registry 与权限模型
- runtime CLI
- 真实任务样本验证
- orchestrator 与 tool registry 的 dry-run 授权联动
- memory_read / memory_write 权限拆分

下一步不要直接接入 MCP Server，也不要开放真实工具执行。

本任务目标是：在正式接 MCP 之前，先完成 MCP 工具生态选型、权限边界、接入顺序和安全策略设计。

## 最高原则

1. 不自研 MCP 协议。
2. 不直接接入 MCP Server。
3. 不执行本地命令。
4. 不访问外部网络。
5. 不读写真实业务文件。
6. 不开放真实执行分支。
7. 不把 planned 工具包装成 enabled。
8. 不把 dry-run 授权评估包装成真实执行。
9. 正式方案优先选择官方或 GitHub 高 star、维护活跃、社区成熟的 MCP Server / 工具。
10. 不写死任何电商业务规则。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/012-industrial-grade-selection-policy.md`
- `docs/current-status.md`
- `docs/next-steps.md`
- `docs/tools/mcp.md`
- `docs/tools/playwright-mcp.md`
- `docs/tools/sources.md`
- `src/ai_test_assistant/tool_registry/README.md`
- `src/ai_test_assistant/orchestrator/README.md`
- `configs/tools.yaml`

## 任务一：新增 MCP 选型文档

新增：

```text
docs/mcp-selection.md
```

文档必须包含：

```text
候选 MCP Server / 工具：
选择结果：
选择理由：
未选择方案及原因：
当前接入状态：
风险与限制：
权限分层：
推荐接入顺序：
Windows 本地运行注意事项：
后续替换策略：
```

至少评估以下类别：

1. filesystem MCP / 文件系统工具
2. GitHub MCP / GitHub 工具
3. Playwright MCP
4. shell / command execution 类工具
5. database readonly 类工具
6. redis readonly 类工具

要求：

- 必须明确哪些适合第一批接入。
- 必须明确哪些暂不接入。
- 必须明确 shell / command execution 默认不接入或保持 disabled。
- 必须明确 database / redis 第一阶段只允许 readonly。
- 必须明确 Playwright MCP 只做 UI dry-run / 冒烟评估前置，不做账号、支付、下单等高风险动作。

## 任务二：新增 MCP 安全策略文档

新增：

```text
docs/mcp-security-policy.md
```

必须定义工具权限分层：

```text
L0: no_tool，仅推理和计划
L1: read_only，只读本地元数据 / 只读 memory / 只读配置
L2: read_project_files，只读仓库文件
L3: write_project_files，可写仓库文件，必须确认
L4: external_network，可访问外部网络，必须确认
L5: execute_local_command，本地命令执行，默认禁止
L6: restricted_business_action，业务高风险动作，默认禁止
```

必须定义每层：

- 可做什么
- 禁止什么
- 是否需要确认
- 是否允许 dry-run
- 是否允许默认启用
- 适用工具示例

必须明确：

- shell 永远不能默认 enabled。
- filesystem write 不能默认 enabled。
- GitHub write 不能默认 enabled。
- database / redis 第一阶段只允许 readonly。
- Playwright MCP 第一阶段不允许执行真实支付、下单、发券、删数据等动作。
- 所有高风险动作必须 human confirmation。

## 任务三：更新 tool registry 规划，但不启用真实 MCP

允许更新：

- `configs/tools.yaml`
- `src/ai_test_assistant/tool_registry/README.md`
- `docs/current-status.md`
- `docs/next-steps.md`

要求：

1. 不要把任何 MCP 工具改成 enabled。
2. 可以补充工具 notes，说明后续接入方式、风险和前置条件。
3. 可以增加 planned 工具项，例如：
   - filesystem_read
   - filesystem_write
   - github_read
   - github_write
   - playwright_browser
   - database_readonly
   - redis_readonly
4. 如果拆分工具名，必须同步测试。
5. 不要删除现有安全边界。

## 任务四：新增 MCP 选型测试或文档一致性测试

新增或更新测试：

```text
tests/test_mcp_selection_docs.py
```

测试重点不是联网验证，而是检查文档和配置边界：

- `docs/mcp-selection.md` 存在。
- `docs/mcp-security-policy.md` 存在。
- `configs/tools.yaml` 中 shell 不是 enabled。
- write 类工具不是 enabled。
- external_network / execute_local_command / restricted_action 工具默认不可执行。
- database_readonly / redis_readonly 不应是写权限。
- Playwright MCP 仍然不是 enabled。

## 禁止事项

- 不要真实接入 MCP Server。
- 不要调用 MCP SDK。
- 不要运行 Playwright MCP。
- 不要访问 GitHub 网络接口。
- 不要执行 shell 命令。
- 不要读写真实业务文件。
- 不要开放 runtime 真实执行入口。
- 不要实现复杂多 Agent。
- 不要引入向量库。

## 验收命令

```bash
pytest
python scripts/run_assistant.py "请调研 MCP 和 GitHub 工具接入方式" --dry-run
python scripts/run_assistant.py "请设计这个页面的 UI 自动化回归方案" --dry-run
python scripts/run_assistant.py "请修改仓库配置并更新工作流" --dry-run
```

## 完成标准

- MCP 选型文档完成。
- MCP 安全策略文档完成。
- 工具注册表仍保持安全默认值。
- 所有 MCP / 网络 / 命令 / 写文件类工具仍未真实启用。
- 测试覆盖关键安全边界。
- 所有文档真实反映：当前仍未接入 MCP，仍不执行真实工具。