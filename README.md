# ai-test-lab

个人执行型 AI 测试助手资产库。

本项目不是传统测试平台，也不是团队协作平台，而是面向个人测试工作的 AI 工作台。目标是在 ChatGPT、Codex、OpenHands、Claude Code、PyCharm、命令行等入口中，通过自然语言完成需求分析、测试设计、接口测试、UI 检查、日志分析、缺陷定位、脚本生成和报告整理。

## 一、项目定位

我要构建的是一个个人专用的执行型 AI 测试助手。

核心目标不是从零开发平台，而是组合成熟工具、成熟框架、AI Agent、Skills、Prompts、MCP、开源项目等能力，形成一个真正能帮我做事的个人测试助手。

理想工作方式：

```text
我提出任务
↓
AI 理解任务类型
↓
AI 自动读取相关上下文
↓
AI 生成执行计划
↓
AI 调用合适工具或技能
↓
AI 执行任务
↓
AI 校验结果
↓
AI 输出可直接使用的结果
```

## 二、当前选择的工业级轮子

### 1. 执行型工程 Agent

- OpenHands
- OpenHands software-agent-sdk

### 2. Agent 编排与应用框架

- LangGraph
- LangGraph Supervisor
- CrewAI
- LangChain

### 3. MCP 工具能力

- 文件系统 MCP
- GitHub MCP
- Playwright MCP
- 数据库 MCP
- 命令行执行 MCP

### 4. 测试专项工具

- Schemathesis
- Keploy
- Pytest
- Allure

### 5. Prompt / Copilot 资产参考

- GitHub awesome-copilot

## 三、第一阶段目标

第一阶段不做平台、不做界面、不做复杂多 Agent 系统。

先完成以下事情：

1. 建立项目资产目录。
2. 固化测试专家 Agent 规则。
3. 固化需求分析、测试用例设计、接口测试、UI 检查、日志分析等核心技能模板。
4. 设计第一个可执行工作流：商家后台商品创建流程检查。
5. 预留 OpenHands、Playwright MCP、Schemathesis、Keploy、Pytest 的接入方式。

## 四、项目目录

```text
ai-test-lab/
├── agents/                 # Agent 角色定义
├── skills/                 # 可复用测试技能
├── workflows/              # 任务工作流
├── memory/                 # 项目记忆与个人偏好
├── tools/                  # 工具接入说明
├── templates/              # 用例、缺陷、报告模板
├── examples/               # 真实任务样例
└── docs/                   # 架构、选型、路线文档
```

## 五、落地原则

- 先资产化，再自动化。
- 先跑通单任务，再考虑多 Agent。
- 先复用成熟轮子，再评估是否需要封装。
- 所有输出默认中文，除非必要才使用英文。
- 所有结果尽量可直接用于测试工作。

## 六、第一个验证场景

场景：检查商家后台商品创建流程有没有问题。

目标工作流：

```text
用户提出任务
↓
AI 读取商家后台商品创建流程规则
↓
AI 使用 Playwright MCP 打开浏览器
↓
AI 登录商家后台
↓
AI 创建商品
↓
AI 截图并记录关键步骤
↓
AI 判断页面、接口、数据是否符合预期
↓
AI 生成测试步骤
↓
AI 发现异常时整理缺陷报告
```
