from pathlib import Path

import yaml


def test_manual_checklist_doc_exists() -> None:
    assert Path("docs/filesystem-mcp-manual-checklist.md").exists()


def test_manual_checklist_contains_required_sections() -> None:
    content = Path("docs/filesystem-mcp-manual-checklist.md").read_text(encoding="utf-8")

    for marker in (
        "## 确认目标",
        "## 候选方案列表",
        "## 候选方案对比表",
        "## 必须确认的问题",
        "## 禁止接入条件",
        "## 推荐结论模板",
        "## 证据记录模板",
        "## 下一步决策",
        "候选名称",
        "仓库地址",
        "GitHub star",
        "Windows 支持",
        "是否支持只读模式",
        "是否支持限制根目录",
        "是否可以禁用写能力",
        "是否支持敏感路径过滤",
        "是否适合个人本地 AI 测试助手",
    ):
        assert marker in content


def test_manual_checklist_lists_explicit_candidate_types() -> None:
    content = Path("docs/filesystem-mcp-manual-checklist.md").read_text(encoding="utf-8")

    for marker in (
        "官方或主流生态中的 filesystem MCP server",
        "社区维护、文档完整、Windows 兼容的 filesystem MCP server",
        "编辑器 / Agent 生态中的成熟只读 filesystem 工具",
    ):
        assert marker in content

    assert "候选 A" not in content
    assert "候选 B" not in content
    assert "候选 C" not in content


def test_manual_checklist_contains_required_checkboxes() -> None:
    content = Path("docs/filesystem-mcp-manual-checklist.md").read_text(encoding="utf-8")

    for marker in (
        "- [ ] 该工具是否为官方或主流社区维护？",
        "- [ ] 是否支持 Windows 本地运行？",
        "- [ ] 是否支持显式只读模式？",
        "- [ ] 是否能限制访问到指定仓库根目录？",
        "- [ ] 是否能禁用写文件能力？",
        "- [ ] 是否能与当前 `FilesystemReadPolicy` 协同，而不是绕过安全边界？",
        "- [ ] 是否可以只开放 `filesystem_read`，不开放 `filesystem_write`？",
    ):
        assert marker in content


def test_manual_checklist_avoids_unverified_completion_claims() -> None:
    content = Path("docs/filesystem-mcp-manual-checklist.md").read_text(encoding="utf-8")

    assert "已确认官方 filesystem MCP 可用" not in content
    assert "已接入 MCP" not in content


def test_mcp_tool_boundaries_remain_locked() -> None:
    config = yaml.safe_load(Path("configs/tools.yaml").read_text(encoding="utf-8"))
    tools = {item["name"]: item for item in config["tools"]}

    assert tools["filesystem_mcp_read"]["status"] == "enabled"
    assert tools["filesystem_mcp_read"]["risk_level"] == "read_only"
    assert tools["filesystem_write"]["status"] == "disabled"
    assert tools["shell"]["status"] == "disabled"
