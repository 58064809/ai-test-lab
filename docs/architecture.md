# 个人执行型 AI 测试助手架构规划

## 一、核心原则

本项目不造轮子。

这里的“不造轮子”指的是：

- 不从零开发 Agent 框架。
- 不从零开发 MCP 协议和工具生态。
- 不从零开发浏览器自动化能力。
- 不从零开发接口测试生成能力。
- 不从零开发测试报告系统。
- 不从零开发完整测试平台或团队协作平台。

本项目只做以下事情：

- 组合成熟工具。
- 配置成熟框架。
- 编排测试工作流。
- 沉淀个人测试规则、提示词、技能和模板。
- 在必要时编写少量胶水代码。
- 把工具能力变成个人可重复使用的测试生产力。

## 二、总体架构

```text
用户自然语言任务
        │
        ▼
任务入口层
ChatGPT / Codex / OpenHands / Claude Code / PyCharm / 命令行
        │
        ▼
任务理解与规划层
测试专家 Agent / Prompt / Skills / 工作流规则
        │
        ▼
任务编排层
LangGraph / LangGraph Supervisor / CrewAI / LangChain
        │
        ▼
工具调用层
MCP 工具集合
文件系统 MCP / GitHub MCP / Playwright MCP / 数据库 MCP / 命令行执行 MCP
        │
        ▼
测试执行层
Pytest / Playwright / Schemathesis / Keploy / Allure
        │
        ▼
结果输出层
测试用例 / 自动化脚本 / 执行日志 / 截图 / 缺陷报告 / 测试总结
        │
        ▼
经验沉淀层
memory / skills / workflows / templates / examples
```

## 三、分层说明

### 1. 任务入口层

负责接收用户的自然语言任务。

候选入口：

- ChatGPT
- Codex
- OpenHands
- Claude Code
- PyCharm
- 命令行

第一阶段优先使用现成入口，不开发新界面。

### 2. 任务理解与规划层

负责把用户的一句话变成可执行计划。

例如：

```text
用户：帮我分析这个需求要怎么测
AI：识别需求类型 → 拆分业务规则 → 提取测试范围 → 生成测试点 → 生成测试用例
```

核心资产：

- 测试专家 Agent 定义
- 需求分析 Skill
- 用例设计 Skill
- 接口测试 Skill
- UI 检查 Skill
- 日志分析 Skill
- 缺陷报告 Skill

### 3. 任务编排层

负责多步骤任务的流程控制。

候选轮子：

- LangGraph：适合做状态机式任务编排。
- LangGraph Supervisor：适合后续多 Agent 管理。
- CrewAI：适合角色协作型任务。
- LangChain：适合作为 LLM 应用基础组件。

第一阶段不急着做复杂多 Agent，优先使用文档化工作流和现成工具入口。

### 4. 工具调用层

通过 MCP 或现成工具，让 AI 能调用外部能力。

优先工具：

- 文件系统 MCP：读取项目文件、写入测试资产。
- GitHub MCP：读取仓库、提交代码、创建 Issue、辅助代码审查。
- Playwright MCP：打开浏览器、操作页面、截图、检查 UI 流程。
- 数据库 MCP：查询业务数据、校验落库结果。
- 命令行执行 MCP：运行 Pytest、Schemathesis、脚本和本地命令。

### 5. 测试执行层

使用成熟测试工具执行真实测试任务。

候选轮子：

- Pytest：作为 Python 自动化测试基础框架。
- Playwright：作为 Web UI 自动化基础框架。
- Schemathesis：基于 OpenAPI 做接口契约测试和模糊测试。
- Keploy：基于真实流量或调用生成 API 测试和 Mock。
- Allure：测试报告展示。

### 6. 结果输出层

统一输出为可直接使用的测试成果。

常见输出：

- 需求分析结论
- 测试范围
- 测试点
- 测试用例表格
- Pytest 自动化脚本
- Playwright 自动化脚本
- 接口测试脚本
- 数据库校验 SQL
- Redis 校验步骤
- 日志分析结论
- 缺陷报告
- 测试总结

### 7. 经验沉淀层

把可复用经验沉淀下来，避免每次重新解释。

沉淀内容：

- 项目记忆
- 个人偏好
- 测试模板
- 常用工作流
- 常用 Prompt
- 常用 Skill
- 电商业务规则
- 自动化框架规范
- 缺陷报告模板

## 四、推荐目录结构

