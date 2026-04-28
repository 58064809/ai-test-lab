# Codex Task 015：真实任务样本验证与授权联动

## 任务背景

当前底座已经完成：

- memory 最小持久化底座
- intent router bootstrap / fallback 规则路由
- LangGraph 最小 orchestrator dry-run 骨架
- tool registry 与权限模型
- runtime CLI
- 007 整体审查加固

下一步不要急着接 MCP，也不要开放真实工具执行。

本任务目标是先验证当前底座在真实测试任务样本上的路由、计划、澄清和风险判断是否稳定，并让 orchestrator 与 tool registry 建立授权联动，为后续 MCP 真实接入打安全基础。

## 最高原则

1. 不接入 MCP Server。
2. 不执行本地命令。
3. 不访问外部网络。
4. 不执行真实工具。
5. 不新增复杂 Web UI。
6. 不自研 Agent 框架。
7. 不把规则路由包装成工业级语义理解。
8. 不把 dry-run 计划包装成真实执行。
9. 不写死任何电商业务规则。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/012-industrial-grade-selection-policy.md`
- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/intent/README.md`
- `src/ai_test_assistant/orchestrator/README.md`
- `src/ai_test_assistant/tool_registry/README.md`
- `src/ai_test_assistant/runtime/README.md`
- `configs/intents.yaml`
- `configs/tools.yaml`

## 任务一：新增真实任务样本集

新增：

```text
validation/
  real-task-samples.yaml
  README.md
```

样本来源要求：

- 使用通用测试工程场景。
- 不写当前公司具体业务规则。
- 不包含敏感数据。
- 不包含真实账号、接口地址、token、数据库信息。

`real-task-samples.yaml` 至少包含以下类别：

1. requirement_analysis：需求分析
2. test_case_generation：测试用例生成
3. api_test_design：接口测试设计
4. ui_test_design：UI 自动化设计
5. pytest_execution：pytest 执行意图
6. log_analysis：日志分析
7. bug_report：缺陷报告
8. code_review：代码审查
9. repo_file_change：仓库文件修改
10. tool_research：工具调研
11. memory_update：记忆更新
12. workflow_update：工作流更新
13. ambiguous：模糊输入，必须触发澄清
14. conflicting：冲突输入，必须触发澄清或确认
15. risky：高风险输入，必须产生风险提示或确认要求

每条样本至少包含：

```yaml
- id: sample_001
  task_text: "根据这个登录需求生成测试用例"
  expected_intent: test_case_generation
  expected_clarification_required: false
  expected_workflow: agent-assets/prompts/test-case-generation.md
  expected_risk_level: low
  notes: "通用用例生成样本"
```

## 任务二：新增验证器，但不执行外部工具

新增：

```text
src/ai_test_assistant/validation/
  __init__.py
  models.py
  loader.py
  runner.py
  README.md

tests/test_validation_samples.py
```

要求：

1. 读取 `validation/real-task-samples.yaml`。
2. 调用现有 `IntentRouter` 与 `TaskOrchestrator`。
3. 仅运行 dry-run。
4. 不执行外部工具。
5. 不访问外部网络。
6. 不执行本地命令。
7. 输出每条样本的验证结果。
8. 测试必须验证关键样本能通过。

验收：

```bash
pytest tests/test_validation_samples.py
```

## 任务三：orchestrator 与 tool registry 授权联动

当前 orchestrator 只根据 intent 自己判断风险，还没有真正读取 tool registry。

请新增最小联动：

1. orchestrator 在 review 或 prepare_context 阶段，根据 intent 推荐可能涉及的工具。
2. 从 `ToolRegistry` 读取工具状态和风险等级。
3. 生成 `tool_decisions` 到 state 或 result 中。
4. 仅做授权判定，不执行工具。

推荐映射：

```yaml
test_case_generation: []
requirement_analysis: []
log_analysis: []
bug_report: []
api_test_design:
  - schemathesis
test_case_generation:
  - memory_store
pytest_execution:
  - pytest_runner
ui_test_design:
  - playwright_mcp
repo_file_change:
  - filesystem
code_review:
  - filesystem
tool_research:
  - github
memory_update:
  - memory_store
workflow_update:
  - filesystem
```

注意：这只是风险和授权建议，不代表执行这些工具。

实现建议：

- 在 `configs/assistant.yaml` 中加入 tool registry 配置路径。
- `TaskOrchestrator.from_config()` 可加载 `ToolRegistry`。
- 如果 tool registry 不存在，orchestrator 仍可降级运行，但应在 result 中标注工具授权未评估。
- 不要因为这个任务重构整个 graph。

## 任务四：状态与输出更新

更新 CLI dry-run 输出，使其包含：

- 推荐工具
- 工具状态
- 工具风险等级
- 是否允许执行
- 是否需要确认
- 拒绝原因

但仍然不执行工具。

更新文档：

- `docs/current-status.md`
- `docs/next-steps.md`
- `src/ai_test_assistant/orchestrator/README.md`
- `src/ai_test_assistant/tool_registry/README.md`
- `src/ai_test_assistant/runtime/README.md`

必须明确：

- 已实现 tool registry 授权联动。
- 仍未接入 MCP。
- 仍不执行真实工具。
- 当前只是 dry-run 阶段的工具风险评估。

## 测试要求

新增或更新测试，至少覆盖：

1. validation 样本加载成功。
2. 12 类主要 intent 样本通过。
3. ambiguous 样本触发澄清。
4. pytest_execution 推荐 pytest_runner，且因为 planned 状态不可执行。
5. repo_file_change 推荐 filesystem，且因为 disabled 状态不可执行。
6. ui_test_design 推荐 playwright_mcp，且因为 planned 状态不可执行。
7. dry-run 输出包含工具风险提示。
8. runtime CLI 不执行任何工具。

## 验收命令

```bash
pytest
python scripts/run_assistant.py "根据这个需求生成测试用例" --dry-run
python scripts/run_assistant.py "请运行 pytest 并分析 Allure 结果" --dry-run
python scripts/run_assistant.py "帮我看看这个" --dry-run
```

## 禁止事项

- 不要接入 MCP Server。
- 不要调用 Playwright MCP。
- 不要运行 pytest。
- 不要生成 Allure 报告。
- 不要访问 GitHub 网络接口。
- 不要读写真实业务文件。
- 不要执行 shell 命令。
- 不要开放真实执行分支。
- 不要引入复杂多 Agent 编排。
- 不要引入向量库。

## 完成标准

- 当前底座能通过真实任务样本验证。
- orchestrator 能输出工具授权评估。
- tool registry 与 orchestrator 已建立 dry-run 级联动。
- runtime CLI 能展示工具风险提示。
- 所有测试通过。
- 文档真实反映：仍未接入 MCP，仍不执行真实工具。