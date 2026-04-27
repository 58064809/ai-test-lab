# MCP 使用说明

## 官方来源

- Model Context Protocol 官方文档：https://modelcontextprotocol.io/

## 当前定位

MCP 是用于连接 AI 应用与外部工具、数据源的开放协议。本仓库后续如果要接文件系统、GitHub、浏览器、数据库、命令行等工具，应优先评估 MCP 生态，而不是自研一套工具调用协议。

## 推荐用途

- 文件系统工具
- GitHub 工具
- Playwright 浏览器工具
- 数据库只读查询工具
- 命令行执行工具
- 日志读取工具

## 使用边界

当前仓库没有声明任何 MCP Server 已完成接入。

在真正接入 MCP 前，必须先确认：

1. 目标 MCP Server 是否官方或可信。
2. 是否支持 Windows 环境。
3. 是否需要本地密钥或 token。
4. 是否存在文件写入、命令执行、数据库修改等高风险权限。
5. 是否可以限制为只读或最小权限。

## 待验证事项

- Codex 当前环境是否支持配置 MCP Server。
- Windows 本地是否已安装 Node.js / Python / uv / npx 等运行依赖。
- GitHub、文件系统、Playwright、数据库等 MCP Server 的权限边界。