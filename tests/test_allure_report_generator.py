from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from ai_test_assistant.reporting import AllureReportGenerator
from ai_test_assistant.runtime.cli import build_parser, run_cli
from ai_test_assistant.tool_registry.models import ToolRiskLevel, ToolStatus
from ai_test_assistant.tool_registry.registry import ToolRegistry


def _write_assistant_config(tmp_path: Path) -> Path:
    memory_db_path = (tmp_path / "memory.sqlite3").resolve()
    intents_path = Path("configs/intents.yaml").resolve()
    tools_path = Path("configs/tools.yaml").resolve()
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


def test_allure_generator_uses_default_dirs_args_list_and_shell_false(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "allure-results").mkdir()
    calls: list[dict[str, object]] = []

    def fake_run(command, **kwargs):
        calls.append({"command": command, **kwargs})
        return SimpleNamespace(returncode=0, stdout="generated", stderr="")

    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.subprocess.run", fake_run)
    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.shutil.which", lambda name: "allure" if name == "allure" else None)

    result = AllureReportGenerator(tmp_path).generate()

    assert result.generated is True
    assert result.command == ["allure", "generate", "allure-results", "-o", "allure-report", "--clean"]
    assert result.results_dir == "allure-results"
    assert result.report_dir == "allure-report"
    assert calls == [
        {
            "command": ["allure", "generate", "allure-results", "-o", "allure-report", "--clean"],
            "cwd": tmp_path.resolve(),
            "capture_output": True,
            "text": True,
            "shell": False,
            "check": False,
        }
    ]


def test_allure_generator_supports_custom_dirs(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "custom-results").mkdir()

    def fake_run(command, **kwargs):
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.subprocess.run", fake_run)
    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.shutil.which", lambda name: "allure" if name == "allure" else None)

    result = AllureReportGenerator(tmp_path).generate("custom-results", "custom-report")

    assert result.command == ["allure", "generate", "custom-results", "-o", "custom-report", "--clean"]
    assert result.generated is True


def test_allure_generator_rejects_absolute_results_dir_without_subprocess(tmp_path: Path, monkeypatch) -> None:
    calls: list[object] = []
    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.subprocess.run", lambda *args, **kwargs: calls.append(args))

    result = AllureReportGenerator(tmp_path).generate(str(tmp_path / "allure-results"))

    assert result.generated is False
    assert "absolute" in result.reason
    assert calls == []


def test_allure_generator_rejects_absolute_report_dir_without_subprocess(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "allure-results").mkdir()
    calls: list[object] = []
    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.subprocess.run", lambda *args, **kwargs: calls.append(args))

    result = AllureReportGenerator(tmp_path).generate("allure-results", str(tmp_path / "allure-report"))

    assert result.generated is False
    assert "absolute" in result.reason
    assert calls == []


def test_allure_generator_rejects_path_traversal_glob_and_sensitive_paths(tmp_path: Path, monkeypatch) -> None:
    calls: list[object] = []
    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.subprocess.run", lambda *args, **kwargs: calls.append(args))
    generator = AllureReportGenerator(tmp_path)

    traversal = generator.generate("../allure-results")
    glob = generator.generate("allure-*")
    sensitive = generator.generate("secret-results")

    assert traversal.generated is False
    assert "traversal" in traversal.reason
    assert glob.generated is False
    assert "glob" in glob.reason
    assert sensitive.generated is False
    assert "Sensitive" in sensitive.reason
    assert calls == []


def test_allure_generator_missing_results_dir_fails_without_subprocess(tmp_path: Path, monkeypatch) -> None:
    calls: list[object] = []
    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.subprocess.run", lambda *args, **kwargs: calls.append(args))

    result = AllureReportGenerator(tmp_path).generate()

    assert result.generated is False
    assert result.exit_code is None
    assert "results directory does not exist" in result.reason
    assert calls == []


def test_allure_generator_reports_missing_cli(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "allure-results").mkdir()
    calls: list[object] = []

    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.subprocess.run", lambda *args, **kwargs: calls.append(args))
    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.shutil.which", lambda name: None)
    monkeypatch.delenv("USERPROFILE", raising=False)

    result = AllureReportGenerator(tmp_path).generate()

    assert result.generated is False
    assert result.exit_code is None
    assert result.reason == "Allure CLI executable not found."
    assert calls == []


def test_allure_generator_uses_shutil_which_allure_hit(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "allure-results").mkdir()
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.subprocess.run", fake_run)
    monkeypatch.setattr(
        "ai_test_assistant.reporting.allure_generator.shutil.which",
        lambda name: r"C:\tools\allure.cmd" if name == "allure" else None,
    )

    result = AllureReportGenerator(tmp_path).generate()

    assert result.command[0] == r"C:\tools\allure.cmd"
    assert calls[0][0] == r"C:\tools\allure.cmd"


