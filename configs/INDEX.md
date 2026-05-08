# configs

`configs/` 只放 runtime 可读取的配置，不放业务规则、不放模板、不放外部资料。

## 目录分层

- `runtime/`：入口装配配置，例如 memory backend、intent rules 路径、tool registry 路径。
- `routing/`：自然语言任务意图路由规则。
- `registry/`：受控工具注册表、工具状态、风险等级和授权条件。
- `mcp/`：MCP server 示例配置。

## 边界

- 不在配置中开放 shell。
- 不在配置中开放 filesystem_write。
- 不在配置中开放 github_write。
- 不把公司业务规则写进通用配置。
- 新增工具必须先进入 `configs/registry/tools.yaml` 并声明状态、风险等级、授权条件和验证方式。
