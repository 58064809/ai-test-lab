from __future__ import annotations

import asyncio
from types import SimpleNamespace

from ai_test_assistant.github import GitHubMcpReadClient


def test_github_mcp_client_requires_owner_repo_format() -> None:
    client = GitHubMcpReadClient()

    result = asyncio.run(client.read_file("ai-test-lab", "README.md"))

    assert result.allowed is False
    assert result.repository == "ai-test-lab"
    assert result.reason == "GitHub repository must use owner/repo format."


def test_github_mcp_client_refuses_empty_repository() -> None:
    client = GitHubMcpReadClient()

    result = asyncio.run(client.read_file("", "README.md"))

    assert result.allowed is False
    assert result.repository is None
    assert result.reason == "GitHub repository must be explicitly provided."


def test_github_mcp_client_refuses_absolute_path_without_starting_server() -> None:
    client = GitHubMcpReadClient()
    called = False

    async def fake_read_file_from_server(_repository: str, _path: str, _ref: str | None) -> str:
        nonlocal called
        called = True
        return "should-not-run"

    client._read_file_from_server = fake_read_file_from_server  # type: ignore[method-assign]

    result = asyncio.run(client.read_file("58064809/ai-test-lab", "/README.md"))

    assert result.allowed is False
    assert result.reason == "Absolute GitHub file paths are blocked."
    assert called is False


def test_github_mcp_client_refuses_path_traversal_without_starting_server() -> None:
    client = GitHubMcpReadClient()
    called = False

    async def fake_read_file_from_server(_repository: str, _path: str, _ref: str | None) -> str:
        nonlocal called
        called = True
        return "should-not-run"

    client._read_file_from_server = fake_read_file_from_server  # type: ignore[method-assign]

    result = asyncio.run(client.read_file("58064809/ai-test-lab", "../README.md"))

    assert result.allowed is False
    assert result.reason == "Path traversal is blocked."
    assert called is False


def test_github_mcp_client_refuses_sensitive_paths_without_starting_server() -> None:
    client = GitHubMcpReadClient()
    called = False

    async def fake_read_file_from_server(_repository: str, _path: str, _ref: str | None) -> str:
        nonlocal called
        called = True
        return "should-not-run"

    client._read_file_from_server = fake_read_file_from_server  # type: ignore[method-assign]

    for path in [".env", "docs/token.txt", "secret/config.md", "passwords/readme.md"]:
        result = asyncio.run(client.read_file("58064809/ai-test-lab", path))
        assert result.allowed is False
        assert result.reason == "Sensitive GitHub file path is blocked."
    assert called is False


def test_github_mcp_client_reads_allowed_file_through_server_hook() -> None:
    client = GitHubMcpReadClient()
    captured: dict[str, str | None] = {}

    async def fake_read_file_from_server(repository: str, path: str, ref: str | None) -> str:
        captured["repository"] = repository
        captured["path"] = path
        captured["ref"] = ref
        return "hello"

    client._read_file_from_server = fake_read_file_from_server  # type: ignore[method-assign]

    result = asyncio.run(client.read_file("58064809/ai-test-lab", "README.md", ref="master"))

    assert result.allowed is True
    assert result.repository == "58064809/ai-test-lab"
    assert result.target == "README.md"
    assert result.content == "hello"
    assert result.reason == "Read allowed through GitHub MCP."
    assert captured == {"repository": "58064809/ai-test-lab", "path": "README.md", "ref": "master"}


def test_github_mcp_client_only_selects_explicit_read_tool() -> None:
    client = GitHubMcpReadClient()

    class Session:
        async def list_tools(self) -> SimpleNamespace:
            return SimpleNamespace(
            tools=[
                SimpleNamespace(name="create_issue", annotations={"readOnlyHint": False}),
                SimpleNamespace(name="get_file_contents", annotations={"readOnlyHint": True}),
            ]
        )

    tool_name = asyncio.run(client._select_read_file_tool(Session()))

    assert tool_name == "get_file_contents"


def test_github_mcp_client_refuses_when_read_tool_cannot_be_confirmed() -> None:
    client = GitHubMcpReadClient()

    class Session:
        async def list_tools(self) -> SimpleNamespace:
            return SimpleNamespace(
            tools=[
                SimpleNamespace(name="search_code", annotations={"readOnlyHint": True}),
                SimpleNamespace(name="create_issue", annotations={"readOnlyHint": False}),
            ]
        )

    try:
        asyncio.run(client._select_read_file_tool(Session()))
    except RuntimeError as exc:
        assert "Unable to confirm a safe GitHub MCP file read tool" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")
