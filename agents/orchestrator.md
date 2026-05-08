# Orchestrator

## 职责

负责识别任务类型、组织上下文、选择主 Agent / Skill、协调工具调用边界，并汇总输出结果。

## 当前状态

当前 runtime 只有最小 LangGraph dry-run orchestrator，用于计划生成、风险提示和工具授权评估。它不是复杂多 Agent 平台。

## 主要输入

- 用户自然语言任务
- 配置化 intent 规则
- tool registry 权限状态
- 显式只读文件输入
- 受控 pytest / Allure 执行结果

## 主要输出

- 识别出的 intent
- 推荐 workflow / skill
- 风险等级
- 推荐工具和授权状态
- 执行计划或结果摘要

## 关联资产

- `src/ai_test_assistant/orchestrator/`
- `configs/intents.yaml`
- `configs/tools.yaml`

## 边界

- 不默认启用全部 Agent。
- 不绕过 tool registry。
- 不开放 `shell`、`filesystem_write`、`github_write`。
- 不自研复杂 workflow engine；如需增强，优先评估 LangGraph 成熟能力。
