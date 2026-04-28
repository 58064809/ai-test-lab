from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
import re


@dataclass(slots=True)
class FilesystemReadDecision:
    allowed: bool
    reason: str
    normalized_path: str | None


class FilesystemReadPolicy:
    """Path-only safety policy for future filesystem_read integration.

    This class intentionally does not read file contents and does not touch MCP.
    It only decides whether a repo-relative path would be allowed in the future.
    """

    ALLOWED_ROOTS = (
        "docs/",
        "agent-assets/",
        "src/ai_test_assistant/",
        "tests/",
        "validation/",
    )
    ALLOWED_EXACT = {"README.md", "AGENTS.md"}
    ALLOWED_CONFIG_PREFIX = "configs/"
    ALLOWED_CONFIG_SUFFIX = ".yaml"

    BLOCKED_PREFIXES = (".assistant/", ".git/")
    BLOCKED_EXACT = {".env"}
    BLOCKED_EXTENSIONS = (".pem", ".key", ".crt")
    BLOCKED_SUBSTRINGS = (
        "token",
        "secret",
        "password",
        "jdbc",
        "connection-string",
        "datasource",
    )
    DRIVE_PATTERN = re.compile(r"^[a-zA-Z]:")

    def evaluate(self, repo_relative_path: str) -> FilesystemReadDecision:
        raw_value = repo_relative_path.strip()
        if not raw_value:
            return FilesystemReadDecision(
                allowed=False,
                reason="Path must not be empty.",
                normalized_path=None,
            )

        normalized_input = raw_value.replace("\\", "/")
        if self.DRIVE_PATTERN.match(normalized_input) or normalized_input.startswith("/"):
            return FilesystemReadDecision(
                allowed=False,
                reason="Absolute paths are not allowed.",
                normalized_path=None,
            )

        path = PurePosixPath(normalized_input)
        parts = path.parts
        if any(part == ".." for part in parts):
            return FilesystemReadDecision(
                allowed=False,
                reason="Path traversal is not allowed.",
                normalized_path=None,
            )

        normalized_path = path.as_posix()
        if normalized_path.startswith("./"):
            normalized_path = normalized_path[2:]
        if not normalized_path:
            return FilesystemReadDecision(
                allowed=False,
                reason="Path must not be empty.",
                normalized_path=None,
            )

        lowered = normalized_path.lower()
        if lowered in self.BLOCKED_EXACT:
            return FilesystemReadDecision(False, "Sensitive file is blocked.", normalized_path)
        if any(lowered.startswith(prefix) for prefix in self.BLOCKED_PREFIXES):
            return FilesystemReadDecision(False, "Sensitive directory is blocked.", normalized_path)
        if any(lowered.endswith(ext) for ext in self.BLOCKED_EXTENSIONS):
            return FilesystemReadDecision(False, "Sensitive certificate or key file is blocked.", normalized_path)
        if any(token in lowered for token in self.BLOCKED_SUBSTRINGS):
            return FilesystemReadDecision(False, "Sensitive filename pattern is blocked.", normalized_path)

        if normalized_path in self.ALLOWED_EXACT:
            return FilesystemReadDecision(True, "Path is explicitly allowed.", normalized_path)
        if lowered.startswith(self.ALLOWED_CONFIG_PREFIX) and lowered.endswith(self.ALLOWED_CONFIG_SUFFIX):
            return FilesystemReadDecision(True, "Config YAML path is allowed.", normalized_path)
        if any(lowered.startswith(prefix) for prefix in self.ALLOWED_ROOTS):
            return FilesystemReadDecision(True, "Path is within an allowed repository area.", normalized_path)

        return FilesystemReadDecision(
            allowed=False,
            reason="Path is outside the current filesystem_read allowlist.",
            normalized_path=normalized_path,
        )
