# Intent 路由底座说明

## 已实现

- 基于 YAML 规则的意图识别与路由。
- 不调用外部 LLM。
- 支持关键词触发、负向触发、置信度和澄清策略。
- 支持以下 intent：
  - `requirement_analysis`
  - `test_case_generation`
  - `api_test_design`
  - `ui_test_design`
  - `pytest_execution`
  - `log_analysis`
  - `bug_report`
  - `code_review`
  - `repo_file_change`
  - `tool_research`
  - `memory_update`
  - `workflow_update`

## 当前限制

- 第一版只做规则匹配，不做复杂 NLP。
- 第一版不接入外部 LLM、向量检索或语义分类模型。
- 输入过短、命中不足或多个 intent 冲突时，会返回 `clarification_required=true`。

## 待接入 / 待验证

- 待接入：未来 orchestrator 调用后的上下文增强路由。
- 待验证：更多真实任务语料下的触发词覆盖率。
- 待验证：是否需要从 memory 中读取用户长期偏好后再做加权。

## 明确不做

- 第一轮不实现 orchestrator。
- 第一轮不实现 tool registry。
- 第一轮不实现 runtime CLI。

