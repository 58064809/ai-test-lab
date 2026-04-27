# Next Steps

## 建议顺序

1. 先用真实任务验证 memory 是否足够支撑 `intent` 读取项目规则和用户偏好。
2. 再实现 `intent` 路由层，直接调用 `MemoryService` 读取 `project_rule` 和 `user_preference`。
3. 之后再评估是否有必要引入 LangGraph 做编排。

## 待接入项

- 待接入：`intent` 规则配置和路由结果模型
- 待接入：`orchestrator` 最小状态流
- 待接入：工具注册和权限模型
- 待接入：runtime CLI

## 风险提醒

- 如果后续没有真实复杂流程，不应为了完整感提前引入 LangGraph。
- 如果后续只需要结构化查询，不应过早引入向量库。
