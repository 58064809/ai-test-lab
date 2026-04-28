# ai-test-lab

个人专用的执行型 AI 测试助手仓库。

本仓库不定位为传统测试平台，也不定位为团队协作平台。当前目标是让 Codex、OpenHands、PyCharm、命令行等入口能够读取仓库规则、Agent 资产、工具说明和 Python 工程代码，从而更稳定地完成测试工程任务。

## 当前已落地

- `AGENTS.md`：仓库级 Agent 工作规则，供 Codex / OpenHands / 其他工程 Agent 读取。
- `agent-assets/`：提示词、工作流、模板、示例等 Agent 资产。
- `docs/tools/`：成熟工具的官方来源、适用场景、接入状态与验证命令。
- `src/ai_test_assistant/`：Python 工程代码。
- `memory` 最小底座：已落地 SQLite 持久化记忆能力。
- `intent router`：已落地基于配置规则、关键词、置信度和澄清策略的意图路由底座。

## 原则

- 不自研 memory、知识库、任务编排、浏览器自动化、接口测试生成器。
- 优先使用官方能力和成熟生态，例如 Codex、OpenHands、MCP、Playwright MCP、Schemathesis、Keploy、Pytest、Allure。
- 当前先沉淀能被 Agent 读取和执行的规则、流程、模板、示例和工具说明。
- 具体业务知识后置，不写死当前公司的电商业务。

## 官方依据

- OpenAI Codex 介绍：Codex 可以读取仓库中的 `AGENTS.md`，用于了解代码库导航方式、测试命令和项目实践。https://openai.com/index/introducing-codex/
- OpenAI Codex / AGENTS.md 文档入口：https://github.com/openai/codex/blob/main/docs/agents_md.md
- GitHub Copilot 仓库自定义指令：`.github/copilot-instructions.md` 可提供仓库级指导；GitHub 文档也提到 `AGENTS.md` 可作为 AI agents 使用的指令文件。https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot
- OpenHands 官方文档：https://docs.openhands.dev/
- Model Context Protocol 官方文档：https://modelcontextprotocol.io/
- Playwright MCP 官方仓库：https://github.com/microsoft/playwright-mcp
- Schemathesis 官方 Quick Start：https://schemathesis.github.io/schemathesis/quick-start/
- Keploy 官方文档：https://keploy.io/docs/
- Allure Pytest 官方文档：https://allurereport.org/docs/pytest/

## 当前状态

本仓库当前处于“memory 与 intent router 已落地、其余模块待接入”阶段。

已实现：

- SQLite 持久化 memory store
- `MemoryService` 配置加载
- `tests/test_memory_store.py`
- 配置化 intent router
- `configs/intents.yaml`
- `tests/test_intent_router.py`

尚未实现：

- orchestrator
- tool registry
- runtime CLI

受限能力：

- intent 第一版只是规则路由，不是复杂 NLP。
- intent 第一版不调用外部 LLM。
- 仓库中的工具说明和 Agent 资产仍然以文档形式沉淀，未把未验证能力伪装成已完成集成。
