# Codex Task 016：补齐 risky 样本验证与 memory 工具权限拆分

## 背景

015 已完成真实任务样本验证与 orchestrator/tool registry 的 dry-run 授权联动，主体方向正确。

审查发现两个需要修复的问题：

1. `validation/real-task-samples.yaml` 中已有 `risky` 样本，但 `tests/test_validation_samples.py` 没有真正验证 risky 样本是否通过，也没有验证它是否产生风险提示或确认要求。
2. `memory_update` 当前推荐 `memory_store`，而 `configs/tools.yaml` 中 `memory_store` 是 `read_only + enabled`。这会让“记忆更新”这种潜在写入意图在 dry-run 授权里显示为可执行，权限语义偏松。后续如果接入真实执行，容易误导。

本任务只修复验证覆盖和工具权限语义，不接入 MCP，不执行真实工具。

## 必须先阅读

- `codex-tasks/015-real-task-validation-and-auth-linkage.md`
- `validation/real-task-samples.yaml`
- `configs/tools.yaml`
- `src/ai_test_assistant/orchestrator/nodes.py`
- `tests/test_validation_samples.py`
- `tests/test_orchestrator_smoke.py`
- `src/ai_test_assistant/tool_registry/README.md`
- `docs/current-status.md`

## 修复 1：补齐 risky 样本验证

请在 `tests/test_validation_samples.py` 中补充测试，明确验证 `category: risky` 样本。

要求至少断言：

- risky 样本会被 validation runner 执行。
- risky 样本 `passed is True`，或者如果现有样本预期不合理，则修正样本预期后通过。
- risky 样本实际结果中必须满足以下至少一个：
  - `actual_clarification_required is True`
  - 或 `actual_risk_level` 为 `medium` / `high`
  - 或关联工具授权结果中存在 `allowed=False`

不要只检查样本存在。

## 修复 2：拆分 memory_read 与 memory_write 工具语义

当前 `memory_store` 同时代表读写，但 risk_level 被标为 `read_only`，容易误导。

请调整 `configs/tools.yaml` 与相关映射：

建议：

- 新增或改名为 `memory_read`
  - status: enabled
  - risk_level: read_only
  - 用于读取 memory
- 新增 `memory_write`
  - status: disabled 或 planned
  - risk_level: write_project_files 或 restricted_action（二选一，按当前安全策略选择更保守者）
  - 用于写入 memory / 更新长期记忆

映射建议：

- `test_case_generation` 如需 memory 辅助，推荐 `memory_read`
- `memory_update` 推荐 `memory_write`

不要把 `memory_update` 继续映射到 `read_only` 工具。

## 修复 3：更新测试期望

需要同步更新：

- `validation/real-task-samples.yaml`
- `tests/test_validation_samples.py`
- `tests/test_orchestrator_smoke.py`
- `tests/test_tool_registry.py`
- `tests/test_runtime_cli.py` 如有相关输出断言

要求：

- `test_case_generation` 推荐 `memory_read`，且 read_only enabled 可通过授权评估。
- `memory_update` 推荐 `memory_write`，且默认不可执行或需要确认。
- 仍然不执行真实 memory 写入动作，除非用户显式 `--write-memory` 控制 task_result 记录。

## 修复 4：更新文档

更新：

- `src/ai_test_assistant/tool_registry/README.md`
- `src/ai_test_assistant/orchestrator/README.md`
- `docs/current-status.md`

必须说明：

- memory 读写工具权限已拆分。
- `memory_read` 是只读能力。
- `memory_write` 默认不开放或需要显式授权。
- 当前仍不执行真实工具，不接入 MCP Server。

## 禁止事项

- 不要接入 MCP Server。
- 不要执行本地命令。
- 不要访问外部网络。
- 不要开放真实工具执行。
- 不要把 dry-run 授权评估包装成真实执行。
- 不要引入向量库。
- 不要做 Web UI。

## 验收命令

```bash
pytest
python scripts/run_assistant.py "根据这个需求生成测试用例" --dry-run
python scripts/run_assistant.py "请记住这个输出偏好并更新记忆" --dry-run
python scripts/run_assistant.py "请修改仓库配置并更新工作流" --dry-run
```

## 完成标准

- risky 样本被真实验证，不只是存在。
- memory 读写权限不再混用同一个 read_only 工具。
- memory_update 不再显示为 read_only 默认可执行。
- 所有测试通过。
- 文档状态真实。