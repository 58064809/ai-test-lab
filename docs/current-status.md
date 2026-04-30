# Current Status

## 032 GitHub MCP live smoke 收口

- GitHub MCP read 已完成最小 read 接入和用户本地 live smoke 验证。
- 当前只支持显式 `--github-repo owner/repo` + 显式 `--github-read-file path` 的单文件读取，不自动猜仓库或文件。
- README 读取验证结果：允许读取=是，来源=`github_mcp`，路径=`README.md`，返回 SHA=`d158cba4bd47f227961ff37268956ffb46f63eef`。
- 敏感路径拒绝已验证：读取 `.env` 被拒绝，原因为 `Sensitive GitHub file path is blocked.`
- 当前 GitHub MCP read 返回的是下载成功提示和 SHA，不保证直接返回完整文件正文。
- `github_write`、`shell`、`filesystem_write` 仍保持 disabled。

## 030 pytest_runner 最小真实执行

- 已新增 `src/ai_test_assistant/testing/pytest_runner.py`
- 已新增 `PytestRunner` 薄 adapter 与 `PytestRunResult`
- runtime CLI 已新增显式 `--run-pytest [TARGET]` 入口
- `pytest_runner` 已改为 `enabled + execute_local_command`
- `pytest_runner` 只允许执行 `sys.executable -m pytest <repo-relative-target>`
- `subprocess.run` 使用 args list 且固定 `shell=False`
- 默认 target 为 `tests`
- 只允许仓库内相对路径 target
- 已拒绝绝对路径、`..` 路径穿越、glob 和额外参数注入
- 真实 pytest 执行结果已支持结构化输出
- 当前不接 Allure
- `shell` 仍保持 `disabled`
- `filesystem_write` 仍保持 `disabled`

## 028 filesystem MCP runtime 只读接入

- 已接入官方 Python MCP SDK 依赖：`mcp`
- 已新增 `src/ai_test_assistant/filesystem/mcp_client.py`
- runtime CLI 已新增显式 `--mcp-read-file` 入口
- `--mcp-read-file` 只支持显式单文件只读读取
- MCP 读取前仍必须先经过 `FilesystemReadPolicy`
- policy 拒绝 `.env`、`.git/`、`.assistant/`、token、secret、password 类路径时，不启动 MCP server
- 当前 filesystem MCP server 固定采用 `@modelcontextprotocol/server-filesystem`
- MCP server 根目录限制为 `repo_root`
- `filesystem_mcp_read` 已改为 `enabled + read_only`
- `filesystem_write` 仍保持 `disabled`
- `shell` 仍保持 `disabled`
- 默认只展示文件预览；只有显式传 `--show-file-content` 才展示完整允许内容
- `task_result/orchestrator` memory 仍只记录文件元信息，不保存完整文件内容
- `LocalFilesystemReadAdapter` 继续保留为 fallback
- 当前不实现目录读取、`glob`、多文件读取或自动上下文收集

## 026 filesystem MCP 最小配置

- 已确定后续官方 / 主流 filesystem MCP server 采用 `@modelcontextprotocol/server-filesystem`
- 已新增 `docs/filesystem-mcp-quickstart.md`
- 已新增 `docs/local-environment-prerequisites.md`
- 已新增 `configs/mcp/filesystem-server.example.json`
- 当前只落地最小配置模板、Windows 前置条件和本地验证命令
- 已记录本地环境验证结果：`node -v`=`v24.15.0`、`npm -v`=`11.12.1`、`npx -v`=`11.12.1`
- 用户本地已验证 `npx -y @modelcontextprotocol/server-filesystem .` 可启动，并返回 `Secure MCP Filesystem Server running on stdio`
- 026 阶段原先尚未接入 Python runtime 的 MCP client；该限制已在 028 中解除，但仍只开放显式单文件只读读取
- 当前 `filesystem_read` 仍然是 `local_python` fallback
- 当前 `filesystem_write` 仍然保持 `disabled`
- 当前 `shell` 仍然保持 `disabled`
- 当前不继续复杂选型，不扩展 `LocalFilesystemReadAdapter`，不实现多文件读取

## 025 filesystem MCP 官方 / 主流确认

- 用户已明确选择：优先确认官方或主流生态中的 filesystem MCP server。
- 已新增 `docs/filesystem-mcp-official-mainstream-confirmation.md`，只做候选收敛与事实确认，不做任何 MCP 接入代码。
- 当前已确认官方 `modelcontextprotocol` 组织、官方包 `@modelcontextprotocol/server-filesystem`、Anthropic Agent SDK 示例和 VS Code 配置入口存在。
- 当前仍未确认通用的 server-side 禁写开关，因此结论仍是“暂缓”，尚不进入最小接入实现。

