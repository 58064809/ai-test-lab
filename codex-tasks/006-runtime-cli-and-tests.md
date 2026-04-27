# Codex Task 006：实现 runtime CLI 与测试验收底座

## 任务目标

实现个人 AI 测试助手的最小运行入口和测试验收体系。

这不是让你做 Web 平台，也不是让你做复杂 UI。当前目标是提供一个能在本地命令行运行的入口，用来验证 memory、intent、orchestrator、tool registry 是否能串起来。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/001-foundation.md`
- `codex-tasks/002-memory-foundation.md`
- `codex-tasks/003-intent-router.md`
- `codex-tasks/004-orchestrator-langgraph.md`
- `codex-tasks/005-tool-registry-and-mcp.md`
- `tools/pytest-allure.md`

## 实现范围

请实现：

```text
src/ai_test_assistant/runtime/
  __init__.py
  cli.py
  output.py
  README.md

scripts/run_assistant.py

tests/test_runtime_cli.py
```

## CLI 参数

必须支持：

- task_text：用户自然语言任务
- --dry-run：只输出计划，不执行工具
- --intent-only：只做意图识别
- --write-memory：允许写入任务结果记忆
- --config：指定配置文件路径

## 输出要求

默认中文输出。

输出至少包含：

- 原始任务
- 识别意图
- 置信度
- 是否需要澄清
- 读取到的记忆摘要
- 推荐 workflow
- 工具风险提示
- 下一步计划

## 安全要求

- 默认 dry-run 不执行外部工具。
- 默认不执行本地命令。
- 默认不访问外部网络。
- 默认不修改业务文件。
- 如果任务需要高风险动作，只输出提示和确认要求。

## 测试要求

至少覆盖：

1. CLI 可以启动。
2. --intent-only 只输出意图识别结果。
3. --dry-run 输出任务计划。
4. 模糊任务返回澄清提示。
5. 未启用工具不会被执行。

## 验收命令

```bash
pytest
python scripts/run_assistant.py "根据这个需求生成测试用例" --dry-run
python scripts/run_assistant.py "分析这段日志" --intent-only
```

## 禁止事项

- 不要做 Web UI。
- 不要绕过 orchestrator 直接输出结果。
- 不要在 dry-run 中执行真实命令。
- 不要把测试写成只检查文件存在。
- 不要伪造工具已经接入。

## 完成标准

- `pytest` 通过。
- CLI 可运行。
- CLI 能串联 intent、memory、orchestrator、tool registry。
- 文档说明当前 runtime 的能力边界。