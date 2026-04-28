from __future__ import annotations

from ai_test_assistant.filesystem.policy import FilesystemReadPolicy


def test_filesystem_policy_allows_readme() -> None:
    decision = FilesystemReadPolicy().evaluate("README.md")

    assert decision.allowed is True
    assert decision.normalized_path == "README.md"


def test_filesystem_policy_allows_docs_file() -> None:
    decision = FilesystemReadPolicy().evaluate("docs/mcp-selection.md")

    assert decision.allowed is True
    assert decision.normalized_path == "docs/mcp-selection.md"


def test_filesystem_policy_allows_agent_asset_file() -> None:
    decision = FilesystemReadPolicy().evaluate("agent-assets/prompts/test-case-generation.md")

    assert decision.allowed is True
    assert decision.normalized_path == "agent-assets/prompts/test-case-generation.md"


def test_filesystem_policy_allows_src_readme() -> None:
    decision = FilesystemReadPolicy().evaluate("src/ai_test_assistant/orchestrator/README.md")

    assert decision.allowed is True
    assert decision.normalized_path == "src/ai_test_assistant/orchestrator/README.md"


def test_filesystem_policy_blocks_dotenv() -> None:
    decision = FilesystemReadPolicy().evaluate(".env")

    assert decision.allowed is False
    assert decision.normalized_path == ".env"


def test_filesystem_policy_blocks_assistant_state() -> None:
    decision = FilesystemReadPolicy().evaluate(".assistant/memory.sqlite3")

    assert decision.allowed is False
    assert decision.normalized_path == ".assistant/memory.sqlite3"


def test_filesystem_policy_blocks_git_config() -> None:
    decision = FilesystemReadPolicy().evaluate(".git/config")

    assert decision.allowed is False
    assert decision.normalized_path == ".git/config"


def test_filesystem_policy_blocks_parent_traversal() -> None:
    decision = FilesystemReadPolicy().evaluate("../.env")

    assert decision.allowed is False
    assert decision.normalized_path is None


def test_filesystem_policy_blocks_nested_parent_traversal() -> None:
    decision = FilesystemReadPolicy().evaluate("docs/../../.env")

    assert decision.allowed is False
    assert decision.normalized_path is None


def test_filesystem_policy_blocks_secret_token_patterns() -> None:
    decision = FilesystemReadPolicy().evaluate("docs/secret-token.txt")

    assert decision.allowed is False
    assert decision.normalized_path == "docs/secret-token.txt"
