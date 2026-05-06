from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import subprocess
import sys
import time


@dataclass(slots=True)
class PytestRunResult:
    command: list[str]
    target: str
    exit_code: int
    duration_seconds: float
    stdout: str
    stderr: str
    passed: bool
    reason: str


class PytestRunner:
    DEFAULT_TARGET = "tests"
    MAX_OUTPUT_CHARS = 20_000
    _GLOB_CHARS = ("*", "?", "[", "]")

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()

    def run(self, target: str = DEFAULT_TARGET, *, allure_results_dir: str | None = None) -> PytestRunResult:
        normalized_target = self._validate_target(target)
        command = [sys.executable, "-m", "pytest", normalized_target]
        if allure_results_dir is not None:
            normalized_allure_results_dir = self._validate_allure_results_dir(allure_results_dir)
            command.append(f"--alluredir={normalized_allure_results_dir}")

        start = time.perf_counter()
        completed = subprocess.run(
            command,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            shell=False,
            check=False,
        )
        duration_seconds = time.perf_counter() - start

        stdout = self._truncate_output(completed.stdout)
        stderr = self._truncate_output(completed.stderr)
        passed = completed.returncode == 0
        reason = "Pytest run completed successfully." if passed else "Pytest run completed with failures."

        return PytestRunResult(
            command=command,
            target=normalized_target,
            exit_code=completed.returncode,
            duration_seconds=round(duration_seconds, 3),
            stdout=stdout,
            stderr=stderr,
            passed=passed,
            reason=reason,
        )

    def _validate_target(self, target: str) -> str:
        raw_target = target.strip()
        if not raw_target:
            raw_target = self.DEFAULT_TARGET

        normalized_input = raw_target.replace("\\", "/")
        if any(char.isspace() for char in normalized_input):
            raise ValueError("Pytest target must be a single repo-relative path without extra arguments.")
        if any(char in normalized_input for char in self._GLOB_CHARS):
            raise ValueError("Pytest target glob patterns are not allowed.")
        if normalized_input.startswith("-"):
            raise ValueError("Pytest target flags are not allowed.")
        if normalized_input.startswith("/") or Path(normalized_input).is_absolute():
            raise ValueError("Pytest target must not be an absolute path.")

        pure_path = PurePosixPath(normalized_input)
        if any(part == ".." for part in pure_path.parts):
            raise ValueError("Pytest target path traversal is not allowed.")

        normalized_target = pure_path.as_posix()
        if normalized_target.startswith("./"):
            normalized_target = normalized_target[2:]
        if not normalized_target:
            normalized_target = self.DEFAULT_TARGET

        resolved_target = (self.repo_root / normalized_target).resolve()
        try:
            resolved_target.relative_to(self.repo_root)
        except ValueError as exc:
            raise ValueError("Pytest target must stay within the repository root.") from exc

        if not resolved_target.exists():
            raise ValueError("Pytest target does not exist within the repository.")

        return normalized_target

    def _validate_allure_results_dir(self, value: str) -> str:
        normalized_value = value.strip().replace("\\", "/")
        if normalized_value != "allure-results":
            raise ValueError("Pytest Allure output is fixed to --alluredir=allure-results.")
        return normalized_value

    def _truncate_output(self, value: str) -> str:
        if len(value) <= self.MAX_OUTPUT_CHARS:
            return value
        return value[: self.MAX_OUTPUT_CHARS] + "\n..."
