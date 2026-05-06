from __future__ import annotations

import json
from pathlib import Path

from ai_test_assistant.memory.sqlite_store import SQLiteMemoryStore
from ai_test_assistant.reporting import AllureReportReader
from ai_test_assistant.runtime.cli import build_parser, run_cli
from ai_test_assistant.tool_registry.models import ToolRiskLevel, ToolStatus
from ai_test_assistant.tool_registry.registry import ToolRegistry


def _write_assistant_config(tmp_path: Path, tools_path: Path | None = None) -> Path:
    memory_db_path = (tmp_path / "memory.sqlite3").resolve()
    intents_path = Path("configs/intents.yaml").resolve()
    tools_path = tools_path or Path("configs/tools.yaml").resolve()
    assistant_config = tmp_path / "assistant.yaml"
    assistant_config.write_text(
        "\n".join(
            [
                "memory:",
                "  backend: sqlite",
                f"  sqlite_path: {memory_db_path.as_posix()}",
                "intent:",
                f"  rules_path: {intents_path.as_posix()}",
                "tool_registry:",
                f"  config_path: {tools_path.as_posix()}",
            ]
        ),
        encoding="utf-8",
    )
    return assistant_config


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _write_minimal_allure_report(repo_root: Path, report_dir: str = "allure-report") -> None:
    widgets_dir = repo_root / report_dir / "widgets"
    _write_json(
        widgets_dir / "summary.json",
        {
            "statistic": {
                "total": 5,
                "passed": 2,
                "failed": 1,
                "broken": 1,
                "skipped": 1,
                "unknown": 0,
            },
            "time": {"duration": 1234},
        },
    )
    _write_json(
        widgets_dir / "categories.json",
        [
            {
                "name": "Product defects",
                "children": [
                    {"name": "test_checkout_failed", "status": "failed"},
                    {"name": "test_payment_broken", "status": "broken"},
                ],
            }
        ],
    )


def test_allure_reader_reads_default_allure_report(tmp_path: Path) -> None:
    _write_minimal_allure_report(tmp_path)

    summary = AllureReportReader(tmp_path).read_summary()

    assert summary.allowed is True
    assert summary.report_dir == "allure-report"
    assert summary.total == 5
    assert summary.passed == 2
    assert summary.failed == 1
    assert summary.broken == 1
    assert summary.skipped == 1
    assert summary.unknown == 0
    assert summary.duration_ms == 1234
    assert summary.top_failures == ["test_checkout_failed", "test_payment_broken"]


def test_allure_reader_rejects_absolute_path(tmp_path: Path) -> None:
    summary = AllureReportReader(tmp_path).read_summary(str(tmp_path / "allure-report"))

    assert summary.allowed is False
    assert "absolute" in summary.reason


def test_allure_reader_rejects_path_traversal(tmp_path: Path) -> None:
    summary = AllureReportReader(tmp_path).read_summary("../allure-report")

    assert summary.allowed is False
    assert "traversal" in summary.reason


def test_allure_reader_rejects_glob_path(tmp_path: Path) -> None:
    summary = AllureReportReader(tmp_path).read_summary("allure-*")

    assert summary.allowed is False
    assert "glob" in summary.reason


def test_allure_reader_rejects_sensitive_path(tmp_path: Path) -> None:
    summary = AllureReportReader(tmp_path).read_summary("secret-report")

    assert summary.allowed is False
    assert "Sensitive" in summary.reason


def test_allure_reader_reports_missing_summary_json(tmp_path: Path) -> None:
    (tmp_path / "allure-report" / "widgets").mkdir(parents=True)

    summary = AllureReportReader(tmp_path).read_summary()

    assert summary.allowed is False
    assert "widgets/summary.json" in summary.reason


def test_allure_reader_can_extract_duration_from_duration_widget(tmp_path: Path) -> None:
    widgets_dir = tmp_path / "allure-report" / "widgets"
    _write_json(
        widgets_dir / "summary.json",
        {"statistic": {"total": 1, "passed": 1, "failed": 0, "broken": 0, "skipped": 0, "unknown": 0}},
    )
    _write_json(widgets_dir / "duration.json", [{"name": "duration", "duration": 456}])

    summary = AllureReportReader(tmp_path).read_summary()

    assert summary.duration_ms == 456


def test_allure_reader_returns_none_duration_when_duration_is_absent(tmp_path: Path) -> None:
    widgets_dir = tmp_path / "allure-report" / "widgets"
    _write_json(
        widgets_dir / "summary.json",
        {"statistic": {"total": 1, "passed": 1, "failed": 0, "broken": 0, "skipped": 0, "unknown": 0}},
    )

    summary = AllureReportReader(tmp_path).read_summary()

    assert summary.allowed is True
    assert summary.duration_ms is None


