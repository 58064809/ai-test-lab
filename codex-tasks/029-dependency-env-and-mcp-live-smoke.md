# Codex Task 029：依赖环境收口与 filesystem MCP live smoke 验证

## 背景

028 已经把 filesystem MCP read 接入 runtime，用户本地也已经安装 Node.js，并验证：

```powershell
npx -y @modelcontextprotocol/server-filesystem .
```

可以启动并输出：

```text
Secure MCP Filesystem Server running on stdio
```

随后用户执行项目依赖安装时，出现过全局 Python 环境依赖冲突警告：

```text
fastapi requires starlette<0.47.0,>=0.40.0, but installed starlette 1.0.0
langchain requires langgraph<1.1.0,>=1.0.8, but installed langgraph 0.6.11
```

用户已明确决定：

- 不新增 `requirements.txt`
- 不新增 `requirements-dev.txt`
- 只维护 `pyproject.toml` 作为唯一主依赖源

本任务目标：把依赖环境、venv 建议、MCP live smoke 验证和 README 读取场景收口，避免继续在环境问题上反复。

## 最高原则

1. `pyproject.toml` 是唯一主依赖源。
2. 不新增 `requirements.txt`。
3. 不新增 `requirements-dev.txt`。
4. 不为了兼容用户全局环境里的 `fastapi/langchain` 去乱改项目依赖。
5. 推荐使用项目独立 `.venv`。
6. 不扩展 `LocalFilesystemReadAdapter`。
7. 不开放 `filesystem_write`。
8. 不开放 `shell`。
9. 不实现多文件读取、目录读取、glob、自动上下文收集。
10. 不把完整文件内容写入 memory。

## 必须先阅读

- `pyproject.toml`
- `docs/local-environment-prerequisites.md`
- `docs/filesystem-mcp-quickstart.md`
- `src/ai_test_assistant/filesystem/mcp_client.py`
- `src/ai_test_assistant/runtime/cli.py`
- `configs/tools.yaml`
- `configs/intents.yaml`
- `tests/test_runtime_cli.py`
- `tests/test_filesystem_mcp_runtime_read.py`

## 任务一：确认 pyproject 是唯一依赖源

检查仓库中是否存在：

- `requirements.txt`
- `requirements-dev.txt`

如果不存在，保持不存在。

如果已经被误加，请删除，并在文档中明确：

```text
本项目使用 pyproject.toml 管理依赖，不维护 requirements.txt / requirements-dev.txt。
```

不要把 `langgraph`、`mcp`、`PyYAML`、`pytest` 的版本重复写到 requirements 文件中。

## 任务二：更新本地环境文档

更新：

```text
docs/local-environment-prerequisites.md
```

必须明确：

1. 推荐 Windows 使用项目独立 `.venv`。
2. 创建与激活命令：

```powershell
cd D:\TestHome\ai-test-lab
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e ".[test]"
```

3. 验证命令：

```powershell
python -c "import mcp; print('mcp ok')"
python -c "import langgraph; print('langgraph ok')"
pytest
```

4. 如果全局 Python 出现 fastapi/starlette/langchain/langgraph 冲突，优先使用独立 `.venv`，不要为了全局环境去改项目依赖。
5. Node.js / npm / npx 仍然是 filesystem MCP server 的前置条件。

## 任务三：补充 filesystem MCP live smoke 文档

更新：

```text
docs/filesystem-mcp-quickstart.md
```

新增一个“live smoke 验证”小节。

必须包含：

```powershell
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --mcp-read-file README.md
python scripts/run_assistant.py "请读取环境配置" --dry-run --mcp-read-file .env
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --mcp-read-file README.md --show-file-content
```

预期：

- 第一条应通过 MCP read 读取 README。
- 第二条应被 `FilesystemReadPolicy` 拒绝，原因包含 `Sensitive file is blocked.`。
- 第三条只有显式 `--show-file-content` 才展示完整允许内容。

## 任务四：补齐 README/项目状态读取意图规则

当前命令：

```powershell
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --mcp-read-file README.md
```

能触发文件读取，但 intent 可能仍是 `unknown`。

请在 `configs/intents.yaml` 中补充或调整规则，使以下任务文本不再识别为 `unknown`：

- `请读取 README 并分析项目状态`
- `读取 README 并分析项目状态`
- `结合 README 分析项目状态`

推荐归类：

- 如果已有 `requirement_analysis` / `code_review` / `tool_research` 等合适 intent，选择最贴近的现有 intent。
- 不要为了这一句新建复杂 intent 体系。
- 不要引入外部 LLM。

同步更新测试：

- `tests/test_intent_router.py`
- `tests/test_runtime_cli.py` 如有必要

要求：MCP read 本身不是 intent，但这类任务不应再被识别为 unknown。

## 任务五：新增或更新测试

至少覆盖：

1. 仓库不包含 `requirements.txt` / `requirements-dev.txt`，或如果有，测试失败并提示不应维护双依赖源。
2. `pyproject.toml` 包含 `mcp`、`langgraph`、`PyYAML`、`pytest`。
3. `docs/local-environment-prerequisites.md` 包含 `.venv`、`python -m pip install -e ".[test]"`。
4. README 项目状态读取任务不再被识别为 `unknown`。
5. `--mcp-read-file README.md` 的 runtime 输出不再是 unknown intent。
6. `.env` 仍然被拒绝。
7. `filesystem_write` 仍是 disabled。
8. `shell` 仍是 disabled。

## 禁止事项

- 不要新增 requirements 文件。
- 不要为了全局 fastapi/langchain 冲突去改项目依赖。
- 不要扩展本地文件 adapter。
- 不要开放 write。
- 不要开放 shell。
- 不要实现多文件读取、目录读取、glob 或自动上下文收集。
- 不要把完整文件内容写入 memory。

## 验收命令

```bash
pytest
```

手动验证：

```powershell
python scripts/run_assistant.py "请读取 README 并分析项目状态" --dry-run --mcp-read-file README.md
python scripts/run_assistant.py "请读取环境配置" --dry-run --mcp-read-file .env
```

## 完成标准

- `pyproject.toml` 仍是唯一主依赖源。
- 文档明确推荐 `.venv`。
- filesystem MCP live smoke 文档清楚。
- README 项目状态读取任务不再识别为 unknown。
- MCP read、安全拒绝、工具边界测试通过。
- 所有测试通过。
