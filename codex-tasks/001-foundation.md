# Codex Task 001：搭建个人执行型 AI 测试助手底座

## 目标

请基于本仓库现有 `AGENTS.md`、`README.md`、`docs/tools/`、`agent-assets/prompts/`、`agent-assets/workflows/`、`agent-assets/templates/`，搭建一个可运行的个人执行型 AI 测试助手底座。

这不是继续补 Markdown，也不是自研平台。目标是让仓库具备最小可运行的 memory、intent、orchestrator、tool registry、runtime CLI。

## 最高原则

1. 不造轮子。
2. 不自研 LLM、向量库、MCP 协议、复杂 Web UI。
3. 优先复用 LangGraph / LangChain memory / MCP / Pytest / Allure / Playwright MCP / Schemathesis / Keploy。
4. 代码只做胶水层、适配层、配置层。
5. 不把当前公司的电商业务写死进通用底座。
6. 未验证能力必须标注为待接入或待验证。

## 必须先阅读

- `AGENTS.md`
- `README.md`
- `docs/tools/sources.md`
- `docs/tools/langgraph.md`
- `docs/tools/mcp.md`
- `docs/tools/pytest-allure.md`
- `docs/tools/playwright-mcp.md`
- `docs/tools/schemathesis.md`
- `docs/tools/keploy.md`

## 目标目录

```text
src/ai_test_assistant/
  __init__.py
  config/
  memory/
  intent/
  orchestrator/
  tool_registry/
  runtime/
  schemas/

configs/
  assistant.yaml

scripts/
  run_assistant.py

tests/
  test_memory_store.py
  test_intent_router.py
  test_orchestrator_smoke.py

docs/
  foundation-architecture.md
  current-status.md
  next-steps.md
```

## 模块 1：memory

实现本地持久化记忆底座。

要求：

- 参考 LangGraph / LangChain long-term memory 的 namespace + key + JSON document 模型。
- 第一版优先使用 SQLite 或官方 store。
- 支持 project_rule、user_preference、workflow_memory、task_result、tool_capability。
- 提供 put/get/search/delete API。
- 必须有测试。

验收：

```bash
pytest tests/test_memory_store.py
```

## 模块 2：intent

实现意图识别和路由底座。

要求：

- 第一版使用规则、关键词和配置文件即可。
- 不要自研复杂 NLP。
- 至少支持 requirement_analysis、test_case_generation、api_test_design、ui_test_design、pytest_execution、log_analysis、bug_report、code_review、repo_file_change、tool_research、memory_update、workflow_update。
- 路由结果包含 intent、confidence、matched_rules、required_context、recommended_workflow、clarification_required。
- 模糊任务必须返回需要澄清。

验收：

```bash
pytest tests/test_intent_router.py
```

## 模块 3：orchestrator

实现最小任务编排底座。

要求：

- 优先参考 LangGraph 的 state graph、node、checkpoint 思路。
- 如果直接引入 LangGraph 成本可控，优先使用 LangGraph。
- 如暂不引入，接口必须兼容未来 LangGraph 接入。
- 最小流程：receive_task -> load_memory -> classify_intent -> select_workflow -> prepare_context -> plan -> review -> write_memory。
- 支持 dry-run。

验收：

```bash
pytest tests/test_orchestrator_smoke.py
python scripts/run_assistant.py "根据这个需求生成测试用例" --dry-run
```

## 模块 4：tools

实现工具注册和权限模型。

要求：

- 不自研 MCP 协议。
- 先实现 tool registry。
- 工具状态区分 enabled、disabled、planned。
- 工具风险级别区分 read_only、write_project_files、execute_local_command、external_network、restricted_action。
- 未启用工具不可执行。

## 模块 5：runtime CLI

提供命令行入口：

```bash
python scripts/run_assistant.py "帮我分析这个需求" --dry-run
python scripts/run_assistant.py "分析这段日志" --intent-only
```

要求：

- 默认中文输出。
- 默认只做计划和路由，不执行高风险动作。
- 输出意图、置信度、使用的记忆、推荐 workflow、下一步计划。

## 文档要求

新增或更新：

- `docs/foundation-architecture.md`
- `docs/current-status.md`
- `docs/next-steps.md`

文档必须区分：

- 已实现
- 已设计但未实现
- 待接入
- 受限能力
- 明确不做

## 禁止事项

- 不要只继续补 Markdown。
- 不要把 prompts/templates 称为底座。
- 不要实现自研 memory 框架、任务编排框架、工具协议。
- 不要写死具体业务。
- 不要把未验证能力写成已完成。

## 最终验收

```bash
pytest
python scripts/run_assistant.py "根据这个需求生成测试用例" --dry-run
python scripts/run_assistant.py "分析这段日志" --intent-only
```

通过标准：

- 测试通过。
- 能识别意图。
- 能读写本地记忆。
- 能输出任务计划。
- 能列出工具注册表。
- 文档说明真实状态。
