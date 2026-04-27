# Codex Task 005：实现 tools 工具注册与 MCP 接入边界

## 任务目标

实现个人 AI 测试助手的工具注册表和权限模型，为后续 MCP、Pytest、Playwright MCP、Schemathesis、Keploy 等工具接入打底。

这不是让你自研 MCP 协议，也不是让你假装已经接入所有工具。当前目标是建立清晰、可测试、可扩展的工具注册和权限边界。

## 官方依据

优先参考：

- MCP 官方文档中的 tools / resources / prompts 概念。
- MCP 的权限、参数校验、资源访问控制和能力协商思想。
- Playwright MCP 官方仓库。
- Pytest / Allure 官方文档。
- Schemathesis / Keploy 官方文档。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/001-foundation.md`
- `docs/tools/mcp.md`
- `docs/tools/playwright-mcp.md`
- `docs/tools/pytest-allure.md`
- `docs/tools/schemathesis.md`
- `docs/tools/keploy.md`
- `docs/tools/sources.md`

## 实现范围

请实现：

```text
src/ai_test_assistant/tool_registry/
  __init__.py
  models.py
  registry.py
  permissions.py
  README.md

configs/tools.yaml

tests/test_tool_registry.py
```

## 工具状态

工具必须有状态：

- enabled：已启用
- disabled：已禁用
- planned：计划接入
- unavailable：当前环境不可用

## 风险等级

工具必须有风险等级：

- read_only
- write_project_files
- execute_local_command
- external_network
- restricted_action

## 第一批工具注册项

至少注册以下工具，但不要假装都已实现：

- memory_store
- intent_router
- pytest_runner
- allure_report
- playwright_mcp
- schemathesis
- keploy
- github
- filesystem
- shell
- database_readonly
- redis_readonly

## 权限策略

要求：

1. read_only 可默认允许。
2. write_project_files 需要明确允许。
3. execute_local_command 默认 dry-run 下禁止执行。
4. external_network 默认需要确认。
5. restricted_action 默认禁止。
6. 未启用工具不可执行。

## MCP 边界

必须明确：

- 不实现自研 MCP 协议。
- 当前只做 MCP server 的注册和接入规划。
- 真实 MCP 接入放到后续任务。
- Playwright MCP、文件系统 MCP、GitHub MCP、数据库 MCP 都必须按官方或可信实现接入。

## 禁止事项

- 不要自研 MCP 协议。
- 不要让工具默认拥有高风险权限。
- 不要把 planned 工具写成 enabled。
- 不要在测试中执行真实外部副作用。
- 不要写死公司业务动作。

## 验收命令

```bash
pytest tests/test_tool_registry.py
```

## 完成标准

- 工具注册表可加载。
- 工具状态和风险等级可查询。
- 未启用工具不可执行。
- restricted_action 默认禁止。
- README 说明当前只是工具注册和权限底座，不是完整 MCP 接入。
