from __future__ import annotations

from pathlib import Path


def test_project_does_not_maintain_requirements_txt_files() -> None:
    assert not Path("requirements.txt").exists()
    assert not Path("requirements-dev.txt").exists()


def test_pyproject_is_the_only_primary_dependency_source() -> None:
    content = Path("pyproject.toml").read_text(encoding="utf-8")

    for marker in (
        "langgraph>=",
        "mcp>=",
        "pydantic>=",
        "PyYAML>=",
        "pytest>=",
    ):
        assert marker in content


def test_local_environment_doc_recommends_project_venv_and_editable_install() -> None:
    content = Path("docs/local-environment-prerequisites.md").read_text(encoding="utf-8")

    for marker in (
        "pyproject.toml",
        "requirements.txt",
        "requirements-dev.txt",
        ".venv",
        "python -m venv .venv",
        ".\\.venv\\Scripts\\activate",
        'python -m pip install -e ".[test]"',
        "python -c \"import mcp; print('mcp ok')\"",
        "python -c \"import langgraph; print('langgraph ok')\"",
    ):
        assert marker in content
