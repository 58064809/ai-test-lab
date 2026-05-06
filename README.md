# ai-test-lab

个人专用的执行型 AI 测试助手仓库。

本仓库不是传统测试平台，也不是团队协作平台。当前目标是让 Codex、OpenHands、PyCharm、命令行等入口能够读取项目规则、任务资产、工具说明和最小 runtime 能力，从而直接辅助完成测试工程任务。

## 当前已落地能力

- `AGENTS.md`：仓库级 Agent 工作规则，供 Codex / OpenHands / 其他工程 Agent 读取。
- `agent-assets/`：提示词、工作流、模板、示例等 Agent 资产。
- `docs/tools/`：成熟工具的官方来源、适用场景、接入状态与验证命令。
- `src/ai_test_assistant/`：最小 Python runtime 工程代码。
- SQLite memory：已落地最小持久化 memory 底座，支持 `namespace + key + JSON document`，不是复杂 RAG 或知识库系统。
- Intent router：已落地基于配置规则、关键词、置信度和澄清策略的意图路由。
- LangGraph dry-run orchestrator：已落地最小任务编排骨架，用于生成计划、风险提示和工具授权评估，不是复杂多 Agent 平台。
- Tool registry：已落地工具注册表与权限模型，用于区分 enabled / disabled / planned / unavailable 状态。
- Runtime CLI：已落地最小命令行入口，支持 `intent-only`、`dry-run`、显式 memory 写入、受控只读输入和测试报告链路。
- Filesystem MCP read：已接入 runtime 的显式单文件只读入口 `--mcp-read-file`，仅支持仓库内低风险文本文件。
- GitHub MCP read：已接入显式 `owner/repo + 单文件路径` 的 GitHub 只读入口，不开放写操作。
- `pytest_runner`：已接入受控 pytest 执行入口，只允许通过 adapter 执行仓库相对 target，不是通用 shell。
- Allure report summary：已接入已有 Allure report 目录的只读摘要读取。
- Allure generate：已接入受控 `allure generate` 报告生成入口，不开放 `allure serve` 或任意参数。
- `run-test-report`：已接入 `pytest --alluredir=allure-results -> allure generate -> allure summary` 一键链路。
- `validation/real-task-samples.yaml`：已扩展真实任务样本，用于验证真实测试工程任务下的路由、澄清、工具授权和报告链路。

## 当前工具执行边界

当前 runtime 只开放受控工具，不开放通用执行能力：

- `shell` 禁用。
- `filesystem_write` 禁用。
- `github_write` 禁用。
- 文件系统只支持显式单文件读取，不支持目录读取、glob、多文件自动扫描。
- GitHub 当前只支持显式单文件读取，不创建 PR、不评论、不改 Issue、不写仓库。
- pytest 与 Allure 只通过受控 adapter 执行固定链路，不开放任意命令或任意参数。

## 常用命令

更多示例见 [docs/cli-examples.md](docs/cli-examples.md)。

```bash
python scripts/run_assistant.py "分析这个需求的测试范围" --intent-only
python scripts/run_assistant.py "根据这个需求生成测试计划" --dry-run
python scripts/run_assistant.py "记录本次任务结果" --dry-run --write-memory
python scripts/run_assistant.py "读取 README" --mcp-read-file README.md
python scripts/run_assistant.py "读取远程 README" --github-repo owner/repo --github-read-file README.md --github-ref main
python scripts/run_assistant.py "运行 pytest" --run-pytest tests
python scripts/run_assistant.py "读取 Allure 摘要" --read-allure-report allure-report
python scripts/run_assistant.py "生成 Allure 报告" --generate-allure-report allure-results --allure-output-dir allure-report
python scripts/run_assistant.py "执行测试并总结报告" --run-test-report tests
```

## 原则

- 不造轮子，优先复用工业级通用工具、成熟生态、开源项目、标准协议和已有工程实践。
- 已落地的 SQLite memory 是最小持久化底座，不扩展为复杂 RAG 或知识库平台。
- 已落地的 LangGraph orchestrator 是最小 dry-run 编排骨架，不扩展为复杂 workflow engine 或多 Agent 平台。
- 后续仍不自研复杂 memory、RAG、workflow engine、UI 平台或多 Agent 聊天系统。
- 具体业务知识后置、分层、可插拔、可迁移，不把当前公司或电商业务规则写入通用架构。

## 当前受限能力

- `intent router` 当前是规则路由，不是工业级语义理解，也不调用外部 LLM。
- `orchestrator` 当前是最小 LangGraph dry-run 流程，不包含 checkpointer、HITL、复杂多 Agent 编排。
- `tool registry` 只做注册、状态和权限判断，不等于所有 planned 工具已经可执行。
- `memory` 当前只支持结构化记录、精确 key、简单文本搜索和过滤，不是语义检索。
- `filesystem_mcp_read` 只支持显式单文件读取，不会扩展为目录扫描或多文件检索系统。
- `pytest_runner`、`allure_generate` 是受控 adapter，不是 shell 通用执行器。

## 明确不做

- 不自研 MCP 协议。
- 不把 fallback / bootstrap 能力包装成工业级平台能力。
- 不开放 shell、filesystem_write、github_write。
- 不新增复杂 Web UI 作为当前阶段目标。
- 不写死任何具体业务规则。
