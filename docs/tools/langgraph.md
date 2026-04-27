# LangGraph 使用说明

## 官方来源

- LangGraph 官方文档：https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph GitHub 仓库：https://github.com/langchain-ai/langgraph

## 当前定位

LangGraph 是面向有状态、长运行 Agent 工作流的编排框架。官方文档将其定位为用于构建可靠、可控、可持久化的 Agent 和多 Agent 系统的低层编排框架。

本仓库后续如果出现真实、稳定、可复用的复杂任务流，例如“读取需求 → 生成用例 → 生成接口脚本 → 执行测试 → 分析报告 → 生成缺陷”，可以再评估 LangGraph。

## 推荐使用场景

- 多步骤任务需要状态管理。
- 任务需要人工确认节点。
- 任务需要失败重试、检查点、恢复执行。
- 多 Agent 或多工具之间需要明确控制流。

## 使用边界

当前仓库没有声明 LangGraph 已完成接入。

不要在没有真实复杂流程前强行引入 LangGraph。

如果只是提示词、模板、单步测试生成、简单文件处理，优先保持 Markdown + Python 脚本 + Codex 执行，不要过早编排。

## 待验证事项

- 是否存在足够稳定的测试任务流程，值得抽象成图。
- 是否需要持久化 checkpoint。
- 是否需要人工确认节点。
- 是否需要和 MCP、Pytest、Allure、GitHub Actions 组合。