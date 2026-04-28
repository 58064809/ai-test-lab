from pathlib import Path

import yaml


def test_official_mainstream_confirmation_doc_exists() -> None:
    assert Path("docs/filesystem-mcp-official-mainstream-confirmation.md").exists()


def test_official_mainstream_confirmation_doc_has_required_sections() -> None:
    content = Path("docs/filesystem-mcp-official-mainstream-confirmation.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "## 确认目标",
        "## 优先级原则",
        "## 官方候选",
        "## 主流生态候选",
        "## 社区候选降级条件",
        "## 已排除项",
        "## 事实确认表",
        "## 推荐结论",
        "## 未确认风险",
        "## 下一步是否允许进入最小接入验证",
        "@modelcontextprotocol/server-filesystem",
        "不继续扩展 `LocalFilesystemReadAdapter`",
    ):
        assert marker in content


def test_official_mainstream_confirmation_doc_does_not_claim_integration() -> None:
    content = Path("docs/filesystem-mcp-official-mainstream-confirmation.md").read_text(
        encoding="utf-8"
    )

    assert "已接入 filesystem MCP" not in content
    assert "filesystem_mcp_read 已启用" not in content


def test_filesystem_mcp_tools_remain_locked() -> None:
    config = yaml.safe_load(Path("configs/tools.yaml").read_text(encoding="utf-8"))
    tools = {item["name"]: item for item in config["tools"]}

    assert tools["filesystem_mcp_read"]["status"] != "enabled"
    assert tools["filesystem_write"]["status"] == "disabled"
    assert tools["shell"]["status"] == "disabled"
