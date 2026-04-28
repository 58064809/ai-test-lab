# MCP 接入前置选型

## 候选 MCP Server / 工具

1. filesystem MCP / 文件系统工具
2. GitHub MCP / GitHub 工具
3. Playwright MCP
4. shell / command execution 类工具
5. database readonly 类工具
6. redis readonly 类工具

## 选择结果

- 第一批优先评估：
  - `filesystem_read`
  - `github_read`
  - `database_readonly`
  - `redis_readonly`
- 第二批谨慎评估：
  - `playwright_browser`
- 暂不接入：
  - `shell`
  - `github_write`
  - `filesystem_write`

## 选择理由

- `filesystem_read` 最适合先落地，因为 AI 测试助手大量任务都依赖读取仓库内规则、配置和测试资产。
- `github_read` 适合后续只读查看 issue、PR、提交和工作流状态，但仍属于外部网络能力，不能默认启用。
- `database_readonly` 与 `redis_readonly` 适合后续做测试排障和数据核对，第一阶段应严格限制为只读。
- `playwright_browser` 有明确价值，但浏览器自动化天然带交互风险，应该晚于只读工具接入。
- `shell` 虽然通用性强，但权限过大，默认不接入，保持 `disabled`。

## 未选择方案及原因

- 直接接入通用 shell / command execution：风险过高，容易绕过更细粒度的工具边界。
- 第一阶段直接接入 GitHub write：会引入评论、建 PR、改状态等外部副作用，不符合当前安全边界。
- 第一阶段直接接入 filesystem write：会带来仓库写入风险，不适合作为 MCP 首批能力。
- 第一阶段直接把 Playwright MCP 用于真实业务动作：账号、支付、下单、发券、删数据等动作风险过高。

## 当前接入状态

- 当前仓库**未真实接入**任何 MCP Server。
- 当前 `configs/tools.yaml` 中的 MCP 相关工具都只是 `planned` 或 `disabled` 规划项。
- 当前 orchestrator 只会在 dry-run 中输出风险评估，不会触发任何 MCP 调用。

## 风险与限制

- filesystem 类工具一旦有写权限，就可能改动仓库文件。
- GitHub 类工具天然需要外部网络和 token。
- Playwright MCP 涉及账号、页面交互和潜在副作用。
- shell / command execution 会放大本地环境风险，默认不开放。
- database / redis 即使只读，也需要确认连接环境、账号权限和脱敏要求。

## 权限分层

- `filesystem_read`：对应只读仓库文件能力，适合先评估。
- `filesystem_write`：对应仓库写入能力，必须确认。
- `github_read`：对应只读远端仓库和协作元数据，必须确认网络与 token。
- `github_write`：对应远端写操作，默认不开放。
- `playwright_browser`：对应浏览器自动化，第一阶段只考虑 UI 冒烟和只读检查。
- `shell`：对应本地命令执行，默认禁止。

## 推荐接入顺序

1. `filesystem_read`
2. `database_readonly`
3. `redis_readonly`
4. `github_read`
5. `playwright_browser`
6. `filesystem_write`
7. `github_write`
8. `shell`

## Windows 本地运行注意事项

- MCP Server 是否支持 Windows，需要逐个确认。
- Node.js / `npx` / Python / `uv` 等运行依赖需要本地安装并验证。
- 文件系统、浏览器、数据库客户端权限需要单独确认。
- GitHub 类工具需要单独管理 token，不应写入仓库。

## 后续替换策略

- 不自研 MCP 协议，优先采用官方或成熟社区方案。
- 如果某个 MCP 工具长期不稳定或不支持 Windows，本仓库再评估替代实现。
- 如果后续任务仍然主要是 dry-run 和计划生成，就不急于引入真实 MCP Server。
