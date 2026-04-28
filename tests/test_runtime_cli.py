from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from ai_test_assistant.memory.sqlite_store import SQLiteMemoryStore
from ai_test_assistant.runtime.cli import build_parser, run_cli


def _write_assistant_config(tmp_path: Path) -> Path:
    memory_db_path = (tmp_path / "memory.sqlite3").resolve()
    intents_path = Path("configs/intents.yaml").resolve()
    tools_path = Path("configs/tools.yaml").resolve()
    assistant_config = tmp_path / "assistant.yaml"
    assistant_config.write_text(
        "\n".join(
            [
                "memory:",
                "  backend: sqlite",
                f"  sqlite_path: {memory_db_path.as_posix()}",
                "intent:",
                f"  rules_path: {intents_path.as_posix()}",
                "tool_registry:",
                f"  config_path: {tools_path.as_posix()}",
            ]
        ),
        encoding="utf-8",
    )
    return assistant_config


def test_cli_parser_supports_required_arguments() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "根据这个需求生成测试用例",
            "--intent-only",
            "--write-memory",
            "--read-file",
            "README.md",
            "--show-file-content",
            "--config",
            "configs/assistant.yaml",
        ]
    )

    assert args.task_text == "根据这个需求生成测试用例"
    assert args.intent_only is True
    assert args.write_memory is True
    assert args.read_file == "README.md"
    assert args.show_file_content is True
    assert args.config == "configs/assistant.yaml"
    assert args.dry_run is True


def test_cli_parser_supports_mcp_read_file_argument() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "请读取 README 并分析项目状态",
            "--mcp-read-file",
            "README.md",
            "--config",
            "configs/assistant.yaml",
        ]
    )

    assert args.mcp_read_file == "README.md"
    assert args.read_file is None


