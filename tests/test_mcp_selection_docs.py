from __future__ import annotations

from pathlib import Path

import yaml


def _load_tools() -> list[dict[str, object]]:
    config = yaml.safe_load(Path("configs/tools.yaml").read_text(encoding="utf-8")) or {}
    return list(config.get("tools", []))


def test_mcp_selection_docs_exist_and_cover_required_sections() -> None:
    selection = Path("docs/mcp-selection.md")
    policy = Path("docs/mcp-security-policy.md")

    assert selection.exists()
    assert policy.exists()

    selection_text = selection.read_text(encoding="utf-8")
    policy_text = policy.read_text(encoding="utf-8")

    for section in [
        "候选 MCP Server / 工具",
        "选择结果",
        "选择理由",
        "未选择方案及原因",
        "当前接入状态",
        "风险与限制",
        "权限分层",
        "推荐接入顺序",
        "Windows 本地运行注意事项",
        "后续替换策略",
    ]:
        assert section in selection_text

    for level in ["L0: no_tool", "L1: read_only", "L2: read_project_files", "L3: write_project_files", "L4: external_network", "L5: execute_local_command", "L6: restricted_business_action"]:
        assert level in policy_text


def test_mcp_related_tools_remain_non_enabled_under_safe_defaults() -> None:
    tools = _load_tools()
    by_name = {str(tool["name"]): tool for tool in tools}

    assert by_name["pytest_runner"]["status"] == "enabled"
    assert by_name["pytest_runner"]["risk_level"] == "execute_local_command"
    assert by_name["shell"]["status"] != "enabled"
    assert by_name["playwright_mcp"]["status"] != "enabled"
    assert by_name["playwright_browser"]["status"] != "enabled"
    assert by_name["filesystem_write"]["status"] != "enabled"
    assert by_name["github_write"]["status"] != "enabled"

    for tool in tools:
        risk_level = str(tool["risk_level"])
        status = str(tool["status"])
        if risk_level in {"external_network", "execute_local_command", "restricted_action"}:
            if str(tool["name"]) in {"pytest_runner", "github_read"}:
                assert status == "enabled"
                continue
            assert status != "enabled"


def test_database_and_redis_tools_stay_readonly_and_non_write_capable() -> None:
    tools = _load_tools()
    by_name = {str(tool["name"]): tool for tool in tools}

    assert by_name["database_readonly"]["risk_level"] == "read_only"
    assert by_name["redis_readonly"]["risk_level"] == "read_only"
    assert by_name["database_readonly"]["status"] != "enabled"
    assert by_name["redis_readonly"]["status"] != "enabled"


def test_security_policy_mentions_key_non_default_enable_rules() -> None:
    text = Path("docs/mcp-security-policy.md").read_text(encoding="utf-8")

    assert "shell 永远不能默认 `enabled`" in text
    assert "filesystem write 不能默认 `enabled`" in text
    assert "GitHub write 不能默认 `enabled`" in text
    assert "database / redis 第一阶段只允许 readonly" in text
    assert "Playwright MCP 第一阶段不允许执行真实支付、下单、发券、删数据等动作" in text
