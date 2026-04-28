# Validation 模块说明

## 当前状态

当前模块已实现 **真实任务样本 dry-run 验证器**。

它只做两件事：

- 读取 `validation/real-task-samples.yaml`
- 调用现有 `IntentRouter` 与 `TaskOrchestrator` 做 dry-run 验证

## 已实现

- 通用测试工程样本加载
- 样本逐条 dry-run 验证
- 意图、澄清、workflow、风险等级、推荐工具、授权结果检查

## 当前限制

- 当前不执行真实工具
- 当前不访问外部网络
- 当前不执行本地命令
- 当前不接入 MCP Server
- 当前不做语义评测或向量召回

## 明确不做

- 不把样本验证器包装成 benchmark 平台
- 不把 dry-run 结果误写成真实执行结果