def test_allure_reader_reports_invalid_json_without_raw_payload(tmp_path: Path) -> None:
    widgets_dir = tmp_path / "allure-report" / "widgets"
    widgets_dir.mkdir(parents=True)
    (widgets_dir / "summary.json").write_text('{"statistic":', encoding="utf-8")

    summary = AllureReportReader(tmp_path).read_summary()

    assert summary.allowed is False
    assert summary.reason == "Invalid JSON in Allure widget file: summary.json."
    assert summary.total is None
    assert summary.top_failures == []


def test_allure_reader_extracts_top_failures_from_suites_and_limits_to_ten(tmp_path: Path) -> None:
    widgets_dir = tmp_path / "allure-report" / "widgets"
    _write_json(
        widgets_dir / "summary.json",
        {"statistic": {"total": 12, "passed": 0, "failed": 12, "broken": 0, "skipped": 0, "unknown": 0}},
    )
    _write_json(
        widgets_dir / "suites.json",
        {"items": [{"name": "suite", "children": [{"name": f"test_{index}", "status": "failed"} for index in range(12)]}]},
    )

    summary = AllureReportReader(tmp_path).read_summary()

    assert summary.top_failures == [f"test_{index}" for index in range(10)]


def test_cli_parser_supports_read_allure_report_default_and_custom() -> None:
    parser = build_parser()

    default_args = parser.parse_args(["分析 Allure 报告", "--read-allure-report"])
    custom_args = parser.parse_args(["分析 Allure 报告", "--read-allure-report", "custom-report"])

    assert default_args.read_allure_report == "allure-report"
    assert custom_args.read_allure_report == "custom-report"


def test_cli_outputs_allure_summary_and_explicit_execution(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    _write_minimal_allure_report(repo_dir, "custom-report")
    monkeypatch.chdir(repo_dir.resolve())

    exit_code = run_cli(["分析 Allure 报告", "--read-allure-report", "custom-report", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "Allure 报告摘要" in captured
    assert "report_dir=custom-report" in captured
    assert "total=5" in captured
    assert "passed=2" in captured
    assert "failed=1" in captured
    assert "duration_ms=1234" in captured
    assert "test_checkout_failed" in captured
    assert "allure_report" in captured
    assert "read_summary" in captured
    assert "Tool 'allure_report'" not in captured


def test_cli_write_memory_keeps_only_allure_summary_metadata(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    _write_minimal_allure_report(repo_dir)
    monkeypatch.chdir(repo_dir.resolve())

    exit_code = run_cli(["分析 Allure 报告", "--read-allure-report", "--write-memory", "--config", str(config_path)])

    assert exit_code == 0
    capsys.readouterr()
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")
    results = store.search_memory("task_result/orchestrator")
    assert len(results) == 1
    allure_reports = results[0].value["allure_reports"]
    assert allure_reports == [
        {
            "report_dir": "allure-report",
            "total": 5,
            "passed": 2,
            "failed": 1,
            "broken": 1,
            "skipped": 1,
            "unknown": 0,
            "duration_ms": 1234,
            "top_failures_count": 2,
            "allowed": True,
            "reason": "Read Allure report summary from existing report widgets.",
        }
    ]
    assert "top_failures" not in allure_reports[0]
    assert "statistic" not in str(results[0].value)
    assert "children" not in str(results[0].value)


def test_allure_report_tool_is_enabled_read_only_and_write_boundaries_stay_disabled() -> None:
    registry = ToolRegistry.from_yaml("configs/tools.yaml")

    allure_report_tool = registry.get_tool("allure_report")
    allure_generate_tool = registry.get_tool("allure_generate")
    shell_tool = registry.get_tool("shell")
    filesystem_write_tool = registry.get_tool("filesystem_write")
    github_write_tool = registry.get_tool("github_write")

    assert allure_report_tool.status is ToolStatus.ENABLED
    assert allure_report_tool.risk_level is ToolRiskLevel.READ_ONLY
    assert allure_generate_tool.status is ToolStatus.ENABLED
    assert allure_generate_tool.risk_level is ToolRiskLevel.EXECUTE_LOCAL_COMMAND
    assert shell_tool.status is ToolStatus.DISABLED
    assert filesystem_write_tool.status is ToolStatus.DISABLED
    assert github_write_tool.status is ToolStatus.DISABLED
