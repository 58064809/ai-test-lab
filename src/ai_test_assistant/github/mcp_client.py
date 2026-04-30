from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any
import os
import re


@dataclass(slots=True)
class GitHubReadResult:
    allowed: bool
    operation: str
    repository: str | None
    target: str | None
    content: str | None
    reason: str
    truncated: bool = False


class GitHubMcpReadClient:
    """Read explicitly requested GitHub content through the official GitHub MCP server."""

    DEFAULT_MAX_BYTES = 128 * 1024
    _REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
    _READ_FILE_TOOL_NAMES = ("get_file_contents",)
    _REPOSITORY_INFO_TOOL_NAMES = ("get_repository", "get_repository_info")
    _BLOCKED_PATH_TOKENS = ("token", "secret", "password")
    _BLOCKED_TOOL_NAME_TOKENS = (
        "add",
        "assign",
        "close",
        "comment",
        "create",
        "delete",
        "edit",
        "merge",
        "push",
        "remove",
        "update",
        "write",
    )

    def __init__(self, max_bytes: int = DEFAULT_MAX_BYTES) -> None:
        self.max_bytes = max_bytes

    async def read_repository_info(self, repository: str) -> GitHubReadResult:
        repository_decision = self._validate_repository(repository)
        if repository_decision is not None:
            return repository_decision

        try:
            content = await self._read_repository_info_from_server(repository)
        except ModuleNotFoundError:
            return self._refused(
                operation="read_repository_info",
                repository=repository,
                target=None,
                reason="Python MCP SDK package 'mcp' is not installed. Install project dependencies first.",
            )
        except BaseExceptionGroup as exc:  # pragma: no cover - exercised through read_file
            return self._refused(
                operation="read_repository_info",
                repository=repository,
                target=None,
                reason=f"github MCP repository read failed: {self._format_exception_for_diagnostic(exc)}",
            )
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            return self._refused(
                operation="read_repository_info",
                repository=repository,
                target=None,
                reason=f"github MCP repository read failed: {self._format_exception_for_diagnostic(exc)}",
            )

        truncated_content, truncated = self._truncate_text(content)
        reason = "Read allowed through GitHub MCP."
        if truncated:
            reason = f"Read allowed through GitHub MCP, content truncated to {self.max_bytes} bytes."
        return GitHubReadResult(
            allowed=True,
            operation="read_repository_info",
            repository=repository,
            target=None,
            content=truncated_content,
            reason=reason,
            truncated=truncated,
        )

    async def read_file(self, repository: str, path: str, ref: str | None = None) -> GitHubReadResult:
        repository_decision = self._validate_repository(repository)
        if repository_decision is not None:
            return repository_decision

        path_decision = self._validate_file_path(repository, path)
        if path_decision is not None:
            return path_decision

        normalized_path = self._normalize_file_path(path)
        try:
            content = await self._read_file_from_server(repository, normalized_path, ref)
        except ModuleNotFoundError:
            return self._refused(
                operation="read_file",
                repository=repository,
                target=normalized_path,
                reason="Python MCP SDK package 'mcp' is not installed. Install project dependencies first.",
            )
        except BaseExceptionGroup as exc:
            return self._refused(
                operation="read_file",
                repository=repository,
                target=normalized_path,
                reason=f"github MCP file read failed: {self._format_exception_for_diagnostic(exc)}",
            )
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            return self._refused(
                operation="read_file",
                repository=repository,
                target=normalized_path,
                reason=f"github MCP file read failed: {self._format_exception_for_diagnostic(exc)}",
            )

        truncated_content, truncated = self._truncate_text(content)
        reason = "Read allowed through GitHub MCP."
        if truncated:
            reason = f"Read allowed through GitHub MCP, content truncated to {self.max_bytes} bytes."
        return GitHubReadResult(
            allowed=True,
            operation="read_file",
            repository=repository,
            target=normalized_path,
            content=truncated_content,
            reason=reason,
            truncated=truncated,
        )

    async def _read_repository_info_from_server(self, repository: str) -> str:
        ClientSession, StdioServerParameters, stdio_client = self._load_sdk()
        owner, repo = repository.split("/", maxsplit=1)
        server_params = self._build_server_params()

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tool_name = await self._select_repository_info_tool(session)
                tool_result = await session.call_tool(tool_name, {"owner": owner, "repo": repo})
        return self._extract_text_content(tool_result)

    async def _read_file_from_server(self, repository: str, path: str, ref: str | None) -> str:
        ClientSession, StdioServerParameters, stdio_client = self._load_sdk()
        owner, repo = repository.split("/", maxsplit=1)
        arguments = {"owner": owner, "repo": repo, "path": path}
        if ref:
            arguments["ref"] = ref

        server_params = self._build_server_params()
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tool_name = await self._select_read_file_tool(session)
                tool_result = await session.call_tool(tool_name, arguments)
        return self._extract_text_content(tool_result)

    def _load_sdk(self) -> tuple[Any, Any, Any]:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        return ClientSession, StdioServerParameters, stdio_client

    def _build_server_params(self) -> Any:
        _, StdioServerParameters, _ = self._load_sdk()
        return StdioServerParameters(
            command="docker",
            args=[
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
            ],
            env=self._build_server_environment(),
        )

    def _build_server_environment(self) -> dict[str, str] | None:
        token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
        if token is None:
            return None
        return {"GITHUB_PERSONAL_ACCESS_TOKEN": token}

    async def _select_read_file_tool(self, session: Any) -> str:
        return await self._select_exact_read_tool(session, self._READ_FILE_TOOL_NAMES, "file read")

    async def _select_repository_info_tool(self, session: Any) -> str:
        return await self._select_exact_read_tool(session, self._REPOSITORY_INFO_TOOL_NAMES, "repository info read")

    async def _select_exact_read_tool(self, session: Any, allowed_names: tuple[str, ...], operation: str) -> str:
        tools_result = await session.list_tools()
        tools = list(getattr(tools_result, "tools", []) or [])
        for allowed_name in allowed_names:
            for tool in tools:
                if getattr(tool, "name", "") == allowed_name and self._looks_read_only(tool):
                    return allowed_name

        available_names = ", ".join(sorted(getattr(tool, "name", "") for tool in tools if getattr(tool, "name", "")))
        raise RuntimeError(
            f"Unable to confirm a safe GitHub MCP {operation} tool."
            f" Available tools: {available_names or 'none'}."
        )

    def _looks_read_only(self, tool: Any) -> bool:
        tool_name = str(getattr(tool, "name", "")).lower()
        if not tool_name:
            return False
        if any(token in tool_name for token in self._BLOCKED_TOOL_NAME_TOKENS):
            return False
        if tool_name in self._READ_FILE_TOOL_NAMES or tool_name in self._REPOSITORY_INFO_TOOL_NAMES:
            return True

        annotations = getattr(tool, "annotations", None)
        if isinstance(annotations, dict):
            return bool(annotations.get("readOnlyHint") or annotations.get("read_only_hint"))
        return bool(
            getattr(annotations, "readOnlyHint", False)
            or getattr(annotations, "read_only_hint", False)
        )

    def _extract_text_content(self, tool_result: Any) -> str:
        if getattr(tool_result, "isError", False) or getattr(tool_result, "is_error", False):
            message = self._join_text_chunks(getattr(tool_result, "content", None))
            raise RuntimeError(message or "GitHub MCP tool returned an error.")

        structured_content = (
            getattr(tool_result, "structuredContent", None)
            or getattr(tool_result, "structured_content", None)
        )
        if isinstance(structured_content, dict):
            for key in ("content", "text", "message"):
                value = structured_content.get(key)
                if isinstance(value, str):
                    return value
            return str(structured_content)

        text = self._join_text_chunks(getattr(tool_result, "content", None))
        if text:
            return text

        raise RuntimeError("GitHub MCP tool did not return readable text content.")

    def _join_text_chunks(self, content_items: Any) -> str:
        if not isinstance(content_items, list):
            return ""

        text_chunks: list[str] = []
        for item in content_items:
            item_type = getattr(item, "type", None)
            item_text = getattr(item, "text", None)
            if item_type == "text" and isinstance(item_text, str):
                text_chunks.append(item_text)
                continue
            if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str):
                text_chunks.append(item["text"])
        return "\n".join(text_chunks)

    def _format_exception_for_diagnostic(self, exc: BaseException) -> str:
        message = self._format_single_exception(exc)
        if isinstance(exc, BaseExceptionGroup):
            children = [
                self._format_exception_for_diagnostic(child)
                for child in exc.exceptions
            ]
            if children:
                message = f"{message}; sub-exceptions: {'; '.join(children)}"
        return self._redact_sensitive_text(message)

    def _format_single_exception(self, exc: BaseException) -> str:
        message = str(exc).strip()
        exc_type = type(exc).__name__
        if message:
            return f"{exc_type}: {message}"
        return exc_type

    def _redact_sensitive_text(self, text: str) -> str:
        token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
        if token:
            return text.replace(token, "<redacted>")
        return text

    def _validate_repository(self, repository: str | None) -> GitHubReadResult | None:
        repository_text = (repository or "").strip()
        if not repository_text:
            return self._refused(
                operation="validate_repository",
                repository=None,
                target=None,
                reason="GitHub repository must be explicitly provided.",
            )
        if not self._REPOSITORY_PATTERN.fullmatch(repository_text):
            return self._refused(
                operation="validate_repository",
                repository=repository_text,
                target=None,
                reason="GitHub repository must use owner/repo format.",
            )
        return None

    def _validate_file_path(self, repository: str, path: str | None) -> GitHubReadResult | None:
        path_text = (path or "").strip()
        if not path_text:
            return self._refused(
                operation="read_file",
                repository=repository,
                target=None,
                reason="GitHub file path must be explicitly provided.",
            )
        normalized = self._normalize_file_path(path_text)
        if path_text.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:[\\/]", path_text):
            return self._refused("read_file", repository, path_text, "Absolute GitHub file paths are blocked.")
        parts = PurePosixPath(normalized).parts
        if ".." in parts:
            return self._refused("read_file", repository, normalized, "Path traversal is blocked.")
        if normalized.endswith("/"):
            return self._refused("read_file", repository, normalized, "Directory reads are not supported.")
        if self._is_sensitive_path(normalized):
            return self._refused("read_file", repository, normalized, "Sensitive GitHub file path is blocked.")
        return None

    def _normalize_file_path(self, path: str) -> str:
        return path.strip().replace("\\", "/")

    def _is_sensitive_path(self, path: str) -> bool:
        lowered = path.lower()
        name_parts = [part for part in PurePosixPath(lowered).parts if part not in ("", ".")]
        if any(part == ".env" or part.startswith(".env.") for part in name_parts):
            return True
        return any(token in lowered for token in self._BLOCKED_PATH_TOKENS)

    def _truncate_text(self, content: str) -> tuple[str, bool]:
        raw_bytes = content.encode("utf-8")
        if len(raw_bytes) <= self.max_bytes:
            return content, False
        truncated_bytes = raw_bytes[: self.max_bytes]
        return truncated_bytes.decode("utf-8", errors="ignore"), True

    def _refused(
        self,
        operation: str,
        repository: str | None,
        target: str | None,
        reason: str,
    ) -> GitHubReadResult:
        return GitHubReadResult(
            allowed=False,
            operation=operation,
            repository=repository,
            target=target,
            content=None,
            reason=reason,
            truncated=False,
        )
