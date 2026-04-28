# Codex Task 011：修复 intent 路由交付审查问题

## 背景

你已经完成了 `003-intent-router.md` 的第一轮实现。审查结论：主体方向正确，但暂不能进入 orchestrator，因为还存在测试覆盖、配置质量校验和状态文档同步问题。

本任务只修复 intent 路由交付问题，不要实现 orchestrator、tool registry、runtime CLI。

## 必须先阅读

- `codex-tasks/003-intent-router.md`
- `configs/intents.yaml`
- `src/ai_test_assistant/intent/README.md`
- `src/ai_test_assistant/intent/router.py`
- `src/ai_test_assistant/intent/rules_loader.py`
- `tests/test_intent_router.py`
- `README.md`
- `docs/current-status.md`

## 问题 1：测试没有覆盖全部必需 intent

`configs/intents.yaml` 已包含 12 类 intent，但 `tests/test_intent_router.py` 当前只重点断言了少数几个。

请补充测试，至少验证以下 intent 均存在并可被清晰输入路由：

- requirement_analysis
- test_case_generation
- api_test_design
- ui_test_design
- pytest_execution
- log_analysis
- bug_report
- code_review
- repo_file_change
- tool_research
- memory_update
- workflow_update

要求：

- 可以使用参数化测试。
- 每个 intent 至少一个明确输入样例。
- 断言 intent、confidence、recommended_workflow、clarification_required。
- 不要为了测试硬编码绕过 router。

## 问题 2：配置加载缺少质量校验

当前 loader 只校验必填字段存在，但没有校验：

- intent name 是否重复
- triggers 是否为空
- required_context 是否为空
- minimum_confidence 是否在 0~1 之间
- ambiguity_gap 是否在 0~1 之间

请在 `IntentRulesLoader` 中补充配置质量校验。

要求：

- 重复 intent name 抛 `ValueError`。
- triggers 为空抛 `ValueError`。
- required_context 为空抛 `ValueError`。
- confidence / gap 超出范围抛 `ValueError`。
- 补充对应单元测试。

## 问题 3：README 和 current-status 状态未同步

当前根目录 `README.md` 和 `docs/current-status.md` 仍写着 intent router 待接入。

请更新：

- `README.md`
- `docs/current-status.md`
- 如有必要，更新 `docs/next-steps.md`

要求明确区分：

- 已实现：memory、intent router
- 待接入：orchestrator、tool registry、runtime CLI、LangGraph / MCP 真实接入
- 受限能力：intent 第一版是规则匹配，不调用外部 LLM，不做复杂 NLP

## 问题 4：assistant config 相对路径解析需要更稳

`IntentRouter.from_assistant_config()` 从 `configs/assistant.yaml` 读取 `intent.rules_path`。

请确认相对路径解析策略：

- 默认仓库根目录运行时，`configs/intents.yaml` 可以正常加载。
- 如果传入的 assistant config 使用绝对路径，也可以正常加载。
- 如果传入的 assistant config 使用相对 rules_path，应有明确约定：相对于当前工作目录，或相对于 assistant config 所在目录。请选择一种并写入 README 和测试。

建议优先保持简单：相对路径按当前工作目录解析；测试里同时覆盖绝对路径。

## 禁止事项

- 不要实现 orchestrator。
- 不要实现 tool registry。
- 不要实现 runtime CLI。
- 不要调用外部 LLM。
- 不要引入 NLP 库。
- 不要引入 LangGraph。
- 不要把规则路由伪装成语义理解。
- 不要把未验证能力写成已完成。

## 验收命令

```bash
pytest tests/test_intent_router.py
pytest tests/test_memory_store.py
```

## 完成标准

- 12 类 intent 均有清晰路由测试。
- 配置质量校验有测试。
- README / current-status 状态真实。
- intent README 明确第一版规则路由能力边界。
- 不新增无关功能。

完成后，intent 路由底座可判定为阶段性通过，再进入 `004-orchestrator-langgraph.md`。