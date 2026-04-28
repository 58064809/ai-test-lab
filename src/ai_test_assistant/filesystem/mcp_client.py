from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_test_assistant.filesystem.adapter import FilesystemReadResult
from ai_test_assistant.filesystem.policy import FilesystemReadPolicy


class FilesystemMcpReadClient:
    """Read a single allowed repository file through the official MCP Python SDK."""

    DEFAULT_MAX_BYTES = 128 * 1024
    _EXACT_READ_TOOL_NAMES = ("read_text_file", "read_file")
    _BLOCKED_TOOL_NAME_TOKENS = (
        "write",
        "delete",
        "create",
        "mkdir",
        "move",
        "rename",
        "directory",
        "glob",
        "search",
        "multiple",
    )

    def __init__(
        self,
        repo_root: Path,
        policy: FilesystemReadPolicy | None = None,
        max_bytes: int = DEFAULT_MAX_BYTES,
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.policy = policy or FilesystemReadPolicy()
        self.max_bytes = max_bytes

    async def read_text(self, repo_relative_path: str) -> FilesystemReadResult:
        decision = self.policy.evaluate(repo_relative_path)
        if not decision.allowed or decision.normalized_path is None:
            return FilesystemReadResult(
                allowed=False,
                path=decision.normalized_path,
                content=None,
                reason=decision.reason,
                truncated=False,
            )

        normalized_path = decision.normalized_path
        target_path = (self.repo_root / normalized_path).resolve()
        if not self._is_within_repo_root(target_path):
            return FilesystemReadResult(
                allowed=False,
                path=normalized_path,
                content=None,
                reason="Resolved path is outside the repository root.",
                truncated=False,
            )

        if not target_path.exists():
            return FilesystemReadResult(
                allowed=False,
                path=normalized_path,
                content=None,
                reason="Target file does not exist.",
                truncated=False,
            )

        if not target_path.is_file():
            return FilesystemReadResult(
                allowed=False,
                path=normalized_path,
                content=None,
                reason="Target path is not a regular file.",
                truncated=False,
            )

        try:
            content = await self._read_from_server(target_path)
        except ModuleNotFoundError:
            return FilesystemReadResult(
                allowed=False,
                path=normalized_path,
                content=None,
                reason="Python MCP SDK package 'mcp' is not installed. Install project dependencies first.",
                truncated=False,
            )
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            return FilesystemReadResult(
                allowed=False,
                path=normalized_path,
                content=None,
                reason=f"filesystem MCP read failed: {exc}",
                truncated=False,
            )

        truncated_content, truncated = self._truncate_text(content)
        reason = "Read allowed through filesystem MCP."
        if truncated:
            reason = f"Read allowed through filesystem MCP, content truncated to {self.max_bytes} bytes."

        return FilesystemReadResult(
            allowed=True,
            path=normalized_path,
            content=truncated_content,
            reason=reason,
            truncated=truncated,
        )

    async def _read_from_server(self, target_path: Path) -> str:
        ClientSession, StdioServerParameters, stdio_client = self._load_sdk()

        server_params = StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                str(self.repo_root),
            ],
        )

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tool_name = await self._select_read_tool(session)
                tool_result = await session.call_tool(tool_name, {"path": str(target_path)})
        return self._extract_text_content(tool_result)

    def _load_sdk(self) -> tuple[Any, Any, Any]:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        return ClientSession, StdioServerParameters, stdio_client

    async def _select_read_tool(self, session: Any) -> str:
        tools_result = await session.list_tools()
        tools = list(getattr(tools_result, "tools", []) or [])

        for exact_name in self._EXACT_READ_TOOL_NAMES:
            for tool in tools:
                if getattr(tool, "name", "") != exact_name:
                    continue
                if self._tool_accepts_single_path(tool):
                    return exact_name

        readonly_candidates = [
            getattr(tool, "name", "")
            for tool in tools
            if self._tool_accepts_single_path(tool) and self._looks_like_single_file_read_tool(tool)
        ]
        if len(readonly_candidates) == 1:
            return readonly_candidates[0]

        available_names = ", ".join(sorted(getattr(tool, "name", "") for tool in tools if getattr(tool, "name", "")))
        raise RuntimeError(
            "Unable to confirm a safe single-file read tool from filesystem MCP server."
            f" Available tools: {available_names or 'none'}."
        )

    def _tool_accepts_single_path(self, tool: Any) -> bool:
        input_schema = getattr(tool, "inputSchema", None) or getattr(tool, "input_schema", None)
        if not isinstance(input_schema, dict):
            return False

        properties = input_schema.get("properties")
        if not isinstance(properties, dict):
            return False

        if "path" not in properties:
            return False

        tool_name = getattr(tool, "name", "")
        lowered_name = tool_name.lower()
        if any(token in lowered_name for token in self._BLOCKED_TOOL_NAME_TOKENS):
            return False

        return True

    def _looks_like_single_file_read_tool(self, tool: Any) -> bool:
        tool_name = str(getattr(tool, "name", "")).lower()
        if not tool_name:
            return False
        if "read" not in tool_name or "file" not in tool_name:
            return False
        if any(token in tool_name for token in self._BLOCKED_TOOL_NAME_TOKENS):
            return False

        annotations = getattr(tool, "annotations", None)
        if annotations is None:
            return False

        if isinstance(annotations, dict):
            return bool(
                annotations.get("readOnlyHint")
                or annotations.get("read_only_hint")
            )

        return bool(
            getattr(annotations, "readOnlyHint", False)
            or getattr(annotations, "read_only_hint", False)
        )

    def _extract_text_content(self, tool_result: Any) -> str:
        if getattr(tool_result, "isError", False) or getattr(tool_result, "is_error", False):
            message = self._join_text_chunks(getattr(tool_result, "content", None))
            raise RuntimeError(message or "filesystem MCP tool returned an error.")

        structured_content = (
            getattr(tool_result, "structuredContent", None)
            or getattr(tool_result, "structured_content", None)
        )
        if isinstance(structured_content, dict):
            for key in ("content", "text"):
                value = structured_content.get(key)
                if isinstance(value, str):
                    return value

        text = self._join_text_chunks(getattr(tool_result, "content", None))
        if text:
            return text

        raise RuntimeError("filesystem MCP tool did not return readable text content.")

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

    def _truncate_text(self, content: str) -> tuple[str, bool]:
        raw_bytes = content.encode("utf-8")
        if len(raw_bytes) <= self.max_bytes:
            return content, False

        truncated_bytes = raw_bytes[: self.max_bytes]
        truncated_text = truncated_bytes.decode("utf-8", errors="ignore")
        return truncated_text, True

    def _is_within_repo_root(self, path: Path) -> bool:
        try:
            path.relative_to(self.repo_root)
            return True
        except ValueError:
            return False
