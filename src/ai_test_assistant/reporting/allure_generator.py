from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import time


@dataclass(slots=True)
class AllureGenerateResult:
    command: list[str]
    results_dir: str
    report_dir: str
    exit_code: int | None
    duration_seconds: float
    stdout: str
    stderr: str
    generated: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class AllureReportGenerator:
    DEFAULT_RESULTS_DIR = "allure-results"
    DEFAULT_REPORT_DIR = "allure-report"
    MAX_OUTPUT_CHARS = 20_000
    _GLOB_CHARS = ("*", "?", "[", "]")
    _SENSITIVE_PARTS = (".env", "token", "secret", "password")

    def __init__(self, repo_root: Path, executable: str = "allure") -> None:
        self.repo_root = repo_root.resolve()
        self.executable = executable

    def generate(
        self,
        results_dir: str = DEFAULT_RESULTS_DIR,
        report_dir: str = DEFAULT_REPORT_DIR,
    ) -> AllureGenerateResult:
        start = time.perf_counter()
        try:
            normalized_results_dir = self._validate_dir(results_dir, default=self.DEFAULT_RESULTS_DIR, must_exist=True)
            normalized_report_dir = self._validate_dir(report_dir, default=self.DEFAULT_REPORT_DIR, must_exist=False)
        except ValueError as exc:
            return self._failure(
                results_dir=str(results_dir),
                report_dir=str(report_dir),
                reason=str(exc),
                duration_seconds=time.perf_counter() - start,
            )

        resolved_executable = self._resolve_executable()
        command = [
            resolved_executable or self.executable,
            "generate",
            normalized_results_dir,
            "-o",
            normalized_report_dir,
            "--clean",
        ]
        if resolved_executable is None:
            return AllureGenerateResult(
                command=command,
                results_dir=normalized_results_dir,
                report_dir=normalized_report_dir,
                exit_code=None,
                duration_seconds=round(time.perf_counter() - start, 3),
                stdout="",
                stderr="",
                generated=False,
                reason="Allure CLI executable not found.",
            )

        try:
            completed = subprocess.run(
                command,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
        except FileNotFoundError:
            return AllureGenerateResult(
                command=command,
                results_dir=normalized_results_dir,
                report_dir=normalized_report_dir,
                exit_code=None,
                duration_seconds=round(time.perf_counter() - start, 3),
                stdout="",
                stderr="",
                generated=False,
                reason="Allure CLI executable not found.",
            )

        generated = completed.returncode == 0
        return AllureGenerateResult(
            command=command,
            results_dir=normalized_results_dir,
            report_dir=normalized_report_dir,
            exit_code=completed.returncode,
            duration_seconds=round(time.perf_counter() - start, 3),
            stdout=self._truncate_output(completed.stdout),
            stderr=self._truncate_output(completed.stderr),
            generated=generated,
            reason="Allure report generated successfully." if generated else "Allure report generation failed.",
        )

    def _resolve_executable(self) -> str | None:
        resolved = shutil.which(self.executable)
        if resolved:
            return resolved

        if self.executable != "allure" or os.name != "nt":
            return None

        for candidate_name in ("allure.cmd", "allure.bat", "allure.exe"):
            resolved = shutil.which(candidate_name)
            if resolved:
                return resolved

        user_profile = os.environ.get("USERPROFILE")
        if not user_profile:
            return None

        scoop_candidates = [
            Path(user_profile) / "scoop" / "shims" / "allure.cmd",
            Path(user_profile) / "scoop" / "shims" / "allure.exe",
            Path(user_profile) / "scoop" / "apps" / "allure" / "current" / "bin" / "allure.bat",
            Path(user_profile) / "scoop" / "apps" / "allure" / "current" / "bin" / "allure",
        ]
        for candidate in scoop_candidates:
            if candidate.is_file():
                return str(candidate)

        return None

    def _validate_dir(self, value: str, *, default: str, must_exist: bool) -> str:
        raw = value.strip() or default
        normalized_input = raw.replace("\\", "/")
        if any(char in normalized_input for char in self._GLOB_CHARS):
            raise ValueError("Allure path glob patterns are not allowed.")
        if normalized_input.startswith("/") or Path(normalized_input).is_absolute():
            raise ValueError("Allure path must be repo-relative, not absolute.")

        pure_path = PurePosixPath(normalized_input)
        if any(part == ".." for part in pure_path.parts):
            raise ValueError("Allure path traversal is not allowed.")
        if any(self._is_sensitive_part(part) for part in pure_path.parts):
            raise ValueError("Sensitive Allure path is blocked.")

        normalized_dir = pure_path.as_posix()
        if normalized_dir.startswith("./"):
            normalized_dir = normalized_dir[2:]
        if not normalized_dir or normalized_dir == ".":
            normalized_dir = default

        resolved_dir = (self.repo_root / normalized_dir).resolve()
        try:
            resolved_dir.relative_to(self.repo_root)
        except ValueError as exc:
            raise ValueError("Allure path must stay within the repository root.") from exc

        if must_exist and not resolved_dir.is_dir():
            raise ValueError("Allure results directory does not exist within the repository.")

        return normalized_dir

    def _truncate_output(self, value: str) -> str:
        if len(value) <= self.MAX_OUTPUT_CHARS:
            return value
        return value[: self.MAX_OUTPUT_CHARS] + "\n..."

    def _is_sensitive_part(self, part: str) -> bool:
        lowered = part.lower()
        return any(pattern in lowered for pattern in self._SENSITIVE_PARTS)

    def _failure(
        self,
        *,
        results_dir: str,
        report_dir: str,
        reason: str,
        duration_seconds: float,
    ) -> AllureGenerateResult:
        return AllureGenerateResult(
            command=[],
            results_dir=results_dir,
            report_dir=report_dir,
            exit_code=None,
            duration_seconds=round(duration_seconds, 3),
            stdout="",
            stderr="",
            generated=False,
            reason=reason,
        )
