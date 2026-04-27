# Codex Task 007：底座审查、加固与防止浅实现

## 任务目标

在 001~006 完成后，对个人执行型 AI 测试助手底座进行统一审查和加固。

本任务不是新增大功能，而是检查 Codex 前面是否偷懒、浅实现、伪造已接入能力，确保 memory、intent、orchestrator、tools、runtime 都符合“不造轮子、可运行、可测试、边界清晰”的要求。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/001-foundation.md`
- `codex-tasks/002-memory-foundation.md`
- `codex-tasks/003-intent-router.md`
- `codex-tasks/004-orchestrator-langgraph.md`
- `codex-tasks/005-tool-registry-and-mcp.md`
- `codex-tasks/006-runtime-cli-and-tests.md`
- `docs/tools/sources.md`

## 审查范围

必须审查：

```text
src/ai_test_assistant/
configs/
scripts/
tests/
docs/
```

## 审查清单

### 1. memory

检查：

- 是否真正有持久化 store。
- 是否支持 namespace + key + JSON document。
- 是否有 put/get/search/delete。
- 是否有重新实例化后仍可读取的测试。
- 是否错误地把 AGENTS.md 当成长期记忆数据库。

### 2. intent

检查：

- 是否配置化。
- 是否支持必须的 intent。
- 是否有 confidence。
- 是否有 clarification_required。
- 是否能处理模糊输入。
- 是否把业务规则硬编码进 router。

### 3. orchestrator

检查：

- 是否有明确 state。
- 是否有节点流程。
- 是否支持 dry-run。
- 是否调用 memory 与 intent。
- 是否说明当前是否已使用 LangGraph。
- 是否把 workflow markdown 冒充为真实编排。

### 4. tools

检查：

- 是否有 tool registry。
- 是否有工具状态。
- 是否有风险等级。
- 是否未启用工具不可执行。
- 是否 restricted_action 默认禁止。
- 是否伪造 MCP 已接入。

### 5. runtime

检查：

- CLI 是否可运行。
- --dry-run 是否不执行外部工具。
- --intent-only 是否只做意图识别。
- 输出是否为中文。
- 输出是否包含意图、置信度、记忆摘要、workflow、风险提示、下一步计划。

### 6. tests

检查：

- pytest 是否通过。
- 测试是否覆盖关键行为。
- 测试是否只是检查文件存在。
- 是否有 smoke test。

### 7. docs

检查：

- 是否明确区分已实现、待接入、待验证、受限能力、不做事项。
- 是否把未验证能力写成已完成。
- 是否引用官方来源。

## 必须修复的问题

如果发现以下问题，必须修复：

- 只有 Markdown，没有可运行代码。
- memory 没有持久化。
- intent 没有置信度或澄清机制。
- orchestrator 没有状态和 dry-run。
- tools 没有权限模型。
- CLI 无法运行。
- pytest 无法通过。
- 文档宣称能力已完成但代码没有实现。

## 禁止事项

- 不要新增复杂 Web UI。
- 不要自研 LLM。
- 不要自研 MCP 协议。
- 不要新增向量库作为强依赖。
- 不要写死具体业务。
- 不要为了通过测试而写无意义 mock。

## 验收命令

```bash
pytest
python scripts/run_assistant.py "根据这个需求生成测试用例" --dry-run
python scripts/run_assistant.py "分析这段日志" --intent-only
```

## 输出要求

完成后请更新：

```text
docs/current-status.md
docs/next-steps.md
```

必须说明：

- 已实现能力
- 未实现能力
- 当前限制
- 下一步建议
- 哪些能力仍需接入成熟工具

## 完成标准

- 所有测试通过。
- CLI 可运行。
- 文档状态真实。
- 未伪造任何外部工具接入。
- 底座可以作为后续真实测试任务执行的基础。
