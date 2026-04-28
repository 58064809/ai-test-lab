from __future__ import annotations

from pathlib import Path

import yaml


def _load_tools() -> list[dict[str, object]]:
    config = yaml.safe_load(Path("configs/tools.yaml").read_text(encoding="utf-8")) or {}
    return list(config.get("tools", []))


def test_filesystem_mcp_docs_exist_and_cover_required_sections() -> None:
    selection_path = Path("docs/filesystem-mcp-selection.md")
    plan_path = Path("docs/filesystem-mcp-minimal-integration-plan.md")

    assert selection_path.exists()
    assert plan_path.exists()

    selection = selection_path.read_text(encoding="utf-8")
    plan = plan_path.read_text(encoding="utf-8")

    for section in [
        "候选方案",
        "信息来源",
        "选择结果",
        "选择理由",
        "未选择方案及原因",
        "Windows 本地运行支持",
        "只读模式支持",
        "仓库根目录限制能力",
        "写能力禁用方式",
        "与 FilesystemReadPolicy 的协同方式",
        "最小接入验证步骤",
        "风险与限制",
        "待人工确认项",
        "后续替换策略",
    ]:
        assert section in selection

    for section in [
        "目标",
        "非目标",
        "前置条件",
        "验证环境",
        "验证命令",
        "安全边界",
        "成功标准",
        "失败回滚",
        "需要人工确认的问题",
    ]:
        assert section in plan


def test_filesystem_mcp_docs_mark_local_adapter_as_fallback_and_not_integrated() -> None:
    selection = Path("docs/filesystem-mcp-selection.md").read_text(encoding="utf-8")
    plan = Path("docs/filesystem-mcp-minimal-integration-plan.md").read_text(encoding="utf-8")

    assert "bootstrap / fallback" in selection
    assert "待人工确认" in selection
    assert "不运行 MCP Server" in plan
    assert "不调用 MCP SDK" in plan
    assert "已接入 filesystem MCP" not in selection
    assert "已接入 filesystem MCP" not in plan


def test_filesystem_mcp_tools_keep_read_only_boundary_and_write_stays_disabled() -> None:
    tools = _load_tools()
    by_name = {str(tool["name"]): tool for tool in tools}

    assert by_name["filesystem_read"]["status"] == "enabled"
    assert by_name["filesystem_read"]["implementation"] == "local_python"
    assert by_name["filesystem_mcp_read"]["status"] == "enabled"
    assert by_name["filesystem_mcp_read"]["implementation"] == "official_mcp"
    assert by_name["filesystem_mcp_read"]["risk_level"] == "read_only"
    assert by_name["filesystem_write"]["status"] == "disabled"
    assert by_name["shell"]["status"] == "disabled"
