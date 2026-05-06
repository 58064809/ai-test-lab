from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from ai_test_assistant.memory.sqlite_store import SQLiteMemoryStore
from ai_test_assistant.runtime.cli import build_parser, run_cli


def _write_assistant_config(tmp_path: Path, tools_path: Path | None = None) -> Path:
    memory_db_path = (tmp_path / "memory.sqlite3").resolve()
    intents_path = Path("configs/intents.yaml").resolve()
    tools_path = tools_path or Path("configs/tools.yaml").resolve()
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


def test_cli_parser_supports_run_pytest_with_default_target() -> None:
    parser = build_parser()
    args = parser.parse_args(["请运行 pytest", "--run-pytest", "--config", "configs/assistant.yaml"])

    assert args.run_pytest == "tests"


def test_cli_parser_supports_run_pytest_with_explicit_target() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "请运行 pytest",
            "--run-pytest",
            "tests/test_runtime_cli.py",
            "--config",
            "configs/assistant.yaml",
        ]
    )

    assert args.run_pytest == "tests/test_runtime_cli.py"


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


def test_cli_github_read_requires_explicit_repo_without_starting_client(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    config_path = _write_assistant_config(tmp_path)

    class StubGitHubClient:
        def __init__(self) -> None:
            raise AssertionError("GitHub MCP client must not start without explicit --github-repo.")

    monkeypatch.setattr("ai_test_assistant.runtime.cli.GitHubMcpReadClient", StubGitHubClient)

    exit_code = run_cli(
        [
            "读取 GitHub README 并分析",
            "--dry-run",
            "--github-read-file",
            "README.md",
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr().out
    assert exit_code == 2
    assert "GitHub read requires explicit --github-repo." in captured


def test_cli_github_read_requires_authorization_before_starting_client(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    tools_path = tmp_path / "tools.yaml"
    tools_path.write_text(
        "\n".join(
            [
                "tools:",
                "  - name: github_read",
                "    description: GitHub read disabled for this test.",
                "    status: disabled",
                "    risk_level: external_network",
                "    category: scm",
                "    implementation: official_mcp",
            ]
        ),
        encoding="utf-8",
    )
    config_path = _write_assistant_config(tmp_path, tools_path=tools_path.resolve())

    class StubGitHubClient:
        def __init__(self) -> None:
            raise AssertionError("GitHub MCP client must not start without github_read authorization.")

    monkeypatch.setattr("ai_test_assistant.runtime.cli.GitHubMcpReadClient", StubGitHubClient)

    exit_code = run_cli(
        [
            "读取 GitHub README 并分析",
            "--dry-run",
            "--github-repo",
            "58064809/ai-test-lab",
            "--github-read-file",
            "README.md",
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr().out
    assert exit_code == 2
    assert "github_read is not authorized." in captured
    assert "not enabled" in captured


def test_cli_github_read_authorized_invokes_client_and_outputs_source_and_risk(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    config_path = _write_assistant_config(tmp_path)
    monkeypatch.setenv("GITHUB_PERSONAL_ACCESS_TOKEN", "ghp_secret_value")
    calls: list[dict[str, str | None]] = []

    class StubGitHubClient:
        async def read_file(self, repository: str, path: str, ref: str | None = None) -> SimpleNamespace:
            calls.append({"repository": repository, "path": path, "ref": ref})
            return SimpleNamespace(
                allowed=True,
                operation="read_file",
                repository=repository,
                target=path,
                content="successfully downloaded text file (SHA: d158cba4bd47f227961ff37268956ffb46f63eef)",
                reason="Read allowed through GitHub MCP.",
                truncated=False,
            )

    monkeypatch.setattr("ai_test_assistant.runtime.cli.GitHubMcpReadClient", StubGitHubClient)

    exit_code = run_cli(
        [
            "读取 GitHub README 并分析",
            "--dry-run",
            "--github-repo",
            "58064809/ai-test-lab",
            "--github-read-file",
            "README.md",
            "--github-ref",
            "master",
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert calls == [{"repository": "58064809/ai-test-lab", "path": "README.md", "ref": "master"}]
    assert "允许读取=是 | 来源=github_mcp | 路径=README.md" in captured
    assert "显式只读外部网络访问" in captured
    assert "显式工具执行结果：" in captured
    assert "github_read | 来源=github_mcp | 操作=read_file | 风险=external_network | 已执行=是 | 授权方式=CLI explicit approval" in captured
    assert "Tool 'github_read' needs external network approval." not in captured
    assert "d158cba4bd47f227961ff37268956ffb46f63eef" in captured
    assert "ghp_secret_value" not in captured


def test_cli_github_read_refused_by_client_does_not_show_dry_run_network_approval_conflict(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    config_path = _write_assistant_config(tmp_path)

    class StubGitHubClient:
        async def read_file(self, repository: str, path: str, ref: str | None = None) -> SimpleNamespace:
            assert repository == "58064809/ai-test-lab"
            assert path == ".env"
            return SimpleNamespace(
                allowed=False,
                operation="read_file",
                repository=repository,
                target=path,
                content=None,
                reason="Sensitive GitHub file path is blocked.",
                truncated=False,
            )

    monkeypatch.setattr("ai_test_assistant.runtime.cli.GitHubMcpReadClient", StubGitHubClient)

    exit_code = run_cli(
        [
            "读取 GitHub 环境配置",
            "--dry-run",
            "--github-repo",
            "58064809/ai-test-lab",
            "--github-read-file",
            ".env",
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "允许读取=否 | 来源=github_mcp | 路径=.env" in captured
    assert "结果说明：Sensitive GitHub file path is blocked." in captured
    assert "显式工具执行结果：" in captured
    assert "github_read | 来源=github_mcp | 操作=read_file | 风险=external_network | 已执行=否 | 授权方式=CLI explicit approval" in captured
    assert "Tool 'github_read' needs external network approval." not in captured


def test_cli_github_write_memory_keeps_only_input_file_metadata(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    config_path = _write_assistant_config(tmp_path)
    db_path = tmp_path / "memory.sqlite3"

    class StubGitHubClient:
        async def read_file(self, repository: str, path: str, ref: str | None = None) -> SimpleNamespace:
            return SimpleNamespace(
                allowed=True,
                operation="read_file",
                repository=repository,
                target=path,
                content="successfully downloaded text file (SHA: d158cba4bd47f227961ff37268956ffb46f63eef)",
                reason="Read allowed through GitHub MCP.",
                truncated=False,
            )

    monkeypatch.setattr("ai_test_assistant.runtime.cli.GitHubMcpReadClient", StubGitHubClient)

    exit_code = run_cli(
        [
            "读取 GitHub README 并分析",
            "--dry-run",
            "--github-repo",
            "58064809/ai-test-lab",
            "--github-read-file",
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
    assert input_files[0]["source"] == "github_mcp"
    assert input_files[0]["content_length"] == len(
        "successfully downloaded text file (SHA: d158cba4bd47f227961ff37268956ffb46f63eef)"
    )
    assert "content" not in input_files[0]


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
    assert "pytest_runner | 状态=enabled | 风险=execute_local_command | 允许执行=否 | 需要确认=否" in captured
    assert "拒绝原因：Tool 'pytest_runner' cannot run local commands during dry-run." in captured


def test_cli_dry_run_outputs_memory_write_risk(tmp_path: Path, capsys) -> None:
    config_path = _write_assistant_config(tmp_path)

    exit_code = run_cli(["请记住这个输出偏好并更新记忆", "--dry-run", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "识别意图：memory_update" in captured
    assert "推荐工具：memory_write" in captured
    assert "memory_write | 状态=disabled | 风险=restricted_action | 允许执行=否 | 需要确认=否" in captured
    assert "拒绝原因：Tool 'memory_write' is not enabled. Current status: disabled." in captured


def test_cli_run_pytest_executes_default_target_and_outputs_structured_result(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    config_path = _write_assistant_config(tmp_path)

    class StubPytestRunner:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        def run(self, target: str = "tests") -> SimpleNamespace:
            assert target == "tests"
            return SimpleNamespace(
                command=["python", "-m", "pytest", "tests"],
                target="tests",
                exit_code=0,
                duration_seconds=1.23,
                stdout="============================= test session starts =============================",
                stderr="",
                passed=True,
                reason="Pytest run completed successfully.",
            )

    monkeypatch.setattr("ai_test_assistant.runtime.cli.PytestRunner", StubPytestRunner)

    exit_code = run_cli(["请运行 pytest", "--run-pytest", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "识别意图：pytest_execution" in captured
    assert "真实 pytest 执行结果：" in captured
    assert "显式工具执行结果：" in captured
    assert "pytest_runner | 来源=pytest_runner | 操作=run_pytest | 风险=execute_local_command | 已执行=是 | 授权方式=CLI explicit approval" in captured
    assert "Tool 'pytest_runner' cannot run local commands during dry-run." not in captured
    assert "target：tests" in captured
    assert "exit_code：0" in captured
    assert "passed：是" in captured


def test_cli_run_pytest_executes_explicit_repo_relative_target(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    config_path = _write_assistant_config(tmp_path)

    class StubPytestRunner:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        def run(self, target: str = "tests") -> SimpleNamespace:
            assert target == "tests/test_runtime_cli.py"
            return SimpleNamespace(
                command=["python", "-m", "pytest", target],
                target=target,
                exit_code=0,
                duration_seconds=0.8,
                stdout="ok",
                stderr="",
                passed=True,
                reason="Pytest run completed successfully.",
            )

    monkeypatch.setattr("ai_test_assistant.runtime.cli.PytestRunner", StubPytestRunner)

    exit_code = run_cli(
        [
            "请运行 pytest",
            "--run-pytest",
            "tests/test_runtime_cli.py",
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "target：tests/test_runtime_cli.py" in captured


def test_cli_run_pytest_rejects_path_traversal_target(tmp_path: Path, capsys) -> None:
    config_path = _write_assistant_config(tmp_path)

    exit_code = run_cli(["请运行 pytest", "--run-pytest", "..", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 2
    assert "错误：pytest target 不合法" in captured
    assert "reason：" in captured


def test_cli_run_test_report_executes_pytest_generate_and_read_in_order(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    config_path = _write_assistant_config(tmp_path)
    calls: list[str] = []

    class StubPytestRunner:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        def run(self, target: str = "tests", *, allure_results_dir: str | None = None) -> SimpleNamespace:
            calls.append("pytest")
            assert target == "tests"
            assert allure_results_dir == "allure-results"
            return SimpleNamespace(
                command=["python", "-m", "pytest", "tests", "--alluredir=allure-results"],
                target="tests",
                exit_code=0,
                duration_seconds=1.0,
                stdout="pytest ok",
                stderr="",
                passed=True,
                reason="Pytest run completed successfully.",
            )

    class StubAllureGenerator:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        def generate(self, results_dir: str = "allure-results", report_dir: str = "allure-report") -> SimpleNamespace:
            calls.append("generate")
            return SimpleNamespace(
                command=["allure", "generate", results_dir, "-o", report_dir, "--clean"],
                results_dir=results_dir,
                report_dir=report_dir,
                exit_code=0,
                duration_seconds=0.5,
                stdout="generated",
                stderr="",
                generated=True,
                reason="Allure report generated successfully.",
                to_dict=lambda: {
                    "command": ["allure", "generate", results_dir, "-o", report_dir, "--clean"],
                    "results_dir": results_dir,
                    "report_dir": report_dir,
                    "exit_code": 0,
                    "duration_seconds": 0.5,
                    "stdout": "generated",
                    "stderr": "",
                    "generated": True,
                    "reason": "Allure report generated successfully.",
                },
            )

    class StubAllureReader:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        def read_summary(self, report_dir: str = "allure-report") -> SimpleNamespace:
            calls.append("read")
            return SimpleNamespace(
                allowed=True,
                report_dir=report_dir,
                total=3,
                passed=3,
                failed=0,
                broken=0,
                skipped=0,
                unknown=0,
                duration_ms=123,
                top_failures=[],
                reason="Read Allure report summary from existing report widgets.",
                to_dict=lambda: {
                    "allowed": True,
                    "report_dir": report_dir,
                    "total": 3,
                    "passed": 3,
                    "failed": 0,
                    "broken": 0,
                    "skipped": 0,
                    "unknown": 0,
                    "duration_ms": 123,
                    "top_failures": [],
                    "reason": "Read Allure report summary from existing report widgets.",
                },
            )

    monkeypatch.setattr("ai_test_assistant.runtime.cli.PytestRunner", StubPytestRunner)
    monkeypatch.setattr("ai_test_assistant.runtime.cli.AllureReportGenerator", StubAllureGenerator)
    monkeypatch.setattr("ai_test_assistant.runtime.cli.AllureReportReader", StubAllureReader)

    exit_code = run_cli(["运行测试并生成报告", "--run-test-report", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert calls == ["pytest", "generate", "read"]
    assert "--alluredir=allure-results" in captured
    assert "Allure 生成结果" in captured
    assert "Allure 报告摘要" in captured
    assert "total=3" in captured
    assert "pytest_runner" in captured
    assert "allure_generate" in captured
    assert "allure_report" in captured


def test_cli_run_test_report_supports_explicit_target(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)

    class StubPytestRunner:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        def run(self, target: str = "tests", *, allure_results_dir: str | None = None) -> SimpleNamespace:
            assert target == "tests/test_runtime_cli.py"
            assert allure_results_dir == "allure-results"
            return SimpleNamespace(
                command=["python", "-m", "pytest", target, "--alluredir=allure-results"],
                target=target,
                exit_code=0,
                duration_seconds=1.0,
                stdout="ok",
                stderr="",
                passed=True,
                reason="Pytest run completed successfully.",
            )

    class StubAllureGenerator:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        def generate(self, results_dir: str = "allure-results", report_dir: str = "allure-report") -> SimpleNamespace:
            return SimpleNamespace(
                command=["allure", "generate", results_dir, "-o", report_dir, "--clean"],
                results_dir=results_dir,
                report_dir=report_dir,
                exit_code=0,
                duration_seconds=0.1,
                stdout="",
                stderr="",
                generated=True,
                reason="Allure report generated successfully.",
                to_dict=lambda: {
                    "command": ["allure", "generate", results_dir, "-o", report_dir, "--clean"],
                    "results_dir": results_dir,
                    "report_dir": report_dir,
                    "exit_code": 0,
                    "duration_seconds": 0.1,
                    "stdout": "",
                    "stderr": "",
                    "generated": True,
                    "reason": "Allure report generated successfully.",
                },
            )

    class StubAllureReader:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        def read_summary(self, report_dir: str = "allure-report") -> SimpleNamespace:
            return SimpleNamespace(
                allowed=True,
                report_dir=report_dir,
                total=1,
                passed=1,
                failed=0,
                broken=0,
                skipped=0,
                unknown=0,
                duration_ms=10,
                top_failures=[],
                reason="Read Allure report summary from existing report widgets.",
                to_dict=lambda: {
                    "allowed": True,
                    "report_dir": report_dir,
                    "total": 1,
                    "passed": 1,
                    "failed": 0,
                    "broken": 0,
                    "skipped": 0,
                    "unknown": 0,
                    "duration_ms": 10,
                    "top_failures": [],
                    "reason": "Read Allure report summary from existing report widgets.",
                },
            )

    monkeypatch.setattr("ai_test_assistant.runtime.cli.PytestRunner", StubPytestRunner)
    monkeypatch.setattr("ai_test_assistant.runtime.cli.AllureReportGenerator", StubAllureGenerator)
    monkeypatch.setattr("ai_test_assistant.runtime.cli.AllureReportReader", StubAllureReader)

    exit_code = run_cli(
        [
            "运行测试并生成报告",
            "--run-test-report",
            "tests/test_runtime_cli.py",
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "target：tests/test_runtime_cli.py" in captured


def test_cli_run_test_report_skips_allure_when_pytest_fails(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)

    class StubPytestRunner:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        def run(self, target: str = "tests", *, allure_results_dir: str | None = None) -> SimpleNamespace:
            return SimpleNamespace(
                command=["python", "-m", "pytest", "tests", "--alluredir=allure-results"],
                target="tests",
                exit_code=1,
                duration_seconds=1.0,
                stdout="failed",
                stderr="",
                passed=False,
                reason="Pytest run completed with failures.",
            )

    class StubAllureGenerator:
        def __init__(self, repo_root: Path) -> None:
            raise AssertionError("Allure generate must not run after pytest failure.")

    class StubAllureReader:
        def __init__(self, repo_root: Path) -> None:
            raise AssertionError("Allure read must not run after pytest failure.")

    monkeypatch.setattr("ai_test_assistant.runtime.cli.PytestRunner", StubPytestRunner)
    monkeypatch.setattr("ai_test_assistant.runtime.cli.AllureReportGenerator", StubAllureGenerator)
    monkeypatch.setattr("ai_test_assistant.runtime.cli.AllureReportReader", StubAllureReader)

    exit_code = run_cli(["运行测试并生成报告", "--run-test-report", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "exit_code：1" in captured
    assert "Skipped because pytest failed." in captured
    assert "generated=否" in captured


def test_cli_run_test_report_skips_summary_when_allure_generate_fails(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)

    class StubPytestRunner:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        def run(self, target: str = "tests", *, allure_results_dir: str | None = None) -> SimpleNamespace:
            return SimpleNamespace(
                command=["python", "-m", "pytest", "tests", "--alluredir=allure-results"],
                target="tests",
                exit_code=0,
                duration_seconds=1.0,
                stdout="ok",
                stderr="",
                passed=True,
                reason="Pytest run completed successfully.",
            )

    class StubAllureGenerator:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        def generate(self, results_dir: str = "allure-results", report_dir: str = "allure-report") -> SimpleNamespace:
            return SimpleNamespace(
                command=["allure", "generate", results_dir, "-o", report_dir, "--clean"],
                results_dir=results_dir,
                report_dir=report_dir,
                exit_code=1,
                duration_seconds=0.1,
                stdout="",
                stderr="bad",
                generated=False,
                reason="Allure report generation failed.",
                to_dict=lambda: {
                    "command": ["allure", "generate", results_dir, "-o", report_dir, "--clean"],
                    "results_dir": results_dir,
                    "report_dir": report_dir,
                    "exit_code": 1,
                    "duration_seconds": 0.1,
                    "stdout": "",
                    "stderr": "bad",
                    "generated": False,
                    "reason": "Allure report generation failed.",
                },
            )

    class StubAllureReader:
        def __init__(self, repo_root: Path) -> None:
            raise AssertionError("Allure read must not run after generation failure.")

    monkeypatch.setattr("ai_test_assistant.runtime.cli.PytestRunner", StubPytestRunner)
    monkeypatch.setattr("ai_test_assistant.runtime.cli.AllureReportGenerator", StubAllureGenerator)
    monkeypatch.setattr("ai_test_assistant.runtime.cli.AllureReportReader", StubAllureReader)

    exit_code = run_cli(["运行测试并生成报告", "--run-test-report", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "Allure report generation failed." in captured
    assert "Skipped because Allure report generation failed." in captured


def test_cli_plain_dry_run_does_not_execute_test_report_chain(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)

    class StubPytestRunner:
        def __init__(self, repo_root: Path) -> None:
            raise AssertionError("Pytest must not run without --run-test-report.")

    monkeypatch.setattr("ai_test_assistant.runtime.cli.PytestRunner", StubPytestRunner)

    exit_code = run_cli(["运行测试并生成报告", "--dry-run", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "真实 pytest 执行结果" not in captured
    assert "Allure 生成结果" not in captured


def test_cli_run_test_report_rejects_extra_pytest_arguments(tmp_path: Path, capsys) -> None:
    config_path = _write_assistant_config(tmp_path)

    exit_code = run_cli(["运行测试并生成报告", "--run-test-report", "tests --maxfail=1", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 2
    assert "pytest target 不合法" in captured
    assert "extra arguments" in captured


def test_cli_plain_github_tool_research_dry_run_still_requires_external_network_approval(
    tmp_path: Path,
    capsys,
) -> None:
    config_path = _write_assistant_config(tmp_path)

    exit_code = run_cli(["读取 GitHub README 并分析", "--dry-run", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "显式工具执行结果：" not in captured
    assert "github_read | 状态=enabled | 风险=external_network | 允许执行=否 | 需要确认=是" in captured
    assert "Tool 'github_read' needs external network approval." in captured
