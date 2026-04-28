# Runtime 模块说明

## 当前状态

当前模块已实现 **最小 runtime CLI**。

本阶段选择 `argparse`，原因是：

- 当前参数集很小
- 标准库即可满足
- 不需要为最小 CLI 额外引入 Typer / Click 依赖

如果后续 CLI 复杂度明显上升，再评估迁移到 Typer 或 Click。

## 已实现

- 命令行参数：
  - `task_text`
  - `--dry-run`
  - `--intent-only`
  - `--write-memory`
  - `--read-file`
  - `--mcp-read-file`
  - `--run-pytest`
  - `--show-file-content`
  - `--config`
- `--intent-only` 只做意图识别
- 非 `--intent-only` 走当前 `TaskOrchestrator` 的最小能力
- 默认中文输出
- 默认不执行外部工具、不执行本地命令、不访问外部网络
- 默认不写入 `task_result/orchestrator` 记忆
- 只有传 `--write-memory` 才允许写入 `task_result/orchestrator`
- `--intent-only` 始终不写入 `task_result` 记忆
- 只有显式传 `--read-file` 才允许单文件读取
- 只有显式传 `--mcp-read-file` 才允许通过 filesystem MCP 读取单文件
- 只有显式传 `--run-pytest` 才允许执行受控 pytest
- `--read-file` 只支持仓库相对路径、白名单文本文件，且必须经过 `FilesystemReadPolicy`
- `--mcp-read-file` 只支持仓库相对路径、白名单文本文件，且必须经过 `FilesystemReadPolicy`
- `--run-pytest` 只支持仓库内相对路径 target，默认 target 为 `tests`
- `--read-file` 使用本地 fallback `LocalFilesystemReadAdapter`
- `--mcp-read-file` 使用 `FilesystemMcpReadClient` + `@modelcontextprotocol/server-filesystem`
- `--run-pytest` 使用 `PytestRunner` 执行 `sys.executable -m pytest <target>`
- 默认只展示文件预览，不完整打印
- 只有显式传 `--show-file-content` 才展示完整允许内容
- pytest 输出为结构化结果，不开放任意命令执行
- dry-run 输出包含工具授权风险提示：
  - 推荐工具
  - 工具状态
  - 风险等级
  - 是否允许执行
  - 是否需要确认
  - 拒绝原因

## 当前限制

- 当前不实现 runtime CLI 之外的执行器
- 当前只接入 `filesystem_mcp_read` 这一个显式只读 MCP 入口
- 当前已接入 `pytest_runner` 最小真实执行能力，但它不是 shell 通用执行
- 当前不执行写文件或 shell 类真实工具
- 当前不访问外部网络
- 当前不执行本地命令
- 当前 `--write-memory` 只控制 `task_result/orchestrator` 写入，不影响其他 memory 类型
- 当前 tool 风险提示来自 dry-run 授权评估，不代表已经接入真实执行器
- 当前 `--read-file` 与 `--mcp-read-file` 都只支持显式单文件读取，不自动根据自然语言猜测多个文件
- 当前 `--run-pytest` 不支持 Allure、不支持额外 pytest 参数、不支持仓库外路径
- 当前文件读取结果会进入 orchestrator dry-run 上下文，但 task_result memory 不保存完整文件内容
- 当前不支持目录读取、glob、多文件读取或自动上下文收集

## 待接入

- 更细粒度的 memory write 控制
- 与 tool registry 的正式执行联动
- CLI 更丰富的输出格式
- 后续如参数复杂度提升，再评估 Typer / Click

## 明确不做

- 不做 Web UI
- 不绕过 orchestrator 伪装成真实执行入口
- 不在 dry-run 中执行真实命令