def test_allure_generator_uses_allure_cmd_when_allure_not_found(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "allure-results").mkdir()
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    def fake_which(name: str) -> str | None:
        if name == "allure.cmd":
            return r"C:\Users\tester\scoop\shims\allure.cmd"
        return None

    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.subprocess.run", fake_run)
    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.shutil.which", fake_which)
    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.os.name", "nt")

    result = AllureReportGenerator(tmp_path).generate()

    assert result.command[0] == r"C:\Users\tester\scoop\shims\allure.cmd"
    assert calls[0][0] == r"C:\Users\tester\scoop\shims\allure.cmd"


def test_allure_generator_uses_scoop_fallback_path(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "allure-results").mkdir()
    user_profile = tmp_path / "user"
    scoop_shim = user_profile / "scoop" / "shims" / "allure.cmd"
    scoop_shim.parent.mkdir(parents=True)
    scoop_shim.write_text("@echo off", encoding="utf-8")
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.subprocess.run", fake_run)
    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.shutil.which", lambda name: None)
    monkeypatch.setattr("ai_test_assistant.reporting.allure_generator.os.name", "nt")
    monkeypatch.setenv("USERPROFILE", str(user_profile))

    result = AllureReportGenerator(tmp_path).generate()

    assert result.command[0] == str(scoop_shim)
    assert calls[0][0] == str(scoop_shim)


def test_cli_parser_supports_generate_allure_defaults_and_custom_dirs() -> None:
    parser = build_parser()

    default_args = parser.parse_args(["生成 Allure 报告", "--generate-allure-report"])
    custom_args = parser.parse_args(
        [
            "生成 Allure 报告",
            "--generate-allure-report",
            "custom-results",
            "--allure-output-dir",
            "custom-report",
        ]
    )

    assert default_args.generate_allure_report == "allure-results"
    assert default_args.allure_output_dir == "allure-report"
    assert custom_args.generate_allure_report == "custom-results"
    assert custom_args.allure_output_dir == "custom-report"


def test_cli_outputs_allure_generate_result_and_explicit_execution(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    monkeypatch.chdir(repo_dir.resolve())

    class StubGenerator:
        def __init__(self, repo_root: Path) -> None:
            self.repo_root = repo_root

        def generate(self, results_dir: str = "allure-results", report_dir: str = "allure-report") -> SimpleNamespace:
            assert results_dir == "custom-results"
            assert report_dir == "custom-report"
            return SimpleNamespace(
                command=["allure", "generate", results_dir, "-o", report_dir, "--clean"],
                results_dir=results_dir,
                report_dir=report_dir,
                exit_code=0,
                duration_seconds=0.12,
                stdout="Report successfully generated",
                stderr="",
                generated=True,
                reason="Allure report generated successfully.",
                to_dict=lambda: {
                    "command": ["allure", "generate", results_dir, "-o", report_dir, "--clean"],
                    "results_dir": results_dir,
                    "report_dir": report_dir,
                    "exit_code": 0,
                    "duration_seconds": 0.12,
                    "stdout": "Report successfully generated",
                    "stderr": "",
                    "generated": True,
                    "reason": "Allure report generated successfully.",
                },
            )

    monkeypatch.setattr("ai_test_assistant.runtime.cli.AllureReportGenerator", StubGenerator)

    exit_code = run_cli(
        [
            "生成 Allure 报告",
            "--generate-allure-report",
            "custom-results",
            "--allure-output-dir",
            "custom-report",
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "Allure 生成结果" in captured
    assert "command=allure generate custom-results -o custom-report --clean" in captured
    assert "generated=是" in captured
    assert "Report successfully generated" in captured
    assert "allure_generate" in captured
    assert "generate_report" in captured
    assert "Tool 'allure_generate' cannot run local commands during dry-run." not in captured


def test_cli_plain_dry_run_does_not_generate_allure_report(tmp_path: Path, capsys, monkeypatch) -> None:
    config_path = _write_assistant_config(tmp_path)

    class StubGenerator:
        def __init__(self, repo_root: Path) -> None:
            raise AssertionError("Allure generator must not run without --generate-allure-report.")

    monkeypatch.setattr("ai_test_assistant.runtime.cli.AllureReportGenerator", StubGenerator)

    exit_code = run_cli(["生成 Allure 报告", "--dry-run", "--config", str(config_path)])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "Allure 生成结果" not in captured
    assert "allure_generate" in captured
    assert "Tool 'allure_generate' cannot run local commands during dry-run." in captured


def test_allure_generate_tool_boundaries() -> None:
    registry = ToolRegistry.from_yaml("configs/tools.yaml")

    allure_generate_tool = registry.get_tool("allure_generate")
    allure_report_tool = registry.get_tool("allure_report")
    shell_tool = registry.get_tool("shell")
    filesystem_write_tool = registry.get_tool("filesystem_write")
    github_write_tool = registry.get_tool("github_write")

    assert allure_generate_tool.status is ToolStatus.ENABLED
    assert allure_generate_tool.risk_level is ToolRiskLevel.EXECUTE_LOCAL_COMMAND
    assert allure_report_tool.status is ToolStatus.ENABLED
    assert allure_report_tool.risk_level is ToolRiskLevel.READ_ONLY
    assert shell_tool.status is ToolStatus.DISABLED
    assert filesystem_write_tool.status is ToolStatus.DISABLED
    assert github_write_tool.status is ToolStatus.DISABLED
