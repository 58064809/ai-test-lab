# OpenHands 使用说明

## 官方来源

- OpenHands 官方文档：https://docs.openhands.dev/
- OpenHands GitHub 仓库：https://github.com/All-Hands-AI/OpenHands

## 当前定位

OpenHands 是面向软件工程任务的 AI Agent 工具，可用于读写代码、运行命令、修改项目文件和协助完成工程任务。

本仓库后续如果需要更强的本地工程执行能力，可以评估 OpenHands，但当前文件不声明 OpenHands 已完成接入。

## 推荐使用场景

- 让 AI 在仓库内完成较完整的工程改造。
- 运行命令并根据结果继续修改。
- 分析测试失败并修改相关代码或测试。
- 与 GitHub 仓库协同完成任务。

## 使用边界

接入前必须确认：

1. 本地运行环境是否满足 OpenHands 要求。
2. 是否需要 Docker 或其他运行依赖。
3. API Key、模型配置和网络环境是否可用。
4. 文件写入、命令执行、浏览器、网络访问等权限边界。
5. 是否能读取并遵守本仓库 `AGENTS.md`。

## 待验证事项

- Windows 本地是否适合直接运行 OpenHands。
- 是否需要 Docker Desktop。
- 是否与当前 Codex 使用方式冲突。
- 是否应作为后置工程执行入口，而不是当前第一入口。