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


def test_cli_parser_supports_github_read_arguments() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "读取 GitHub README 并分析",
            "--github-repo",
            "58064809/ai-test-lab",
            "--github-read-file",
            "README.md",
            "--github-ref",
            "master",
            "--config",
            "configs/assistant.yaml",
        ]
    )

    assert args.github_repo == "58064809/ai-test-lab"
    assert args.github_read_file == "README.md"
    assert args.github_ref == "master"


def test_cli_github_read_requires_explicit_repo(tmp_path: Path, capsys) -> None:
    config_path = _write_assistant_config(tmp_path)

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


def test_cli_github_repo_without_read_file_does_not_trigger_github_read(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    config_path = _write_assistant_config(tmp_path)
    called = False

    class StubGitHubClient:
        async def read_file(self, repository: str, path: str, ref: str | None = None) -> SimpleNamespace:
            nonlocal called
            called = True
            return SimpleNamespace()

    monkeypatch.setattr("ai_test_assistant.runtime.cli.GitHubMcpReadClient", StubGitHubClient)

    exit_code = run_cli(
        [
            "读取 GitHub README 并分析",
            "--dry-run",
            "--github-repo",
            "58064809/ai-test-lab",
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert called is False
    assert "github_mcp" not in captured


def test_cli_dry_run_reads_single_allowed_file_via_github_mcp_with_preview_by_default(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    config_path = _write_assistant_config(tmp_path)

    class StubGitHubClient:
        async def read_file(self, repository: str, path: str, ref: str | None = None) -> SimpleNamespace:
            assert repository == "58064809/ai-test-lab"
            assert path == "README.md"
            assert ref == "master"
            return SimpleNamespace(
                allowed=True,
                operation="read_file",
                repository=repository,
                target=path,
                content="line1\nline2\nline3",
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
    assert "github_mcp" in captured
    assert "README.md" in captured
    assert "line1" in captured
    assert "Read allowed through GitHub MCP." in captured


def test_cli_github_write_memory_keeps_only_input_file_metadata(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)
    db_path = tmp_path / "memory.sqlite3"

    class StubGitHubClient:
        async def read_file(self, repository: str, path: str, ref: str | None = None) -> SimpleNamespace:
            return SimpleNamespace(
                allowed=True,
                operation="read_file",
                repository=repository,
                target=path,
                content="line1\nline2\nline3",
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
    assert input_files[0]["content_length"] == len("line1\nline2\nline3")
    assert "content" not in input_files[0]