## 已实现

- `memory` 最小可运行底座已落地。
- `intent router` 最小可运行底座已落地。
- orchestrator 工业级选型说明已完成，正式目标方案选择为 LangGraph。
- LangGraph 最小 orchestrator 骨架已落地，支持 dry-run 计划生成。
- tool registry 与权限模型底座已落地。
- 最小 runtime CLI 已落地，支持 intent-only 与 dry-run 入口。
- 最小 pytest_runner 真实执行入口已落地，支持显式 `--run-pytest`。
- 已新增真实任务样本集与 dry-run 验证器。
- 已完成 MCP 接入前置选型文档与安全边界设计。
- 已完成 filesystem_read 接入前安全策略设计。
- 已落地 filesystem_read 本地白名单只读 adapter。
- `codex-tasks/021-explicit-multi-file-read-context.md` 已暂停，不执行。
- 已完成成熟 filesystem MCP / 等价成熟工具的选型文档与最小接入验证方案。
- 已新增 `docs/filesystem-mcp-manual-checklist.md`，用于人工确认候选方案，但尚未完成真实人工核验。
- `python scripts/run_assistant.py ...` 已可从仓库根目录直接运行，不依赖测试注入 `src` 路径。
- Agent 资产已统一迁移到 `agent-assets/`。
- 工具说明文档已统一迁移到 `docs/tools/`。
- Python 工程代码统一放在 `src/ai_test_assistant/`。
- `SQLiteMemoryStore` 支持：
  - `put_memory`
  - `get_memory`
  - `search_memory`
  - `delete_memory`
- `MemoryService` 可从 YAML 配置读取 SQLite 路径。
- `tests/test_memory_store.py` 覆盖写入、读取、搜索、删除、重建实例后的持久化读取。
- `IntentRouter` 支持基于配置化规则、关键词、置信度和澄清策略进行意图识别。
- `tests/test_intent_router.py` 覆盖 12 类 intent 路由、模糊输入澄清和配置异常场景。
- `TaskOrchestrator` 支持最小流程：
  - `receive_task`
  - `load_memory`
  - `classify_intent`
  - `select_workflow`
  - `prepare_context`
  - `plan`
  - `review`
  - `write_memory`
- `TaskOrchestrator.run(..., write_memory=False)` 默认不写入 `task_result/orchestrator`。
- 只有显式传 `write_memory=True` 或 CLI 传 `--write-memory` 时，才写入 `task_result/orchestrator`。
- `TaskOrchestrator` 已在 dry-run 阶段接入 tool registry 授权联动，可输出推荐工具、工具状态、风险等级、是否允许执行、是否需要确认和拒绝原因。
- memory 工具权限已拆分为：
  - `memory_read`：只读、已启用
  - `memory_write`：长期记忆写入、默认不开放
- `tests/test_orchestrator_smoke.py` 覆盖 dry-run、澄清和非执行边界。
- `ToolRegistry` 支持工具配置加载、状态查询和权限判定。
- `tests/test_tool_registry.py` 覆盖注册表加载、状态风险检查和权限边界。
- `docs/mcp-selection.md` 已定义 MCP 候选工具、接入顺序和暂缓接入项。
- `docs/mcp-security-policy.md` 已定义 L0-L6 工具权限分层与默认禁止规则。
- `tests/test_mcp_selection_docs.py` 覆盖 MCP 文档存在性和关键安全边界一致性。
- `docs/filesystem-read-design.md` 已定义 filesystem_read 的白名单、黑名单、路径穿越拦截和 dry-run 边界。
- `docs/filesystem-mcp-selection.md` 已完成成熟 filesystem MCP / 等价成熟工具选型说明。
- `docs/filesystem-mcp-minimal-integration-plan.md` 已完成最小接入验证方案。
- `docs/filesystem-mcp-manual-checklist.md` 已整理候选方案人工确认清单、禁止接入条件和证据记录模板。
- `src/ai_test_assistant/filesystem/policy.py` 已提供路径安全策略模型，但不真实读取文件。
- `src/ai_test_assistant/filesystem/adapter.py` 已提供本地只读单文件 adapter，所有读取都经过 `FilesystemReadPolicy`。
- `configs/tools.yaml` 中 `filesystem_read` 已启用为 `enabled + read_only` 的本地 adapter，不代表 MCP 已接入。
- `tests/test_filesystem_read_policy.py` 覆盖白名单、黑名单和路径穿越。
- `tests/test_filesystem_read_adapter.py` 覆盖允许读取、拒绝敏感路径、文件不存在、二进制文件和大文件处理。
- `runtime CLI` 已支持显式 `--read-file` 单文件读取入口，只用于 dry-run 上下文展示。
- `runtime CLI` 已支持 `--show-file-content`，默认只展示文件预览。
- `runtime CLI` 已支持显式 `--run-pytest`，用于受控 pytest 真实执行。
- 文件读取结果已接入 orchestrator dry-run 上下文。
- `task_result/orchestrator` memory 只记录文件元信息，不保存完整文件内容。
- `runtime CLI` 支持 `task_text`、`--dry-run`、`--intent-only`、`--write-memory`、`--config`。
- `runtime CLI` 当前真实执行只开放 `pytest_runner`，不开放 shell 通用命令。
- `tests/test_runtime_cli.py` 覆盖启动、intent-only、dry-run、澄清提示、配置异常、memory 写入开关语义和工具风险提示输出。
- `tests/test_filesystem_mcp_selection_docs.py` 覆盖 filesystem MCP 文档存在性和配置边界一致性。
- `tests/test_filesystem_mcp_manual_checklist.py` 覆盖人工确认清单存在性、未验证表述约束和工具配置边界。
- `validation/real-task-samples.yaml` 覆盖 15 类通用测试工程样本。
- `tests/test_validation_samples.py` 覆盖样本加载、12 类主要 intent 验证、模糊输入澄清和 dry-run 工具授权结果。

