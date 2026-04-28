from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_test_assistant.filesystem.policy import FilesystemReadPolicy


@dataclass(slots=True)
class FilesystemReadResult:
    allowed: bool
    path: str | None
    content: str | None
    reason: str
    truncated: bool


class LocalFilesystemReadAdapter:
    """Local repo-only readonly adapter for future filesystem_read replacement.

    This adapter is intentionally narrow:
    - only repo-relative paths
    - policy gate before any file access
    - text files only
    - no MCP / no shell / no network
    """

    DEFAULT_MAX_BYTES = 128 * 1024

    def __init__(
        self,
        repo_root: Path,
        policy: FilesystemReadPolicy | None = None,
        max_bytes: int = DEFAULT_MAX_BYTES,
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.policy = policy or FilesystemReadPolicy()
        self.max_bytes = max_bytes

    def read_text(self, repo_relative_path: str) -> FilesystemReadResult:
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

        raw_bytes, truncated = self._read_limited_bytes(target_path)

        if self._looks_binary(raw_bytes):
            return FilesystemReadResult(
                allowed=False,
                path=normalized_path,
                content=None,
                reason="Binary files are not allowed for filesystem_read.",
                truncated=False,
            )

        content = self._decode_text(raw_bytes)
        if content is None:
            return FilesystemReadResult(
                allowed=False,
                path=normalized_path,
                content=None,
                reason="Only UTF-8 text files are allowed for filesystem_read.",
                truncated=False,
            )

        reason = "Read allowed."
        if truncated:
            reason = f"Read allowed, content truncated to {self.max_bytes} bytes."

        return FilesystemReadResult(
            allowed=True,
            path=normalized_path,
            content=content,
            reason=reason,
            truncated=truncated,
        )

    def _is_within_repo_root(self, path: Path) -> bool:
        try:
            path.relative_to(self.repo_root)
            return True
        except ValueError:
            return False

    def _looks_binary(self, raw_bytes: bytes) -> bool:
        return b"\x00" in raw_bytes

    def _read_limited_bytes(self, path: Path) -> tuple[bytes, bool]:
        with path.open("rb") as file:
            raw_bytes = file.read(self.max_bytes + 1)
        if len(raw_bytes) > self.max_bytes:
            return raw_bytes[: self.max_bytes], True
        return raw_bytes, False

    def _decode_text(self, raw_bytes: bytes) -> str | None:
        try:
            return raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return None
