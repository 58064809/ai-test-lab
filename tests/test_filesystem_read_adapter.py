from __future__ import annotations

from pathlib import Path

from ai_test_assistant.filesystem import LocalFilesystemReadAdapter


def test_adapter_reads_allowed_readme(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("project status", encoding="utf-8")

    result = LocalFilesystemReadAdapter(tmp_path).read_text("README.md")

    assert result.allowed is True
    assert result.path == "README.md"
    assert result.content == "project status"
    assert result.truncated is False


def test_adapter_reads_allowed_docs_file(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "example.md").write_text("doc text", encoding="utf-8")

    result = LocalFilesystemReadAdapter(tmp_path).read_text("docs/example.md")

    assert result.allowed is True
    assert result.path == "docs/example.md"
    assert result.content == "doc text"


def test_adapter_blocks_sensitive_env_file(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("SECRET=1", encoding="utf-8")

    result = LocalFilesystemReadAdapter(tmp_path).read_text(".env")

    assert result.allowed is False
    assert result.content is None
    assert "Sensitive file" in result.reason


def test_adapter_blocks_git_config(tmp_path: Path) -> None:
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]", encoding="utf-8")

    result = LocalFilesystemReadAdapter(tmp_path).read_text(".git/config")

    assert result.allowed is False
    assert result.content is None


def test_adapter_blocks_outside_path(tmp_path: Path) -> None:
    result = LocalFilesystemReadAdapter(tmp_path).read_text("../outside.txt")

    assert result.allowed is False
    assert result.path is None


def test_adapter_blocks_secret_pattern_path(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "secret-token.txt").write_text("x", encoding="utf-8")

    result = LocalFilesystemReadAdapter(tmp_path).read_text("docs/secret-token.txt")

    assert result.allowed is False
    assert result.content is None


def test_adapter_returns_structured_rejection_for_missing_file(tmp_path: Path) -> None:
    result = LocalFilesystemReadAdapter(tmp_path).read_text("README.md")

    assert result.allowed is False
    assert result.path == "README.md"
    assert result.reason == "Target file does not exist."


def test_adapter_rejects_binary_file(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_bytes(b"\x00\x01\x02")

    result = LocalFilesystemReadAdapter(tmp_path).read_text("README.md")

    assert result.allowed is False
    assert result.content is None
    assert "Binary files" in result.reason


def test_adapter_truncates_large_text_file(tmp_path: Path) -> None:
    content = "a" * 40
    (tmp_path / "README.md").write_text(content, encoding="utf-8")

    result = LocalFilesystemReadAdapter(tmp_path, max_bytes=16).read_text("README.md")

    assert result.allowed is True
    assert result.truncated is True
    assert result.content == "a" * 16
