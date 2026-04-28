from pathlib import Path


def test_local_environment_prerequisites_doc_exists() -> None:
    assert Path("docs/local-environment-prerequisites.md").exists()


def test_local_environment_prerequisites_doc_contains_required_markers() -> None:
    content = Path("docs/local-environment-prerequisites.md").read_text(encoding="utf-8")

    for marker in (
        "pyproject.toml",
        "requirements.txt",
        "requirements-dev.txt",
        "## 必装工具",
        "## 可选工具",
        "## 版本检查命令",
        "## Windows 安装建议",
        "## 失败时怎么处理",
        "## Codex 可自动修复的范围",
        "## 需要用户手动处理的范围",
        "Git",
        "Python",
        "pytest",
        "Node.js",
        "npm",
        "npx",
        "nvm-windows",
        "可选，不是必装",
        ".venv",
        "python -m venv .venv",
        ".\\.venv\\Scripts\\activate",
        "python -m pip install -U pip",
        'python -m pip install -e ".[test]"',
        "python -c \"import mcp; print('mcp ok')\"",
        "python -c \"import langgraph; print('langgraph ok')\"",
        "@modelcontextprotocol/server-filesystem",
        "<ABSOLUTE_PATH_TO_AI_TEST_LAB>",
    ):
        assert marker in content


def test_local_environment_prerequisites_doc_contains_expected_workspace_bootstrap_command() -> None:
    content = Path("docs/local-environment-prerequisites.md").read_text(encoding="utf-8")

    assert "cd D:\\TestHome\\ai-test-lab" in content
