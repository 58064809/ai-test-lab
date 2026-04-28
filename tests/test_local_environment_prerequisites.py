from pathlib import Path


def test_local_environment_prerequisites_doc_exists() -> None:
    assert Path("docs/local-environment-prerequisites.md").exists()


def test_local_environment_prerequisites_doc_contains_required_markers() -> None:
    content = Path("docs/local-environment-prerequisites.md").read_text(encoding="utf-8")

    for marker in (
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
        "@modelcontextprotocol/server-filesystem",
        "<ABSOLUTE_PATH_TO_AI_TEST_LAB>",
    ):
        assert marker in content


def test_local_environment_prerequisites_doc_does_not_hardcode_local_path() -> None:
    content = Path("docs/local-environment-prerequisites.md").read_text(encoding="utf-8")

    assert "D:\\TestHome\\ai-test-lab" not in content
