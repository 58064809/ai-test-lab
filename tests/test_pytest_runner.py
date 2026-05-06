from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

from ai_test_assistant.testing import PytestRunner


def test_pytest_runner_uses_default_tests_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    runner = PytestRunner(tmp_path)
    captured: dict[str, object] = {}

    def fake_run(args, cwd, capture_output, text, shell, check):
        captured["args"] = args
        captured["cwd"] = cwd
        captured["capture_output"] = capture_output
        captured["text"] = text
        captured["shell"] = shell
        captured["check"] = check
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr("ai_test_assistant.testing.pytest_runner.subprocess.run", fake_run)

    result = runner.run()

    assert result.target == "tests"
    assert result.command == [sys.executable, "-m", "pytest", "tests"]
    assert captured["args"] == [sys.executable, "-m", "pytest", "tests"]
    assert captured["cwd"] == tmp_path.resolve()
    assert captured["capture_output"] is True
    assert captured["text"] is True
    assert captured["shell"] is False
    assert captured["check"] is False


def test_pytest_runner_uses_sys_executable_and_repo_relative_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_path = tmp_path / "tests" / "test_runtime_cli.py"
    target_path.parent.mkdir()
    target_path.write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")
    runner = PytestRunner(tmp_path)
    captured: dict[str, object] = {}

    def fake_run(args, cwd, capture_output, text, shell, check):
        captured["args"] = args
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr("ai_test_assistant.testing.pytest_runner.subprocess.run", fake_run)

    result = runner.run("tests/test_runtime_cli.py")

    assert result.command == [sys.executable, "-m", "pytest", "tests/test_runtime_cli.py"]
    assert captured["args"] == [sys.executable, "-m", "pytest", "tests/test_runtime_cli.py"]


def test_pytest_runner_allows_only_fixed_allure_results_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    runner = PytestRunner(tmp_path)
    captured: dict[str, object] = {}

    def fake_run(args, cwd, capture_output, text, shell, check):
        captured["args"] = args
        captured["shell"] = shell
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr("ai_test_assistant.testing.pytest_runner.subprocess.run", fake_run)

    result = runner.run("tests", allure_results_dir="allure-results")

    assert result.command == [sys.executable, "-m", "pytest", "tests", "--alluredir=allure-results"]
    assert captured["args"] == [sys.executable, "-m", "pytest", "tests", "--alluredir=allure-results"]
    assert captured["shell"] is False


def test_pytest_runner_rejects_custom_allure_results_dir(tmp_path: Path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    runner = PytestRunner(tmp_path)

    with pytest.raises(ValueError, match="allure-results"):
        runner.run("tests", allure_results_dir="custom-results")


@pytest.mark.parametrize(
    "target",
    [
        "C:/temp/test_file.py",
        "D:\\temp\\test_file.py",
        "../tests/test_runtime_cli.py",
        "tests/*.py",
        "tests --maxfail=1",
    ],
)
def test_pytest_runner_rejects_unsafe_targets(target: str, tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    runner = PytestRunner(tmp_path)

    with pytest.raises(ValueError):
        runner.run(target)


def test_pytest_runner_truncates_long_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    runner = PytestRunner(tmp_path)

    def fake_run(args, cwd, capture_output, text, shell, check):
        return SimpleNamespace(
            returncode=1,
            stdout="a" * 25_000,
            stderr="b" * 25_000,
        )

    monkeypatch.setattr("ai_test_assistant.testing.pytest_runner.subprocess.run", fake_run)

    result = runner.run()

    assert len(result.stdout) <= runner.MAX_OUTPUT_CHARS + 4
    assert len(result.stderr) <= runner.MAX_OUTPUT_CHARS + 4
    assert result.passed is False
