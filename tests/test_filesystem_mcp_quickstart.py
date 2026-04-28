from __future__ import annotations

import json
from pathlib import Path

import yaml


def _load_tools() -> dict[str, dict[str, object]]:
    config = yaml.safe_load(Path("configs/tools.yaml").read_text(encoding="utf-8")) or {}
    return {str(item["name"]): item for item in config.get("tools", [])}


def test_filesystem_mcp_quickstart_docs_and_example_exist() -> None:
    assert Path("docs/filesystem-mcp-quickstart.md").exists()
    assert Path("configs/mcp/filesystem-server.example.json").exists()


def test_filesystem_mcp_quickstart_doc_contains_required_markers() -> None:
    content = Path("docs/filesystem-mcp-quickstart.md").read_text(encoding="utf-8")

    for marker in (
        "@modelcontextprotocol/server-filesystem",
        "Windows 前置条件",
        "Git",
        "Python",
        "pytest",
        "Node.js",
        "npm",
        "npx",
        "nvm-windows",
        "本地验证命令",
        "安全边界",
        "不开放 `filesystem_write`",
        "不开放 `shell`",
        "--mcp-read-file",
        "[local-environment-prerequisites.md](local-environment-prerequisites.md)",
        "[filesystem-server.example.json](../configs/mcp/filesystem-server.example.json)",
    ):
        assert marker in content


def test_filesystem_mcp_example_uses_placeholder_and_official_package() -> None:
    config = json.loads(
        Path("configs/mcp/filesystem-server.example.json").read_text(encoding="utf-8")
    )

    server = config["mcpServers"]["filesystem"]
    assert server["command"] == "npx"
    assert server["args"][0] == "-y"
    assert "@modelcontextprotocol/server-filesystem" in server["args"]
    assert "<ABSOLUTE_PATH_TO_AI_TEST_LAB>" in server["args"]


def test_filesystem_mcp_example_does_not_include_real_paths_or_secrets() -> None:
    content = Path("configs/mcp/filesystem-server.example.json").read_text(encoding="utf-8")

    assert "D:\\" not in content
    lowered = content.lower()
    for marker in ("token", "secret", "password", ".env"):
        assert marker not in lowered


def test_filesystem_mcp_tool_boundaries_remain_locked() -> None:
    tools = _load_tools()

    assert tools["filesystem_mcp_read"]["status"] == "enabled"
    assert tools["filesystem_mcp_read"]["risk_level"] == "read_only"
    assert tools["filesystem_write"]["status"] == "disabled"
    assert tools["shell"]["status"] == "disabled"


def test_filesystem_mcp_quickstart_doc_does_not_contain_local_absolute_paths() -> None:
    content = Path("docs/filesystem-mcp-quickstart.md").read_text(encoding="utf-8")

    assert "D:/" not in content
    assert "D:\\" not in content
