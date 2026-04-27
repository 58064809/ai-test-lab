# Codex 使用说明

## 官方来源

- OpenAI Codex 介绍：https://openai.com/index/introducing-codex/
- OpenAI Codex AGENTS.md 文档：https://github.com/openai/codex/blob/main/docs/agents_md.md
- OpenAI Codex CLI 仓库：https://github.com/openai/codex

## 当前定位

Codex 是当前优先推荐的工程执行入口。它适合读取仓库上下文、理解任务、修改文件、运行命令、解释变更和协助测试工程改造。

本仓库已经落地 `AGENTS.md`，用于给 Codex 提供项目级规则、测试输出规范、工具选型原则和执行边界。

## 使用边界

Codex 可以帮助执行工程任务，但不应被要求自研 memory、知识库、任务编排系统或测试平台。

当任务涉及仓库修改时，Codex 应先读取 `AGENTS.md`，再读取相关目录文件，最后进行小步可验证修改。

## 建议任务示例

```text
阅读 AGENTS.md，根据 agent-assets/prompts/test-case-generation.md，为这个需求生成测试用例。
```

```text
阅读 agent-assets/workflows/api-test-workflow.md，基于当前 OpenAPI 文档设计接口测试方案。
```

```text
阅读 docs/tools/schemathesis.md，判断当前项目是否适合接入 Schemathesis，并给出验证步骤。
```

## 待验证事项

- 在本地 PyCharm / Codex 环境中确认 Codex 是否稳定读取仓库根目录 `AGENTS.md`。
- 确认 Codex 执行命令、修改文件、提交变更的权限边界。
- 确认 Windows 环境下命令执行路径和 shell 行为。
