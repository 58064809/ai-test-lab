# Playwright MCP 使用说明

## 官方来源

- Playwright MCP 官方仓库：https://github.com/microsoft/playwright-mcp
- Playwright 官方文档：https://playwright.dev/

## 当前定位

Playwright MCP 是 Microsoft 官方维护的 MCP Server，用于让 AI Agent 通过浏览器可访问性快照进行自动化操作。官方仓库说明中明确提到，它不依赖截图或视觉模型，而是使用结构化可访问性快照。

本仓库后续如果需要让 AI 操作浏览器、分析页面、执行 UI 冒烟流程，应优先评估 Playwright MCP，而不是自研浏览器控制层。

## 推荐使用场景

- AI 辅助浏览器操作。
- UI 冒烟流程验证。
- 页面交互问题复现。
- 前端回归检查。
- 结合 Codex / OpenHands 执行浏览器任务。

## 使用边界

当前仓库没有声明 Playwright MCP 已完成接入。

接入前必须确认：

1. 当前 Agent 入口是否支持 MCP Server。
2. Windows 本地是否安装 Node.js / npx。
3. 浏览器启动权限是否正常。
4. 是否涉及账号登录、支付、发券、下单等高风险操作。
5. 是否需要测试环境账号与隔离数据。

## 待验证事项

- Codex 或其他 Agent 是否能加载 Playwright MCP。
- Windows 本地是否能运行 Playwright MCP。
- 是否需要与 Pytest Playwright 分开管理。
- UI 任务的安全边界和账号权限。