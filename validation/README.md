# 真实任务样本说明

本目录用于沉淀通用测试工程任务样本，验证当前底座在真实自然语言输入上的表现。

## 目标

- 验证 `IntentRouter` 的规则路由是否稳定
- 验证 `TaskOrchestrator` 的 dry-run 计划是否可用
- 验证 tool registry 授权联动是否能给出风险提示

## 边界

- 不包含敏感数据
- 不包含真实账号、地址、token、数据库信息
- 不执行任何真实工具
- 不访问外部网络
- 不调用 MCP Server

## 文件

- `real-task-samples.yaml`：真实任务样本集

