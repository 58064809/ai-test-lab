# AGENTS.md

> 本文件是给 Codex / OpenHands / 其他工程 Agent 读取的项目级工作规则。
> 人类说明文档放在 `README.md`；AI 执行规则、仓库约束、测试规范、输出要求放在本文件。

## 1. 项目定位

本项目不是传统测试平台，也不是团队级平台，更不是为了从零开发一套界面系统。

本项目目标是构建一个个人专用的执行型 AI 测试助手，通过 ChatGPT、Codex、OpenHands、PyCharm、命令行等入口，使用自然语言驱动 AI 完成测试相关工作，包括但不限于：

- 需求分析
- 测试范围分析
- 测试点设计
- 测试用例生成
- 接口测试设计
- 自动化测试脚本编写
- Pytest 测试框架优化
- 日志分析
- 数据库校验
- Redis 校验
- 缺陷定位
- 缺陷报告整理
- 测试报告总结
- 代码审查
- 工程改造建议
- 测试效率提升

核心目标：让 AI 能直接帮我完成测试工程任务，而不是只给建议。

## 2. 核心原则

### 2.1 不造轮子

除非用户明确要求，否则不要自行设计一套新的记忆系统、任务编排系统、知识库系统、自动化平台或 UI 平台。

优先采用工业级通用工具、成熟生态、开源项目、标准协议和已有工程实践。

例如：

- 做 Agent 项目级规则，优先使用 `AGENTS.md`
- 做工程执行，优先考虑 Codex / OpenHands
- 做任务编排，优先考虑 LangGraph / LangGraph Supervisor / CrewAI / LangChain
- 做工具调用，优先考虑 MCP 生态
- 做浏览器自动化，优先考虑 Playwright / Playwright MCP
- 做接口测试生成，优先考虑 Schemathesis
- 做 API 测试与 Mock 生成，优先考虑 Keploy
- 做自动化测试执行，优先使用 Pytest + Allure

### 2.2 当前先做通用架构

当前阶段不要把具体公司、具体电商业务、具体业务规则写死到通用架构里。

业务知识应后置、分层、可插拔、可迁移。未来换公司或换行业时，通用能力仍应可复用。

### 2.3 先小步落地，再逐步增强

当前优先落地：

1. 项目级规则入口：`AGENTS.md`
2. 测试任务提示词与工作流规则
3. 常用输出模板
4. 可执行的测试工具链说明
5. 后续再接入 OpenHands、MCP、LangGraph、Schemathesis、Keploy 等能力

不要一开始就设计复杂平台、复杂 UI、复杂知识库或复杂多 Agent 编排。

### 2.4 遇到阻碍优先解决

如果遇到权限、工具不可用、命令失败、依赖缺失、搜索不可用、环境不一致等阻碍，应优先定位和解决阻碍，不要绕开问题继续堆方案。

处理方式：

1. 明确当前阻碍是什么
2. 给出最小复现或验证命令
3. 判断是环境问题、权限问题、依赖问题、代码问题还是工具能力限制
4. 优先给出可执行修复步骤
5. 修复后再继续原任务

## 3. 工作入口与职责边界

### 3.1 入口层

允许通过以下入口使用本项目：

- ChatGPT
- Codex
- OpenHands
- Claude Code（后置，当前未启用）
- PyCharm
- 命令行
- 其他支持仓库级上下文规则的 Agent 工具

### 3.2 Agent 任务理解层

Agent 接到自然语言任务后，应先判断任务类型：

- 需求分析类
- 测试用例类
- 接口测试类
- UI 自动化类
- 自动化框架优化类
- 日志分析类
- 数据库 / Redis 校验类
- 缺陷定位类
- 报告总结类
- 工程改造类
- 工具接入类

不同任务类型应使用对应的工作方式，不要所有任务都直接写代码。

### 3.3 工具调用层

优先复用成熟工具：

- 文件系统：本地文件读写 / 文件系统 MCP
- GitHub：GitHub MCP / Git CLI
- 浏览器：Playwright / Playwright MCP
- 数据库：数据库 MCP / Python DB Client
- 命令执行：命令行 / Shell / PowerShell
- 自动化测试：Pytest / Playwright / Allure
- 接口测试生成：Schemathesis
- API 测试与 Mock：Keploy

## 4. 当前推荐落地结构

建议仓库先保持轻量结构：

```text
.
├── AGENTS.md
├── README.md
├── prompts/
│   ├── test-case-generation.md
│   ├── requirement-analysis.md
│   ├── log-analysis.md
│   └── bug-report.md
├── workflows/
│   ├── api-test-workflow.md
│   ├── ui-test-workflow.md
│   └── defect-analysis-workflow.md
├── templates/
│   ├── test-case-template.md
│   ├── bug-report-template.md
│   └── test-summary-template.md
├── examples/
│   ├── api-test-example.md
│   ├── pytest-example.md
│   └── log-analysis-example.md
└── tools/
    ├── codex.md
    ├── openhands.md
    ├── playwright-mcp.md
    ├── schemathesis.md
    ├── keploy.md
    └── pytest-allure.md
```

说明：

- `AGENTS.md`：AI Agent 的主入口规则
- `README.md`：给人看的项目说明
- `prompts/`：沉淀高频提示词
- `workflows/`：沉淀可复用任务流程
- `templates/`：沉淀输出模板
- `examples/`：沉淀优秀样例
- `tools/`：记录成熟工具的使用方式

## 5. 暂时不做的事情

当前阶段不要做以下事项，除非用户明确要求：

