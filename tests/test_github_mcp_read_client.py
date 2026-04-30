from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

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


def test_github_mcp_client_expands_exception_group_diagnostics() -> None:
    client = GitHubMcpReadClient()

    async def fake_read_file_from_server(_repository: str, _path: str, _ref: str | None) -> str:
        raise ExceptionGroup(
            "unhandled errors in a TaskGroup",
            [
                ValueError("missing token"),
                RuntimeError("docker exited"),
            ],
        )

    client._read_file_from_server = fake_read_file_from_server  # type: ignore[method-assign]

    result = asyncio.run(client.read_file("58064809/ai-test-lab", "README.md"))

    assert result.allowed is False
    assert "github MCP file read failed:" in result.reason
    assert "ExceptionGroup: unhandled errors in a TaskGroup (2 sub-exceptions)" in result.reason
    assert "ValueError: missing token" in result.reason
    assert "RuntimeError: docker exited" in result.reason


def test_github_mcp_client_redacts_token_from_exception_diagnostics(monkeypatch) -> None:
    client = GitHubMcpReadClient()
    monkeypatch.setenv("GITHUB_PERSONAL_ACCESS_TOKEN", "ghp_secret_value")

    async def fake_read_file_from_server(_repository: str, _path: str, _ref: str | None) -> str:
        raise RuntimeError("token ghp_secret_value was rejected")

    client._read_file_from_server = fake_read_file_from_server  # type: ignore[method-assign]

    result = asyncio.run(client.read_file("58064809/ai-test-lab", "README.md"))

    assert result.allowed is False
    assert "ghp_secret_value" not in result.reason
    assert "token <redacted> was rejected" in result.reason


def test_github_mcp_client_passes_token_to_stdio_env_not_docker_args(monkeypatch) -> None:
    client = GitHubMcpReadClient()
    monkeypatch.setenv("GITHUB_PERSONAL_ACCESS_TOKEN", "ghp_secret_value")

    server_params = client._build_server_params()

    assert server_params.env == {"GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_secret_value"}
    assert "ghp_secret_value" not in server_params.args
    assert server_params.args == [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "-e",
        "GITHUB_READ_ONLY=1",
        "-e",
        "GITHUB_TOOLS=get_file_contents",
        "ghcr.io/github/github-mcp-server",
    ]


def test_github_mcp_client_uses_official_get_file_contents_arguments() -> None:
    client = GitHubMcpReadClient()
    captured: dict[str, Any] = {}

    class StdioContext:
        async def __aenter__(self) -> tuple[object, object]:
            return object(), object()

        async def __aexit__(self, *_exc: object) -> None:
            return None

    class Session:
        def __init__(self, _read_stream: object, _write_stream: object) -> None:
            pass

        async def __aenter__(self) -> "Session":
            return self

        async def __aexit__(self, *_exc: object) -> None:
            return None

        async def initialize(self) -> None:
            return None

        async def list_tools(self) -> SimpleNamespace:
            return SimpleNamespace(
                tools=[
                    SimpleNamespace(name="get_file_contents", annotations={"readOnlyHint": True}),
                ]
            )

        async def call_tool(self, tool_name: str, arguments: dict[str, str]) -> SimpleNamespace:
            captured["tool_name"] = tool_name
            captured["arguments"] = arguments
            return SimpleNamespace(content=[SimpleNamespace(type="text", text="hello")])

    class ServerParameters:
        def __init__(self, **_kwargs: object) -> None:
            pass

    def stdio_client(_server_params: object) -> StdioContext:
        return StdioContext()

    client._load_sdk = lambda: (Session, ServerParameters, stdio_client)  # type: ignore[method-assign]

    content = asyncio.run(client._read_file_from_server("58064809/ai-test-lab", "README.md", "master"))

    assert content == "hello"
    assert captured == {
        "tool_name": "get_file_contents",
        "arguments": {
            "owner": "58064809",
            "repo": "ai-test-lab",
            "path": "README.md",
            "ref": "master",
        },
    }


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
