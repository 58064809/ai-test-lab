# MCP 安全策略

## L0: no_tool

- 可做什么：仅推理、计划、澄清、风险评估
- 禁止什么：任何真实工具调用
- 是否需要确认：否
- 是否允许 dry-run：是
- 是否允许默认启用：是
- 适用工具示例：无

## L1: read_only

- 可做什么：只读本地元数据、只读 memory、只读配置
- 禁止什么：写文件、外网访问、命令执行
- 是否需要确认：通常否
- 是否允许 dry-run：是
- 是否允许默认启用：可以，但只限低风险只读能力
- 适用工具示例：`memory_read`、`intent_router`

## L2: read_project_files

- 可做什么：只读仓库文件
- 禁止什么：写仓库文件、读写真实业务敏感文件、外网访问、命令执行
- 是否需要确认：建议是
- 是否允许 dry-run：是
- 是否允许默认启用：否
- 适用工具示例：`filesystem_read`

## L3: write_project_files

- 可做什么：修改仓库内工程文件
- 禁止什么：写真实业务文件、越权写系统目录
- 是否需要确认：是，必须 human confirmation
- 是否允许 dry-run：是
- 是否允许默认启用：否
- 适用工具示例：`filesystem_write`

## L4: external_network

- 可做什么：访问 GitHub、浏览器远端资源、未来只读远端接口
- 禁止什么：默认外网访问、默认远端写操作
- 是否需要确认：是
- 是否允许 dry-run：是
- 是否允许默认启用：否
- 适用工具示例：`github_read`、`github_write`、`playwright_browser`

## L5: execute_local_command

- 可做什么：运行本地命令
- 禁止什么：默认执行任何本地命令
- 是否需要确认：是
- 是否允许 dry-run：否，dry-run 只允许评估风险
- 是否允许默认启用：否
- 适用工具示例：`shell`、`pytest_runner`

## L6: restricted_business_action

- 可做什么：只有在高权限确认后才能执行的高风险业务动作
- 禁止什么：支付、下单、发券、删数据、敏感写操作的默认执行
- 是否需要确认：是，必须 human confirmation
- 是否允许 dry-run：是，但只能输出计划和风险
- 是否允许默认启用：否
- 适用工具示例：`memory_write`、`keploy`

## 全局约束

- shell 永远不能默认 `enabled`
- filesystem write 不能默认 `enabled`
- GitHub write 不能默认 `enabled`
- database / redis 第一阶段只允许 readonly
- Playwright MCP 第一阶段不允许执行真实支付、下单、发券、删数据等动作
- 所有高风险动作必须 human confirmation
- 当前仓库只允许 dry-run 级风险评估，不开放 MCP 真实执行入口