- 不做自研 memory 系统
- 不做自研知识库
- 不做自研任务编排系统
- 不做团队管理平台
- 不做复杂 UI 页面
- 不做 domains/ecommerce 这种强业务目录
- 不把当前公司的电商业务规则写入通用架构
- 不创建 `.cursor/rules`，除非用户重新启用 Cursor
- 不创建 `CLAUDE.md`，除非用户开始使用 Claude Code
- 不把 `README.md` 当作 AI 核心记忆入口

## 6. 输出规范

### 6.1 默认语言

默认使用中文输出。只有在以下情况才使用英文：

- 代码、命令、配置项、错误日志本身是英文
- 官方工具名、协议名、仓库名必须保持英文
- 用户明确要求英文
- 技术语境中英文表达更准确

### 6.2 Markdown 规范

默认输出 Markdown。

Markdown 应结构清晰、标题层级明确、可直接复制到飞书、GitHub、文档或 IDE 中使用。

### 6.3 测试用例默认格式

如用户要求生成测试用例，默认使用以下表格格式：

| 标题 | 优先级 | 前置条件 | 测试步骤 | 预期结果 |
| --- | --- | --- | --- | --- |

要求：

- 优先级使用 P0、P1、P2、P3
- 不默认增加“用例类型”列
- 不强制一个步骤对应一个预期，允许多对多
- 表格应完整、整齐、可直接复制到飞书或 Excel

### 6.4 代码输出规范

修改代码前应先理解现有结构，不要盲目重构。

优先遵守项目已有风格：

- 保持目录结构一致
- 保持命名风格一致
- 保持日志风格一致
- 保持异常处理风格一致
- 保持测试风格一致

如必须重构，应说明：

1. 为什么需要改
2. 改了什么
3. 影响范围
4. 如何验证

## 7. 测试工程规范

### 7.1 自动化测试优先级

优先考虑以下测试能力：

1. 接口自动化测试
2. 数据库校验
3. Redis 校验
4. 日志分析
5. UI 自动化回归
6. 测试报告与结果归档

不要为了“平台化”而牺牲可执行性。

### 7.2 Pytest 规范

如果涉及 Pytest：

- 优先使用清晰的 fixture
- 公共配置放入 `conftest.py`
- 测试数据与测试逻辑分离
- 断言要可读、可定位
- 日志要能支持失败定位
- 报告优先对接 Allure

### 7.3 接口测试规范

如果涉及接口测试：

- 先分析接口契约、请求参数、响应结构、状态码、鉴权方式
- 再设计正向、反向、边界、权限、幂等、并发、异常场景
- 如存在 OpenAPI 文档，优先考虑 Schemathesis
- 如可基于真实流量生成测试或 Mock，优先考虑 Keploy

### 7.4 UI 自动化规范

如果涉及 UI 自动化：

- 优先考虑高价值稳定场景，不追求全量 UI 覆盖
- 优先覆盖核心链路、冒烟流程、历史高频回归问题
- 选择器应稳定，避免依赖脆弱 XPath
- 如需要 AI 操作浏览器，优先考虑 Playwright MCP

### 7.5 日志分析规范

如果涉及日志分析：

- 先定位错误时间、请求链路、traceId、用户信息、接口路径、异常栈
- 区分业务异常、参数异常、数据异常、依赖异常、环境异常、代码异常
- 输出应包含：问题现象、关键日志、初步原因、验证方式、建议修复方向

## 8. Agent 执行要求

### 8.1 做任务前

Agent 执行任务前应先判断：

- 用户真实目标是什么
- 当前是否需要读文件
- 当前是否需要查官方资料
- 当前是否需要运行命令
- 当前是否会修改代码
- 当前是否存在风险

不要为了显得完整而过度设计。

### 8.2 做任务中

执行过程中应遵守：

- 小步修改
- 可验证
- 不破坏现有结构
- 不引入不必要依赖
- 不擅自改变技术路线
- 遇到阻碍先解决阻碍

### 8.3 做任务后

任务完成后应输出：

1. 完成了什么
2. 修改了哪些文件
3. 如何验证
4. 是否还有遗留问题
5. 下一步建议

## 9. 工具选型优先级

当前认可的工具 / 生态优先级如下：

| 目标 | 优先工具 / 生态 | 当前状态 |
| --- | --- | --- |
| Agent 项目级规则 | AGENTS.md | 优先落地 |
| Codex 项目执行 | OpenAI Codex | 优先推荐 |
| 执行型工程 Agent | OpenHands | 后置接入 |
| 任务编排 | LangGraph / LangGraph Supervisor / CrewAI / LangChain | 后置接入 |
| 工具调用 | MCP 生态 | 后置接入 |
| UI / 浏览器操作 | Playwright / Playwright MCP | 后置接入 |
| 接口测试生成 | Schemathesis | 后置接入 |
| API 测试与 Mock | Keploy | 后置接入 |
| 自动化测试执行 | Pytest + Allure | 持续使用 |
| GitHub Copilot 规则 | `.github/copilot-instructions.md` | 后置 |
| Skills 能力扩展 | Codex Agent Skills / Open Agent Skills | 后置 |

## 10. 重要提醒

本项目的价值不在于目录多、概念多、平台复杂，而在于：

- AI 能理解我的测试任务
- AI 能遵守我的工程规则
- AI 能复用成熟工具
- AI 能产出可执行结果
- AI 能沉淀高质量提示词、流程、模板和样例
- AI 能逐步成为我的个人执行型测试助手
