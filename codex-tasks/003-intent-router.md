# Codex Task 003：实现 intent 意图识别与路由底座

## 任务目标

在 `001-foundation.md` 与 `002-memory-foundation.md` 的基础上，实现个人 AI 测试助手的意图识别与路由底座。

这不是让你自研复杂 NLP 系统，而是先用配置化规则、关键词、置信度和澄清策略，形成可维护、可测试、可替换的 intent router。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/001-foundation.md`
- `codex-tasks/002-memory-foundation.md`
- `prompts/requirement-analysis.md`
- `prompts/test-case-generation.md`
- `prompts/log-analysis.md`
- `prompts/bug-report.md`

## 实现范围

请实现：

```text
src/ai_test_assistant/intent/
  __init__.py
  models.py
  router.py
  rules_loader.py
  README.md

configs/intents.yaml

tests/test_intent_router.py
```

## 必须支持的 intent

至少支持：

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

## 路由结果结构

每次识别必须返回：

- intent
- confidence
- matched_rules
- required_context
- recommended_workflow
- clarification_required
- clarification_questions

## 配置要求

`configs/intents.yaml` 中每个 intent 至少包含：

- name
- description
- triggers
- negative_triggers
- required_context
- optional_context
- recommended_workflow
- default_prompt

## 置信度要求

- 明确命中多个强触发词时，置信度可较高。
- 命中多个互斥 intent 时，必须降低置信度。
- 信息不足时必须 `clarification_required=true`。
- 不允许把模糊输入硬路由成确定任务。

## 示例验收

以下输入应路由到 `test_case_generation`：

```text
根据这个需求生成测试用例
```

以下输入应路由到 `log_analysis`：

```text
分析这段报错日志
```

以下输入应触发澄清：

```text
帮我看看这个
```

## 禁止事项

- 不要自研复杂 NLP。
- 不要调用外部 LLM 作为第一版 intent router。
- 不要把当前公司业务规则写进 intent。
- 不要只有 if/else 散落在代码里，规则必须配置化。
- 不要让低置信度结果直接进入执行层。

## 验收命令

```bash
pytest tests/test_intent_router.py
```

## 完成标准

- 单测通过。
- intent 规则可配置。
- 路由结果包含置信度和澄清信息。
- 后续 orchestrator 可以直接调用 intent router。