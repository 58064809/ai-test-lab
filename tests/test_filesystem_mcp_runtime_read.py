from __future__ import annotations

import asyncio
from pathlib import Path

from ai_test_assistant.filesystem import FilesystemMcpReadClient


def test_mcp_client_refuses_env_without_starting_server(tmp_path: Path) -> None:
    client = FilesystemMcpReadClient(repo_root=tmp_path)
    called = False

    async def fake_read_from_server(_target_path: Path) -> str:
        nonlocal called
        called = True
        return "should-not-run"

    client._read_from_server = fake_read_from_server  # type: ignore[method-assign]

    result = asyncio.run(client.read_text(".env"))

    assert result.allowed is False
    assert result.path == ".env"
    assert result.reason == "Sensitive file is blocked."
    assert called is False


def test_mcp_client_refuses_git_config_without_starting_server(tmp_path: Path) -> None:
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]\nrepositoryformatversion = 0\n", encoding="utf-8")
    client = FilesystemMcpReadClient(repo_root=tmp_path)
    called = False

    async def fake_read_from_server(_target_path: Path) -> str:
        nonlocal called
        called = True
        return "should-not-run"

    client._read_from_server = fake_read_from_server  # type: ignore[method-assign]

    result = asyncio.run(client.read_text(".git/config"))

    assert result.allowed is False
    assert result.path == ".git/config"
    assert result.reason == "Sensitive directory is blocked."
    assert called is False


def test_mcp_client_reads_allowed_file_through_server_hook(tmp_path: Path) -> None:
    readme_path = tmp_path / "README.md"
    readme_path.write_text("line1\nline2\nline3", encoding="utf-8", newline="\n")
    client = FilesystemMcpReadClient(repo_root=tmp_path)
    captured_path: Path | None = None

    async def fake_read_from_server(target_path: Path) -> str:
        nonlocal captured_path
        captured_path = target_path
        return "line1\nline2\nline3"

    client._read_from_server = fake_read_from_server  # type: ignore[method-assign]

    result = asyncio.run(client.read_text("README.md"))

    assert result.allowed is True
    assert result.path == "README.md"
    assert result.content == "line1\nline2\nline3"
    assert result.reason == "Read allowed through filesystem MCP."
    assert result.truncated is False
    assert captured_path == readme_path.resolve()


def test_mcp_client_returns_structured_reason_when_sdk_missing(tmp_path: Path) -> None:
    readme_path = tmp_path / "README.md"
    readme_path.write_text("line1", encoding="utf-8")
    client = FilesystemMcpReadClient(repo_root=tmp_path)

    async def fake_read_from_server(_target_path: Path) -> str:
        raise ModuleNotFoundError("No module named 'mcp'")

    client._read_from_server = fake_read_from_server  # type: ignore[method-assign]

    result = asyncio.run(client.read_text("README.md"))

    assert result.allowed is False
    assert result.path == "README.md"
    assert "package 'mcp' is not installed" in result.reason
