# 本地环境前置条件

本项目使用 `pyproject.toml` 作为唯一主依赖源，不维护 `requirements.txt` / `requirements-dev.txt`。

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
allure --version
```

Allure CLI 说明：

- `allure_generate` 需要本机已安装官方 Allure CLI。
- 本项目不会自动安装 Allure CLI，也不会访问外部网络安装依赖。
- Windows 上需要用户自行安装 Allure CLI，并确保 `allure --version` 可用。
- runtime 只会受控执行固定命令：`allure generate <results_dir> -o <report_dir> --clean`。
- 不支持 `allure serve`，不打开浏览器，不开放 shell。

只要这些命令能正常输出版本号，就说明对应工具已可用。

当前已完成的本地验证结果：

- `node -v`：`v24.15.0`
- `npm -v`：`11.12.1`
- `npx -v`：`11.12.1`

## Windows 安装建议

- 推荐 Windows 使用项目独立 `.venv`，不要长期复用全局 Python 环境。
- `Git`：安装官方 Windows 版本
- `Python`：安装当前项目可用的 Python 版本，并确保命令行可直接使用 `python`
- `pytest`：在当前 Python 环境内安装，不要跨环境混装
- `Node.js`：优先安装 LTS 版本
- `npm` / `npx`：通常随 `Node.js` 一起提供

推荐初始化步骤：

```powershell
cd D:\TestHome\ai-test-lab
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e ".[test]"
```

推荐验证命令：

```powershell
python -c "import mcp; print('mcp ok')"
python -c "import langgraph; print('langgraph ok')"
pytest
```

如果全局 Python 环境里出现 `fastapi/starlette`、`langchain/langgraph` 之类的冲突，优先切换到项目独立 `.venv`，不要为了兼容全局环境去修改本项目依赖。

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
