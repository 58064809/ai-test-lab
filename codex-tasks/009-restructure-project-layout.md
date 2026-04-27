# Codex Task 009：重构项目目录结构，分离 Agent 资产、文档与 Python 工程代码

## 任务背景

当前仓库已经从“文档型仓库”开始转向“个人执行型 AI 测试助手工程”。但目录结构仍然混杂：

- `tools/` 实际是工具说明文档，不是代码工具层。
- `prompts/`、`templates/`、`workflows/`、`examples/` 是 Agent 资产，但散落在根目录。
- 后续代码层需要 `tool_registry`，不应与根目录 `tools/` 混淆。
- 当前已有 `src/ai_test_assistant/`，但缺少标准 Python 工程配置。

本任务只做目录结构重构与路径引用修复，不新增业务功能，不实现 intent、orchestrator、tools registry、runtime。

## 最高原则

1. 不造轮子。
2. 不新增业务功能。
3. 不改变 memory 核心逻辑。
4. 不写死任何具体业务规则。
5. 不把未实现能力写成已完成。
6. 重构后必须保持现有 memory 测试可运行。
7. Markdown 默认中文，非必要不使用英文。

## 必须先阅读

- `AGENTS.md`
- `codex-tasks/008-memory-review-fixes.md`
- `docs/current-status.md`
- `docs/foundation-architecture.md`
- `src/ai_test_assistant/memory/README.md`

## 目标目录结构

请将仓库调整为以下结构方向：

```text
ai-test-lab/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── .gitignore
├── configs/
│   └── assistant.yaml
│
├── codex-tasks/
│   ├── 001-foundation.md
│   ├── 002-memory-foundation.md
│   ├── 003-intent-router.md
│   ├── 004-orchestrator-langgraph.md
│   ├── 005-tool-registry-and-mcp.md
│   ├── 006-runtime-cli-and-tests.md
│   ├── 007-review-and-hardening.md
│   ├── 008-memory-review-fixes.md
│   └── 009-restructure-project-layout.md
│
├── agent-assets/
│   ├── prompts/
│   ├── templates/
│   ├── workflows/
│   └── examples/
│
├── docs/
│   ├── foundation-architecture.md
│   ├── current-status.md
│   ├── next-steps.md
│   └── tools/
│       ├── codex.md
│       ├── mcp.md
│       ├── playwright-mcp.md
│       ├── schemathesis.md
│       ├── keploy.md
│       ├── pytest-allure.md
│       ├── openhands.md
│       ├── langgraph.md
│       └── sources.md
│
├── src/
│   └── ai_test_assistant/
│       ├── __init__.py
│       ├── config/
│       ├── memory/
│       ├── intent/
│       ├── orchestrator/
│       ├── tool_registry/
│       ├── runtime/
│       └── schemas/
│
├── scripts/
│   └── .gitkeep
│
└── tests/
    └── test_memory_store.py
```

说明：

- `agent-assets/`：存放给 Codex / OpenHands / Agent 读取的提示词、模板、工作流、示例。
- `docs/tools/`：存放工具说明文档和官方来源，不是代码工具层。
- `src/ai_test_assistant/tool_registry/`：后续代码层工具注册表目录，避免与文档型 `tools/` 混淆。
- `scripts/` 暂时只保留 `.gitkeep`，不要实现 runtime CLI。

## 必须执行的迁移

### 1. 移动 Agent 资产

将：

```text
prompts/      -> agent-assets/prompts/
templates/    -> agent-assets/templates/
workflows/    -> agent-assets/workflows/
examples/     -> agent-assets/examples/
```

迁移后删除旧目录。

### 2. 移动工具说明文档

将：

```text
tools/ -> docs/tools/
```

迁移后删除旧 `tools/` 目录。

### 3. 预留代码目录

创建以下 Python 包目录：

```text
src/ai_test_assistant/config/
src/ai_test_assistant/intent/
src/ai_test_assistant/orchestrator/
src/ai_test_assistant/tool_registry/
src/ai_test_assistant/runtime/
src/ai_test_assistant/schemas/
```

要求：

- 每个目录至少有 `__init__.py`。
- 不要在这些目录里写实现逻辑。
- 不要实现 intent、orchestrator、tool registry、runtime。

### 4. 新增或修复 pyproject.toml

如果尚未存在，请新增最小 `pyproject.toml`。

要求：

- 使用 src-layout。
- 声明项目名。
- 声明 Python 版本范围。
- 声明运行依赖 `PyYAML`。
- 声明测试依赖 `pytest`。
- 不引入无关依赖。

### 5. 新增或修复 .gitignore

必须包含：

```text
.assistant/
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
.env
```

### 6. 修复所有路径引用

必须更新以下文件中的旧路径引用：

- `README.md`
- `AGENTS.md`
- `docs/current-status.md`
- `docs/foundation-architecture.md`
- `docs/next-steps.md`
- `codex-tasks/*.md`

重点：

- `tools/xxx.md` 改为 `docs/tools/xxx.md`。
- `prompts/xxx.md` 改为 `agent-assets/prompts/xxx.md`。
- `templates/xxx.md` 改为 `agent-assets/templates/xxx.md`。
- `workflows/xxx.md` 改为 `agent-assets/workflows/xxx.md`。
- `examples/xxx.md` 改为 `agent-assets/examples/xxx.md`。
- 删除所有本地绝对路径，例如本地磁盘路径。

## 禁止事项

- 不要实现 intent router。
- 不要实现 orchestrator。
- 不要实现 tool registry 逻辑。
- 不要实现 runtime CLI。
- 不要引入 LangGraph。
- 不要引入 MCP server。
- 不要引入向量库。
- 不要修改 memory 的业务逻辑，除非路径重构导致 import 必须调整。
- 不要把 Agent 资产误放进 Python package。

## 验收命令

```bash
pytest tests/test_memory_store.py
```

如果本地环境缺依赖，请先按 `pyproject.toml` 安装测试依赖后再执行。

## 人工验收清单

完成后请确认：

- 根目录没有旧 `tools/`、`prompts/`、`templates/`、`workflows/`、`examples/`。
- Agent 资产统一在 `agent-assets/`。
- 工具说明统一在 `docs/tools/`。
- 代码工具层预留目录叫 `src/ai_test_assistant/tool_registry/`，不是 `tools/`。
- `pyproject.toml` 存在。
- `.gitignore` 存在。
- 文档中没有本地绝对路径。
- memory 测试仍能通过。

## 完成标准

本任务完成后，仓库可以进入更清晰的阶段：

1. 先完成 `008-memory-review-fixes.md` 中剩余修复。
2. 再进入 `003-intent-router.md`。
3. 后续代码实现都放在 `src/ai_test_assistant/` 下。
4. 后续 Agent 资产都放在 `agent-assets/` 下。
5. 后续工具说明都放在 `docs/tools/` 下。