## 待验证

- Windows 之外环境的 SQLite 文件行为。
- 更大数据量下的搜索性能。
- 后续多模块并发访问时的锁竞争行为。
- 更真实任务文本下的 orchestrator 计划质量与澄清触发阈值。
- tool-intent 映射在更多真实项目中的稳定性。
- MCP 工具在更多 Windows 本地环境下的真实可运行性。
- pytest 在更多 Windows 本地环境下的执行稳定性。
- filesystem_read 策略模型与未来 MCP adapter 的真实对接方式。
- filesystem_read 本地 adapter 与未来 MCP filesystem adapter 的替换细节。
- `mcp` Python SDK 与官方 filesystem server 在用户本地环境中的依赖安装稳定性。

## 待接入

- 除 `filesystem_mcp_read` 之外的其他 MCP 真实接入。
- 真实工具执行层。
- orchestrator 的正式执行分支。
- 与 tool registry 联动的更细粒度执行授权。
- 如果未来确有收益，再评估 tool registry 到 MCP 真实执行器的适配层。

## 受限能力

- 当前搜索不是语义检索，只是 namespace 内文本匹配和简单过滤。
- 当前 intent 不是复杂 NLP，只是规则匹配。
- 当前 intent 不调用外部 LLM。
- 当前 orchestrator 只实现最小 LangGraph 骨架，不包含 checkpointer、HITL、工具执行和复杂状态流。
- 当前 orchestrator 的 tool registry 联动仍以 dry-run 级风险评估为主；真实工具执行目前只开放显式 `pytest_runner`。
- 当前 `memory_write` 只用于授权评估和风险提示，不会触发真实长期记忆写入。
- 当前 tool registry 只做注册与权限判定，不执行本地命令，不访问外部网络；真实 MCP 接入目前只开放 `filesystem_mcp_read`。
- 除 `filesystem_mcp_read` 外，其他 MCP 相关文档仍只是选型与安全边界设计，不代表已接入。
- 当前 filesystem_read 虽然已同时支持本地 adapter 与 MCP 只读入口，但都只限显式单文件读取。
- 当前 `LocalFilesystemReadAdapter` 只是 bootstrap / fallback，不是长期正式 filesystem 能力。
- 当前不继续扩展本地 adapter 为多文件读取、目录读取、自动上下文收集或文件检索系统。
- 当前 filesystem_write 仍未开放。
- 当前文件内容默认只展示预览，完整内容需要显式参数。
- 当前 runtime CLI 只允许调用 intent-only、orchestrator dry-run、显式只读文件读取和显式 `pytest_runner`，不开放写文件或 shell 执行。
- 当前默认不写入 `task_result/orchestrator`，需要显式 `--write-memory`。

## 明确不做

- 不自研 MCP 协议。
- 不把规则路由、dry-run 计划或文档占位能力包装成工业级能力。
- 不在当前阶段接入复杂多 Agent 聊天系统。
- 不写死任何电商业务规则。
# 031 GitHub MCP read 最小接入

- 已接入 GitHub MCP read 最小能力：采用官方 `github/github-mcp-server`，通过 MCP SDK / 协议调用。
- runtime 已提供显式 GitHub 单文件读取入口：`--github-repo owner/repo --github-read-file path`，来源标记为 `github_mcp`。
- 当前不支持 GitHub 写操作，不保存 token，不打印 token；`github_write`、`shell`、`filesystem_write` 保持 disabled。