```text
ai-test-lab/
├── README.md
├── agents/
│   ├── test-expert-agent.md
│   ├── api-test-agent.md
│   ├── ui-test-agent.md
│   ├── log-analysis-agent.md
│   └── code-review-agent.md
│
├── skills/
│   ├── requirement-analysis.md
│   ├── testcase-design.md
│   ├── api-test-design.md
│   ├── pytest-generation.md
│   ├── ui-check.md
│   ├── log-analysis.md
│   ├── db-validation.md
│   └── defect-report.md
│
├── workflows/
│   ├── requirement-to-testcases.md
│   ├── openapi-to-api-tests.md
│   ├── ui-flow-check.md
│   ├── log-to-defect-report.md
│   └── pytest-run-and-summary.md
│
├── memory/
│   ├── project-memory.md
│   ├── user-preferences.md
│   ├── ecommerce-domain.md
│   └── testing-rules.md
│
├── tools/
│   ├── openhands.md
│   ├── langgraph.md
│   ├── langchain.md
│   ├── crewai.md
│   ├── mcp-filesystem.md
│   ├── mcp-github.md
│   ├── mcp-playwright.md
│   ├── mcp-database.md
│   ├── mcp-command-line.md
│   ├── schemathesis.md
│   ├── keploy.md
│   └── pytest-allure.md
│
├── templates/
│   ├── testcase-table.md
│   ├── defect-report.md
│   ├── test-summary.md
│   ├── api-testcase.md
│   └── log-analysis-report.md
│
├── examples/
│   ├── requirement-analysis-example.md
│   ├── testcase-design-example.md
│   ├── api-test-example.md
│   ├── ui-check-example.md
│   └── log-analysis-example.md
│
└── docs/
    ├── architecture.md
    ├── roadmap.md
    ├── tool-selection.md
    └── integration-plan.md
```

## 五、第一阶段落地路线

### 阶段 1：资产库初始化

目标：先把项目变成可用的个人 AI 测试资产库。

产物：

- README.md
- docs/architecture.md
- docs/tool-selection.md
- docs/roadmap.md
- agents/test-expert-agent.md
- skills/testcase-design.md
- templates/testcase-table.md
- templates/defect-report.md

### 阶段 2：测试专家能力沉淀

目标：先让 AI 稳定输出高质量测试成果。

重点能力：

- 需求分析
- 测试点设计
- 测试用例生成
- 缺陷报告整理
- 日志分析
- 数据库校验思路

### 阶段 3：接入现成执行工具

目标：让 AI 从“会写”变成“能执行”。

优先接入：

- OpenHands
- GitHub MCP
- 文件系统 MCP
- 命令行执行 MCP

### 阶段 4：接入测试专项工具

目标：让 AI 能跑测试、生成测试、分析结果。

优先接入：

- Pytest
- Allure
- Schemathesis
- Keploy
- Playwright MCP

### 阶段 5：沉淀真实业务工作流

目标：把高频测试任务变成标准流程。

候选工作流：

- 需求文档 → 测试点 → 测试用例
- OpenAPI → 接口测试 → 测试报告
- UI 流程 → Playwright 检查 → 截图 → 缺陷报告
- 日志文本 → 根因分析 → 缺陷报告
- Pytest 执行结果 → 失败原因分析 → 修复建议

## 六、我当前建议的最小可行版本

不要一开始做大而全。

最小可行版本只做 5 件事：

```text
1. 一个测试专家 Agent
2. 三个核心 Skill：需求分析、用例设计、缺陷报告
3. 两个模板：测试用例表格、缺陷报告
4. 三个工具说明：OpenHands、Playwright MCP、Schemathesis
5. 一个真实样例：从需求到用例
```

这个版本完成后，ai-test-lab 就能开始被 ChatGPT、Codex、OpenHands 或 PyCharm 中的 AI 读取和使用。

## 七、暂不做的事情

为了避免重新造轮子，暂时不做：

- 不做 Web 管理后台。
- 不做团队权限系统。
- 不做自研 Agent 框架。
- 不做自研 MCP 协议。
- 不做自研浏览器自动化引擎。
- 不做自研测试报告系统。
- 不做复杂任务调度平台。
- 不做完整知识库平台。

## 八、判断是否偏离方向的标准

如果一个需求会导致大量开发底层能力，就先停下来判断有没有现成轮子。

判断标准：

| 问题 | 如果答案是“是” | 处理方式 |
|---|---|---|
| 有没有成熟开源工具能做？ | 是 | 优先接入工具 |
| 是不是测试工作高频场景？ | 是 | 沉淀为 Skill 或 Workflow |
| 是不是只为好看而做界面？ | 是 | 暂不做 |
| 是不是需要大量平台开发？ | 是 | 暂不做 |
| 是不是能通过 Prompt + MCP + 现成工具解决？ | 是 | 不写新系统 |

## 九、最终形态

最终的 ai-test-lab 应该是一个个人 AI 测试工作台资产库。

它不一定自己运行成一个平台，但它能被 ChatGPT、Codex、OpenHands、Claude Code、PyCharm、命令行工具读取和使用。

最终使用方式类似：

```text
我：根据这个需求生成测试用例
AI：读取 skills/testcase-design.md 和 templates/testcase-table.md，输出用例表格

我：根据这个 OpenAPI 生成接口测试
AI：读取 tools/schemathesis.md 和 workflows/openapi-to-api-tests.md，生成执行命令和测试方案

我：分析这段日志为什么下单失败
AI：读取 skills/log-analysis.md 和 templates/log-analysis-report.md，输出根因分析

我：帮我检查这个页面流程
AI：读取 tools/mcp-playwright.md 和 workflows/ui-flow-check.md，打开浏览器执行检查
```
