# Next Steps

## 037 Allure 链路收口之后

- 一键链路优先使用：`python scripts/run_assistant.py "运行测试并总结报告" --run-test-report`。
- 如需指定单个测试文件，使用：`python scripts/run_assistant.py "运行测试并总结报告" --run-test-report tests/test_xxx.py`。
- 该入口固定执行 `pytest -> allure generate -> Allure report summary`，不要扩展任意 pytest 参数、任意 Allure 参数或 `allure serve`。
- 后续 Allure 相关工作只做缺陷修复和真实样本验证；除非能力边界改变，不再拆新的 Allure 小任务。
- `shell`、`filesystem_write`、`github_write` 继续保持不开放。

## 036 Allure CLI 生成之后

- 可先运行：`python scripts/run_assistant.py "生成 Allure 报告" --generate-allure-report`。
- 再读取摘要：`python scripts/run_assistant.py "分析 Allure 报告" --read-allure-report allure-report`。
- 前提是本机已安装 Allure CLI，且仓库内已有 `allure-results`。
- 后续不要扩展到 `allure serve`、浏览器打开或任意 Allure 参数。
- `shell`、`filesystem_write`、`github_write` 继续保持不开放。

## 035 Allure 只读摘要之后

- 继续保持 `allure_report` 的边界：只读已有 `allure-report` 目录，不生成报告，不执行 Allure CLI。
- 手动验证可使用：`python scripts/run_assistant.py "分析 Allure 报告" --read-allure-report allure-report`。
- 如果报告目录不存在或缺少 `widgets/summary.json`，应输出结构化失败原因，不自动生成报告。
- 如后续需要“运行 pytest 后生成 Allure 报告”，必须单独任务接入官方 Allure CLI，且不能通过 shell 通用命令绕过受控入口。
- `shell`、`filesystem_write`、`github_write` 继续保持不开放。

## 034 显式工具执行展示对齐之后

- 继续保持显式入口和 dry-run 推荐工具的边界：`--github-read-file`、`--mcp-read-file`、`--read-file`、`--run-pytest` 才能触发对应真实动作。
- 普通 dry-run 仍只做计划、推荐工具和授权风险提示，不自动执行推荐工具。
- 后续如增加新显式入口，也必须同步记录显式工具执行元信息，避免输出中同时出现“已执行”和“dry-run 未授权”的矛盾。
- 不开放 `github_write`、`shell`、`filesystem_write`。

## 033 GitHub MCP 正文解析增强之后

- 下一步可用用户本地 token 重新运行 README 单文件读取，确认当前 MCP SDK 是否透传 embedded resource text。
- 如果仍只看到下载成功提示和 SHA，保持原样，不伪造 README 正文。
- 如确需完整正文，有两条合规路线：继续确认官方 MCP 是否支持稳定返回正文；或另起任务评估已有 GitHub connector / 官方 SDK 作为独立 read-only 工具，并单独授权、单独边界。
- 不自研 GitHub REST API fallback，不新增 `requests` / `httpx` 直连 GitHub API。
- 继续禁止 GitHub 写操作、issue / PR / comment、merge / push / 改文件，`github_write`、`shell`、`filesystem_write` 保持 disabled。

## 032 GitHub MCP live smoke 之后

- GitHub MCP read 已完成最小 live smoke 验证，下一步只围绕只读能力做稳定性增强。
- 可选下一步：确认官方 `get_file_contents` 返回结构后增强 README 正文解析，但不自研 GitHub REST API fallback。
- 可选下一步：按官方 GitHub MCP read-only tool 单独评估 Issue / PR 只读元数据读取，必须继续保持显式参数和白名单。
- 可选下一步：补 Allure 报告读取与总结，不通过 shell 通用命令绕过受控入口。
- 继续禁止 issue / PR / comment / merge / push / 改文件，`github_write`、`shell`、`filesystem_write` 保持不开放。
- 不实现目录批量读取、搜索全仓库或自然语言自动猜仓库 / 文件。

## 030 pytest_runner 最小真实执行之后

- 下一步继续保持“单一受控工具入口”的节奏，不扩展成 shell 通用执行器。
- 当前 `pytest_runner` 已可真实执行，后续重点是验证更多仓库内 target 场景，而不是开放额外参数。
- 当前不生成 Allure 报告、不接报告服务、不开放 shell；Allure 只读摘要已由 `--read-allure-report` 接入。
- `filesystem_write`、`shell` 继续保持 `disabled`。

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
- 待接入：除受控 `pytest_runner` 外的其他真实工具执行层
- 待接入：orchestrator 正式执行分支
- 待接入：tool registry 与 orchestrator 的正式执行授权联动
- 待接入：更系统化的真实任务样本库扩展

## 风险提醒

- 当前 `intent router` 仍然只是 bootstrap / fallback 规则路由，不应包装成工业级语义理解系统。
- 当前 `orchestrator` 仍然只是最小 dry-run 骨架，即使已经接入 tool registry 授权联动，也不应包装成完整执行平台。
- 当前除 `filesystem_mcp_read` 之外，其余 MCP 规划文档不代表真实接入，不应把 planned 工具包装成 enabled。
- 当前 filesystem_read 本地 adapter 只是 fallback，不应扩展成通用文件管理器。
- 当前 `pytest_runner` 虽然已启用，但它只是受控 pytest 执行，不是 shell 通用执行器。
- 当前文件读取上下文只支持显式单文件输入，不应扩展成自然语言自动多文件读取。
- 当前不应继续开发多文件读取、目录读取、glob / 通配符读取、自动上下文收集或文件检索。
- 当前虽然已接入成熟 filesystem MCP 的只读读取入口，但不代表任何写能力或 shell 能力已开放。
- 即使继续使用 LangGraph，也不要在 graph 外面再包一层复杂自研状态机。
- 如果后续只需要结构化查询，不应过早引入向量库。
# 031 GitHub MCP read 之后

- GitHub MCP read 已完成本地真实 token 手工验证，后续只做必要的只读稳定性增强和只读元数据白名单扩展。
- 如需读取 issue / PR 元数据，必须先确认官方 GitHub MCP read-only tool，再单独新增显式参数和测试。
- 继续禁止 issue / PR / comment / merge / push / 改文件，`github_write` 保持不开放。
