# 本地环境前置条件

## 必装工具

Windows 本地要完成当前仓库的基础开发、测试和 filesystem MCP 最小验证，至少需要：

- `Git`
- `Python`
- `pytest`
- `Node.js`
- `npm`
- `npx`

## 可选工具

- `nvm-windows`

说明：

- `nvm-windows` 是可选，不是必装。
- 如果本机已经有可用的 `Node.js` LTS，当前不需要额外安装 `nvm-windows`。
- 只有在 `node -v` 不存在、版本混乱或需要并行维护多个 Node 版本时，再考虑安装 `nvm-windows`。

## 版本检查命令

```powershell
git --version
python --version
pytest --version
node -v
npm -v
npx -v
```

只要这些命令能正常输出版本号，就说明对应工具已可用。

当前已完成的本地验证结果：

- `node -v`：`v24.15.0`
- `npm -v`：`11.12.1`
- `npx -v`：`11.12.1`

## Windows 安装建议

- `Git`：安装官方 Windows 版本
- `Python`：安装当前项目可用的 Python 版本，并确保命令行可直接使用 `python`
- `pytest`：在当前 Python 环境内安装，不要跨环境混装
- `Node.js`：优先安装 LTS 版本
- `npm` / `npx`：通常随 `Node.js` 一起提供

## filesystem MCP 最小启动命令

当前采用官方 / 主流方案：

```powershell
npx -y @modelcontextprotocol/server-filesystem <ABSOLUTE_PATH_TO_AI_TEST_LAB>
```

如果已经进入仓库根目录，也可以直接执行：

```powershell
npx -y @modelcontextprotocol/server-filesystem .
```

当前已完成的本地验证结果：

- 命令：`npx -y @modelcontextprotocol/server-filesystem .`
- 输出：`Secure MCP Filesystem Server running on stdio`

说明：

- `configs/mcp/filesystem-server.example.json` 中仍应保留 `<ABSOLUTE_PATH_TO_AI_TEST_LAB>` 占位符，不要写死用户本地路径。
- `.` 只适合在当前工作目录已经是仓库根目录时使用。
- 第一阶段只验证 read 能力，不开放 `filesystem_write`。
- 不读取 `.env`、`.git/`、`.assistant/` 等敏感内容。

## 失败时怎么处理

优先按下面顺序排查：

1. `git --version` 是否可运行。
2. `python --version` 是否可运行。
3. `pytest --version` 是否可运行。
4. `node -v`、`npm -v`、`npx -v` 是否可运行。
5. `npx -y @modelcontextprotocol/server-filesystem <ABSOLUTE_PATH_TO_AI_TEST_LAB>` 或 `npx -y @modelcontextprotocol/server-filesystem .` 是否因为网络、npm 源、路径或当前目录不正确而失败。

如果 `pytest` 不存在，应根据当前项目依赖文件补装，不要猜测包名或跨环境安装。

## Codex 可自动修复的范围

- 补充文档
- 补充配置模板
- 明确需要运行的本地检查命令
- 解释失败原因和下一步排查方向
- 在项目依赖文件明确存在时，给出 `pytest` 的安装命令

## 需要用户手动处理的范围

- 安装 `Git`
- 安装 `Python`
- 安装 `Node.js`
- 安装 `pytest`
- 选择是否安装 `nvm-windows`
- 配置 npm 源、代理或网络访问
- 在本机实际运行 MCP server 启动命令

当前仓库不会在测试中自动安装这些依赖，也不会自动启动 MCP server。
