# Codex Task 008：修复 memory 交付审查问题

## 背景

你已经完成了 memory 最小底座第一轮交付。审查结果：方向基本正确，但还不能算完全通过，因为存在工程可运行性、文档路径、依赖声明和边界一致性问题。

本任务只修复 memory 交付问题，不要开始实现 intent、orchestrator、tools、runtime。

## 必须先阅读

- `codex-tasks/002-memory-foundation.md`
- `src/ai_test_assistant/memory/README.md`
- `docs/current-status.md`
- `docs/foundation-architecture.md`
- `tests/test_memory_store.py`

## 问题 1：缺少项目依赖与 src-layout 测试配置

当前代码使用 `src/ai_test_assistant` 目录，但仓库没有 `pyproject.toml`、`pytest.ini` 或等价配置。

风险：

- 在干净环境直接执行 `pytest tests/test_memory_store.py` 时，可能无法 import `ai_test_assistant`。
- `MemoryService` 使用 `yaml`，但仓库没有声明 `PyYAML` 依赖。

修复要求：

1. 新增最小 `pyproject.toml`。
2. 声明 Python 版本范围。
3. 声明运行依赖 `PyYAML`。
4. 声明测试依赖 `pytest`。
5. 确保 src-layout 下 pytest 能正常 import 包。
6. 不要引入多余依赖。

验收：

```bash
pytest tests/test_memory_store.py
```

## 问题 2：缺少 .gitignore

当前默认配置会将 SQLite 文件写入 `.assistant/memory.sqlite3`，但仓库没有 `.gitignore`。

风险：

- 本地 memory 数据可能被误提交。
- 测试缓存、Python 缓存可能被误提交。

修复要求：

新增 `.gitignore`，至少包含：

```text
.assistant/
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
.env
```

## 问题 3：docs/foundation-architecture.md 使用了本地绝对路径链接

当前文档里出现类似：

```text
../src/ai_test_assistant/...
```

这是本地机器路径，不适合提交到仓库文档。

修复要求：

1. 改成仓库相对路径。
2. 不要出现本地磁盘路径。
3. 保持中文说明。

## 问题 4：search_memory 的 filter 能力过窄，需要明确边界或补足

当前 `search_memory` 只支持 `memory_type` 和 `source` 过滤。这个实现可以接受，但文档必须明确第一版只支持这两个过滤条件。

修复要求：

1. 在 `src/ai_test_assistant/memory/README.md` 中明确支持的 filters。
2. 在测试中增加一个未知 filter 抛错用例。
3. 不要伪装成支持任意 JSON 字段过滤。

## 问题 5：README 总状态落后

根目录 `README.md` 仍然说仓库主要是规则、提示词、工作流、模板和工具说明，没有同步说明 memory 最小底座已经落地。

修复要求：

更新根目录 `README.md`：

- 增加 memory 最小底座已落地。
- 明确 intent、orchestrator、tool registry、runtime CLI 尚未实现。
- 不要夸大成完整助手已经可用。

## 禁止事项

- 不要实现 intent。
- 不要实现 orchestrator。
- 不要实现 tools registry。
- 不要实现 runtime CLI。
- 不要引入向量库。
- 不要引入 LangGraph 作为 memory 修复的一部分。
- 不要把未验证能力写成已完成。

## 最终验收

```bash
pytest tests/test_memory_store.py
```

并人工检查：

- `pyproject.toml` 存在且依赖最小。
- `.gitignore` 存在且排除 `.assistant/`。
- 文档没有本地绝对路径。
- README 状态真实。
- memory README 明确 search filter 边界。

## 通过标准

完成后，这一轮 memory 底座可判定为“阶段性通过”，然后才能进入 `003-intent-router.md`。
