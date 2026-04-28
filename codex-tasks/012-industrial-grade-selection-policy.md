# Codex Task 012：工业级成熟方案选型约束

## 任务背景

当前仓库已经完成 memory 与 intent router 的最小底座。

其中 intent router 当前是 bootstrap / fallback 级别的规则路由，不应被包装成最终工业级意图系统。

后续正式实现 orchestrator、tool registry、MCP、runtime CLI、测试执行层、报告层时，必须优先复用工业级成熟方案，而不是手写一套看起来合理的系统。

本任务只新增选型约束和后续任务执行规则，不实现业务功能。

## 最高原则

1. 不造轮子。
2. 正式能力优先使用成熟生态、成熟框架、成熟协议、成熟开源项目。
3. 不限定必须官方；如果官方方案不合适，可以选择 GitHub 高 star、维护活跃、社区成熟、文档完整的开源方案。
4. 只有在没有合适成熟方案、或成熟方案明显过重时，才允许写最小胶水层 / adapter / fallback。
5. 自写 fallback 必须明确标注为临时方案，不得包装成最终工业级能力。
6. 不把当前公司的电商业务写进通用底座。
7. 不把未验证能力写成已完成。

## 适用范围

后续所有正式模块都必须遵守本约束，包括但不限于：

- orchestrator / 任务编排
- memory / 长期记忆
- intent / 意图识别
- tool registry / 工具注册
- MCP / 工具协议接入
- runtime CLI / 执行入口
- Pytest / 测试执行
- Playwright / 浏览器自动化
- Schemathesis / 接口契约测试
- Keploy / API 测试与 Mock
- Allure / 测试报告
- GitHub / 文件与代码仓库操作

## 工业级方案选择标准

选择任何正式依赖或方案前，必须先评估：

1. 是否是官方或主流生态方案。
2. GitHub star 数量是否较高。
3. 最近是否仍在维护。
4. issue / PR 活跃度是否正常。
5. 文档是否完整。
6. Python / Windows 支持是否明确。
7. 是否适合个人本地执行型 AI 测试助手。
8. 是否会引入过重的服务依赖。
9. 是否存在明显安全风险。
10. 是否能与当前 `src/ai_test_assistant/` 工程结构集成。

## 选型说明要求

后续每个正式模块在实现前，必须在对应 README 或 docs 中给出选型说明，至少包含：

```text
候选方案：
选择结果：
选择理由：
未选择方案及原因：
当前接入状态：
风险与限制：
后续替换策略：
```

## fallback 规则

如果当前阶段使用自写轻量实现，只能作为 fallback 或 bootstrap。

必须满足：

- 命名或文档中明确说明是 fallback / bootstrap。
- 不继续扩展成复杂自研系统。
- 一旦需求复杂度升高，优先替换为成熟方案。
- 测试必须覆盖其边界。
- README / current-status 必须说明它不是最终工业级能力。

例如：

- 当前 `intent router` 是规则路由 fallback，不是最终语义意图系统。
- 如果后续需要更复杂意图识别，应优先评估 LangChain / LangGraph / Pydantic structured output / function calling / 其他成熟分类方案，而不是继续手搓复杂 scoring。

## 后续模块强制要求

### orchestrator

正式任务编排优先评估：

- LangGraph
- LangGraph Supervisor
- CrewAI
- LangChain Runnable / Agent 生态

不得直接手写复杂状态机作为最终方案。

如果暂不引入 LangGraph，必须说明原因，并保持接口可替换。

### tool registry / MCP

正式工具调用优先评估：

- MCP 官方协议
- 官方或高质量 MCP Server
- GitHub MCP
- Filesystem MCP
- Playwright MCP
- 数据库只读 MCP
- Shell / command 执行类成熟工具

不得自研 MCP 协议。

### runtime CLI

正式 CLI 优先评估：

- Typer
- Click
- argparse

简单阶段可用 argparse，但如果 CLI 复杂度上升，应优先迁移 Typer 或 Click。

### 数据模型与校验

正式配置和结构化输出优先评估：

- Pydantic
- dataclasses + 明确校验

如果字段、schema、配置变复杂，应优先使用 Pydantic，不要继续手写大量校验。

### 测试执行层

正式测试执行优先复用：

- Pytest
- Allure Pytest
- Playwright
- Schemathesis
- Keploy

不得自研测试执行框架、报告框架、接口测试生成器。

## 禁止事项

- 不要自研 Agent 框架。
- 不要自研任务编排框架。
- 不要自研 MCP 协议。
- 不要自研向量数据库。
- 不要自研接口测试生成器。
- 不要自研浏览器自动化框架。
- 不要自研测试报告系统。
- 不要把 fallback 包装成工业级方案。
- 不要用“当前够用”作为长期自研理由。

## 需要更新的仓库文件

请后续任务在适当时机更新：

- `README.md`
- `docs/current-status.md`
- `docs/next-steps.md`
- 各模块 README
- 对应 `codex-tasks/*.md`

必须明确：

- 哪些是正式成熟方案。
- 哪些是 fallback。
- 哪些只是待接入。
- 哪些能力仍未验证。

## 与已有任务的关系

本任务不是替代 004、005、006，而是作为它们的前置约束。

后续执行顺序建议：

1. 完成并确认本选型约束。
2. 进入 `004-orchestrator-langgraph.md`。
3. 在 004 中正式评估 LangGraph / LangGraph Supervisor / CrewAI / LangChain。
4. 进入 `005-tool-registry-and-mcp.md`。
5. 在 005 中正式评估 MCP 工具生态。
6. 进入 `006-runtime-cli-and-tests.md`。

## 验收标准

本任务完成后，Codex 后续实现任何正式模块时，都必须先回答：

```text
我是否在复用成熟方案？
如果没有，为什么？
当前自写部分是正式能力还是 fallback？
有没有替换为成熟方案的路径？
是否把未验证能力写成已完成？
```

如果回答不清楚，不允许继续实现。