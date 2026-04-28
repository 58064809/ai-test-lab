# ai-test-lab

个人专用的执行型 AI 测试助手仓库。

本仓库不定位为传统测试平台，也不定位为团队协作平台。当前目标是让 Codex、OpenHands、PyCharm、命令行等入口能够读取仓库规则、Agent 资产、工具说明和 Python 工程代码，从而更稳定地完成测试工程任务。

## 当前已落地

- `AGENTS.md`：仓库级 Agent 工作规则，供 Codex / OpenHands / 其他工程 Agent 读取。
- `agent-assets/`：提示词、工作流、模板、示例等 Agent 资产。
- `docs/tools/`：成熟工具的官方来源、适用场景、接入状态与验证命令。
- `src/ai_test_assistant/`：Python 工程代码。
- `memory`：SQLite 持久化记忆底座，支持 `namespace + key + JSON document`。
- `intent router`：基于配置规则、关键词、置信度和澄清策略的意图路由底座。
- `orchestrator`：基于 LangGraph 的最小 dry-run 编排骨架。
- `tool registry`：工具注册表与权限模型。
- `runtime CLI`：最小命令行入口，支持 `intent-only` 与 `dry-run`。

## 原则

- 不自研 memory、知识库、任务编排、浏览器自动化、接口测试生成器。
- 优先使用官方能力和成熟生态，例如 Codex、OpenHands、MCP、Playwright MCP、Schemathesis、Keploy、Pytest、Allure。
- 当前先沉淀能被 Agent 读取和执行的规则、流程、模板、示例和工具说明。
- 具体业务知识后置，不写死任何电商业务规则。

## 当前状态

### 已实现

- `memory` 最小底座已落地，持久化后可通过测试验证重启后读取。
- `intent router` 已落地，规则存放在 `configs/intents.yaml`。
- `orchestrator` 已落地最小 LangGraph 流程，只生成任务计划，不执行外部工具。
- `tool registry` 已落地注册与权限判定，不包含真实执行器。
- `runtime CLI` 已可运行，支持：
  - `python scripts/run_assistant.py "根据这个需求生成测试用例" --dry-run`
  - `python scripts/run_assistant.py "分析这段日志" --intent-only`
- `--write-memory` 已真实控制 `task_result/orchestrator` 写入：
  - 默认不写
  - 显式传入才写
  - `--intent-only` 始终不写

### 受限能力

- `intent router` 第一版只是规则路由，不是工业级语义理解，也不调用外部 LLM。
- `orchestrator` 第一版只是最小 LangGraph dry-run 骨架，不包含 checkpointer、HITL、工具执行和复杂多 Agent 编排。
- `tool registry` 第一版只做注册和权限模型，不执行本地命令，不访问外部网络，不接入真实 MCP Server。
- `runtime CLI` 当前只开放 `intent-only` 和 `dry-run`，不开放真实执行。
- `memory` 当前只支持精确 key 读取、简单文本搜索和 `memory_type/source` 过滤，不是语义检索。

### 待接入

- MCP 真实接入
- 真实工具执行层
- 更完整的 orchestrator 执行分支
- 与 tool registry 联动的正式执行决策

### 待验证

- Windows 之外环境的 SQLite 文件行为
- 更大数据量下的 memory 搜索性能
- 多模块并发访问时的锁竞争行为

### 明确不做

- 不自研 MCP 协议
- 不把 fallback / bootstrap 能力包装成工业级能力
- 不引入复杂 Web UI 作为当前阶段目标
- 不写死任何业务规则