def test_cli_intent_only_outputs_intent_result(tmp_path: Path, capsys) -> None:
    config_path = _write_assistant_config(tmp_path)

    exit_code = run_cli(["分析这段报错日志", "--intent-only", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "识别意图：log_analysis" in captured
    assert "是否需要澄清：否" in captured
    assert "推荐 workflow：agent-assets/prompts/log-analysis.md" in captured


def test_cli_dry_run_outputs_plan(tmp_path: Path, capsys) -> None:
    config_path = _write_assistant_config(tmp_path)

    exit_code = run_cli(["根据这个需求生成测试用例", "--dry-run", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "dry-run：是" in captured
    assert "识别意图：test_case_generation" in captured
    assert "下一步计划：" in captured
    assert "当前为 dry-run：仅生成任务计划，不执行外部工具。" in captured
    assert "任务结果记忆写入：禁止" in captured
    assert "工具授权评估：已完成" in captured
    assert "推荐工具：memory_read" in captured
    assert "memory_read | 状态=enabled | 风险=read_only | 允许执行=是 | 需要确认=否" in captured


def test_cli_dry_run_reads_single_allowed_file_with_preview_by_default(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / "README.md").write_text("line1\nline2\nline3", encoding="utf-8", newline="\n")
    monkeypatch.chdir(repo_dir.resolve())

    exit_code = run_cli(["请读取 README 并分析项目状态", "--dry-run", "--read-file", "README.md", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "显式文件读取请求：README.md" in captured
    assert "文件读取结果：" in captured
    assert "允许读取=是 | 来源=local_adapter | 路径=README.md | 字符数=17 | 已截断=否" in captured
    assert "结果说明：Read allowed." in captured
    assert "文件预览：" in captured
    assert "line1" in captured
    assert "文件内容：" not in captured


def test_cli_dry_run_shows_full_file_content_only_with_explicit_flag(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / "README.md").write_text("line1\nline2\nline3", encoding="utf-8", newline="\n")
    monkeypatch.chdir(repo_dir.resolve())

    exit_code = run_cli(
        [
            "请读取 README 并分析项目状态",
            "--dry-run",
            "--read-file",
            "README.md",
            "--show-file-content",
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "文件内容：" in captured
    assert "line1" in captured
    assert "line3" in captured
    assert "文件预览：" not in captured


def test_cli_dry_run_refuses_sensitive_file_read(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    monkeypatch.chdir(repo_dir.resolve())

    exit_code = run_cli(["请读取环境配置", "--dry-run", "--read-file", ".env", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "显式文件读取请求：.env" in captured
    assert "允许读取=否 | 来源=local_adapter | 路径=.env | 字符数=0 | 已截断=否" in captured
    assert "结果说明：Sensitive file is blocked." in captured
    assert "文件预览：" not in captured
    assert "文件内容：" not in captured


def test_cli_dry_run_reads_single_allowed_file_via_mcp_with_preview_by_default(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    config_path = _write_assistant_config(tmp_path)
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    monkeypatch.chdir(repo_dir.resolve())

    class StubMcpClient:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        async def read_text(self, repo_relative_path: str) -> SimpleNamespace:
            assert repo_relative_path == "README.md"
            assert self.repo_root == repo_dir.resolve()
            return SimpleNamespace(
                allowed=True,
                path="README.md",
                content="line1\nline2\nline3",
                reason="Read allowed through filesystem MCP.",
                truncated=False,
            )

    monkeypatch.setattr("ai_test_assistant.runtime.cli.FilesystemMcpReadClient", StubMcpClient)

    exit_code = run_cli(
        [
            "请读取 README 并分析项目状态",
            "--dry-run",
            "--mcp-read-file",
            "README.md",
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "识别意图：tool_research" in captured
    assert "显式文件读取请求：README.md" in captured
    assert "允许读取=是 | 来源=filesystem_mcp | 路径=README.md | 字符数=17 | 已截断=否" in captured
    assert "结果说明：Read allowed through filesystem MCP." in captured
    assert "文件预览：" in captured
    assert "文件内容：" not in captured


def test_cli_mcp_readme_project_status_request_is_not_unknown(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    monkeypatch.chdir(repo_dir.resolve())

    class StubMcpClient:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        async def read_text(self, repo_relative_path: str) -> SimpleNamespace:
            return SimpleNamespace(
                allowed=True,
                path=repo_relative_path,
                content="project status",
                reason="Read allowed through filesystem MCP.",
                truncated=False,
            )

    monkeypatch.setattr("ai_test_assistant.runtime.cli.FilesystemMcpReadClient", StubMcpClient)

    exit_code = run_cli(
        [
            "请读取 README 并分析项目状态",
            "--dry-run",
            "--mcp-read-file",
            "README.md",
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "识别意图：unknown" not in captured
    assert "识别意图：tool_research" in captured


def test_cli_dry_run_shows_full_mcp_file_content_only_with_explicit_flag(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    config_path = _write_assistant_config(tmp_path)
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    monkeypatch.chdir(repo_dir.resolve())

    class StubMcpClient:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        async def read_text(self, repo_relative_path: str) -> SimpleNamespace:
            return SimpleNamespace(
                allowed=True,
                path=repo_relative_path,
                content="line1\nline2\nline3",
                reason="Read allowed through filesystem MCP.",
                truncated=False,
            )

    monkeypatch.setattr("ai_test_assistant.runtime.cli.FilesystemMcpReadClient", StubMcpClient)

    exit_code = run_cli(
        [
            "请读取 README 并分析项目状态",
            "--dry-run",
            "--mcp-read-file",
            "README.md",
            "--show-file-content",
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "文件内容：" in captured
    assert "line1" in captured
    assert "line3" in captured
    assert "文件预览：" not in captured


def test_cli_dry_run_refuses_sensitive_mcp_file_read(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    monkeypatch.chdir(repo_dir.resolve())

    class StubMcpClient:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        async def read_text(self, repo_relative_path: str) -> SimpleNamespace:
            assert repo_relative_path == ".env"
            return SimpleNamespace(
                allowed=False,
                path=".env",
                content=None,
                reason="Sensitive file is blocked.",
                truncated=False,
            )

    monkeypatch.setattr("ai_test_assistant.runtime.cli.FilesystemMcpReadClient", StubMcpClient)

    exit_code = run_cli(
        [
            "请读取环境配置",
            "--dry-run",
            "--mcp-read-file",
            ".env",
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "显式文件读取请求：.env" in captured
    assert "允许读取=否 | 来源=filesystem_mcp | 路径=.env | 字符数=0 | 已截断=否" in captured
    assert "结果说明：Sensitive file is blocked." in captured
    assert "文件预览：" not in captured
    assert "文件内容：" not in captured


def test_cli_ambiguous_task_returns_clarification_prompt(tmp_path: Path, capsys) -> None:
    config_path = _write_assistant_config(tmp_path)

    exit_code = run_cli(["帮我看看这个", "--intent-only", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "识别意图：unknown" in captured
    assert "是否需要澄清：是" in captured
    assert "澄清问题：" in captured


def test_cli_reports_missing_config(capsys) -> None:
    exit_code = run_cli(["分析这段日志", "--config", "missing-assistant.yaml"])

    captured = capsys.readouterr().out
    assert exit_code == 2
    assert "错误：配置文件不存在" in captured


def test_cli_write_memory_flag_is_reflected_in_output(tmp_path: Path, capsys) -> None:
    config_path = _write_assistant_config(tmp_path)

    exit_code = run_cli(["根据这个需求生成测试用例", "--dry-run", "--write-memory", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "任务结果记忆写入：允许" in captured


def test_cli_without_write_memory_does_not_write_task_result_memory(tmp_path: Path, capsys) -> None:
    config_path = _write_assistant_config(tmp_path)
    db_path = tmp_path / "memory.sqlite3"

    exit_code = run_cli(["根据这个需求生成测试用例", "--dry-run", "--config", str(config_path)])

    assert exit_code == 0
    capsys.readouterr()
    store = SQLiteMemoryStore(db_path)
    assert store.search_memory("task_result/orchestrator") == []


def test_cli_with_write_memory_writes_task_result_memory(tmp_path: Path, capsys) -> None:
    config_path = _write_assistant_config(tmp_path)
    db_path = tmp_path / "memory.sqlite3"

    exit_code = run_cli(["根据这个需求生成测试用例", "--dry-run", "--write-memory", "--config", str(config_path)])

    assert exit_code == 0
    capsys.readouterr()
    store = SQLiteMemoryStore(db_path)
    results = store.search_memory("task_result/orchestrator")
    assert len(results) == 1
    assert results[0].value["intent"] == "test_case_generation"


def test_cli_write_memory_keeps_only_input_file_metadata(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)
    db_path = tmp_path / "memory.sqlite3"
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / "README.md").write_text("line1\nline2\nline3", encoding="utf-8", newline="\n")
    monkeypatch.chdir(repo_dir.resolve())

    exit_code = run_cli(
        [
            "请读取 README 并分析项目状态",
            "--dry-run",
            "--read-file",
            "README.md",
            "--write-memory",
            "--config",
            str(config_path),
        ]
    )

    assert exit_code == 0
    capsys.readouterr()
    store = SQLiteMemoryStore(db_path)
    results = store.search_memory("task_result/orchestrator")
    assert len(results) == 1
    input_files = results[0].value["input_files"]
    assert input_files[0]["path"] == "README.md"
    assert input_files[0]["content_length"] == len("line1\nline2\nline3")
    assert "content" not in input_files[0]


def test_cli_mcp_write_memory_keeps_only_input_file_metadata(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)
    db_path = tmp_path / "memory.sqlite3"
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    monkeypatch.chdir(repo_dir.resolve())

    class StubMcpClient:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        async def read_text(self, repo_relative_path: str) -> SimpleNamespace:
            return SimpleNamespace(
                allowed=True,
                path=repo_relative_path,
                content="line1\nline2\nline3",
                reason="Read allowed through filesystem MCP.",
                truncated=False,
            )

    monkeypatch.setattr("ai_test_assistant.runtime.cli.FilesystemMcpReadClient", StubMcpClient)

    exit_code = run_cli(
        [
            "请读取 README 并分析项目状态",
            "--dry-run",
            "--mcp-read-file",
            "README.md",
            "--write-memory",
            "--config",
            str(config_path),
        ]
    )

    assert exit_code == 0
    capsys.readouterr()
    store = SQLiteMemoryStore(db_path)
    results = store.search_memory("task_result/orchestrator")
    assert len(results) == 1
    input_files = results[0].value["input_files"]
    assert input_files[0]["path"] == "README.md"
    assert input_files[0]["source"] == "filesystem_mcp"
    assert input_files[0]["content_length"] == len("line1\nline2\nline3")
    assert "content" not in input_files[0]


def test_cli_intent_only_never_writes_task_result_memory(tmp_path: Path, capsys) -> None:
    config_path = _write_assistant_config(tmp_path)
    db_path = tmp_path / "memory.sqlite3"

    exit_code = run_cli(["分析这段报错日志", "--intent-only", "--write-memory", "--config", str(config_path)])

    assert exit_code == 0
    capsys.readouterr()
    store = SQLiteMemoryStore(db_path)
    assert store.search_memory("task_result/orchestrator") == []


def test_cli_dry_run_outputs_tool_risk_for_planned_tools(tmp_path: Path, capsys) -> None:
    config_path = _write_assistant_config(tmp_path)

    exit_code = run_cli(["请运行 pytest 并分析 Allure 结果", "--dry-run", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "识别意图：pytest_execution" in captured
    assert "推荐工具：pytest_runner" in captured
    assert "pytest_runner | 状态=planned | 风险=execute_local_command | 允许执行=否 | 需要确认=否" in captured
    assert "拒绝原因：Tool 'pytest_runner' is not enabled. Current status: planned." in captured


def test_cli_dry_run_outputs_memory_write_risk(tmp_path: Path, capsys) -> None:
    config_path = _write_assistant_config(tmp_path)

    exit_code = run_cli(["请记住这个输出偏好并更新记忆", "--dry-run", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "识别意图：memory_update" in captured
    assert "推荐工具：memory_write" in captured
    assert "memory_write | 状态=disabled | 风险=restricted_action | 允许执行=否 | 需要确认=否" in captured
    assert "拒绝原因：Tool 'memory_write' is not enabled. Current status: disabled." in captured
