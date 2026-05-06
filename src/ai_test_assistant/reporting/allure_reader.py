from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path, PurePosixPath
from typing import Any


@dataclass(slots=True)
class AllureReportSummary:
    allowed: bool
    report_dir: str
    total: int | None
    passed: int | None
    failed: int | None
    broken: int | None
    skipped: int | None
    unknown: int | None
    duration_ms: int | None
    top_failures: list[str]
    reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class AllureReportReader:
    """Read a pre-generated Allure report directory without running Allure CLI."""

    DEFAULT_REPORT_DIR = "allure-report"
    _GLOB_CHARS = ("*", "?", "[", "]")
    _SENSITIVE_PARTS = (".env", "token", "secret", "password")
    _WIDGET_FILES = {
        "summary": "summary.json",
        "duration": "duration.json",
        "categories": "categories.json",
        "suites": "suites.json",
    }

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()

    def read_summary(self, report_dir: str = DEFAULT_REPORT_DIR) -> AllureReportSummary:
        try:
            normalized_report_dir = self._validate_report_dir(report_dir)
        except ValueError as exc:
            return self._failure(str(report_dir), str(exc))

        widgets_dir = self.repo_root / normalized_report_dir / "widgets"
        summary_path = widgets_dir / self._WIDGET_FILES["summary"]
        if not summary_path.is_file():
            return self._failure(
                normalized_report_dir,
                "Missing required Allure report file: widgets/summary.json.",
            )

        try:
            summary_json = self._read_json(summary_path)
            duration_json = self._read_optional_json(widgets_dir / self._WIDGET_FILES["duration"])
            categories_json = self._read_optional_json(widgets_dir / self._WIDGET_FILES["categories"])
            suites_json = self._read_optional_json(widgets_dir / self._WIDGET_FILES["suites"])
        except ValueError as exc:
            return self._failure(normalized_report_dir, str(exc))

        statistic = summary_json.get("statistic") if isinstance(summary_json, dict) else None
        statistic = statistic if isinstance(statistic, dict) else {}
        return AllureReportSummary(
            allowed=True,
            report_dir=normalized_report_dir,
            total=self._as_int(statistic.get("total")),
            passed=self._as_int(statistic.get("passed")),
            failed=self._as_int(statistic.get("failed")),
            broken=self._as_int(statistic.get("broken")),
            skipped=self._as_int(statistic.get("skipped")),
            unknown=self._as_int(statistic.get("unknown")),
            duration_ms=self._extract_duration_ms(summary_json, duration_json),
            top_failures=self._extract_top_failures(categories_json, suites_json),
            reason="Read Allure report summary from existing report widgets.",
        )

    def _validate_report_dir(self, report_dir: str) -> str:
        raw = report_dir.strip() or self.DEFAULT_REPORT_DIR
        normalized_input = raw.replace("\\", "/")
        if any(char in normalized_input for char in self._GLOB_CHARS):
            raise ValueError("Allure report path glob patterns are not allowed.")
        if normalized_input.startswith("/") or Path(normalized_input).is_absolute():
            raise ValueError("Allure report path must be repo-relative, not absolute.")

        pure_path = PurePosixPath(normalized_input)
        if any(part == ".." for part in pure_path.parts):
            raise ValueError("Allure report path traversal is not allowed.")
        if any(self._is_sensitive_part(part) for part in pure_path.parts):
            raise ValueError("Sensitive Allure report path is blocked.")

        normalized_report_dir = pure_path.as_posix()
        if normalized_report_dir.startswith("./"):
            normalized_report_dir = normalized_report_dir[2:]
        if not normalized_report_dir or normalized_report_dir == ".":
            normalized_report_dir = self.DEFAULT_REPORT_DIR

        resolved_report_dir = (self.repo_root / normalized_report_dir).resolve()
        try:
            resolved_report_dir.relative_to(self.repo_root)
        except ValueError as exc:
            raise ValueError("Allure report path must stay within the repository root.") from exc

        return normalized_report_dir

    def _read_json(self, path: Path) -> Any:
        try:
            path.resolve().relative_to(self.repo_root)
        except ValueError as exc:
            raise ValueError("Allure widget path must stay within the repository root.") from exc
        if not path.is_file():
            raise ValueError(f"Missing Allure widget file: {path.name}.")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in Allure widget file: {path.name}.") from exc
        except OSError as exc:
            raise ValueError(f"Unable to read Allure widget file: {path.name}.") from exc

    def _read_optional_json(self, path: Path) -> Any | None:
        if not path.is_file():
            return None
        return self._read_json(path)

    def _extract_duration_ms(self, summary_json: Any, duration_json: Any | None) -> int | None:
        if isinstance(summary_json, dict):
            time_data = summary_json.get("time")
            if isinstance(time_data, dict):
                duration = self._as_int(time_data.get("duration"))
                if duration is not None:
                    return duration
                start = self._as_int(time_data.get("start"))
                stop = self._as_int(time_data.get("stop"))
                if start is not None and stop is not None and stop >= start:
                    return stop - start

        duration_value = self._find_first_int_by_key(duration_json, {"duration", "sumDuration"})
        return duration_value

    def _extract_top_failures(self, categories_json: Any | None, suites_json: Any | None) -> list[str]:
        failures: list[str] = []
        for source in (categories_json, suites_json):
            self._collect_failure_names(source, failures)
            if len(failures) >= 10:
                break

        deduplicated: list[str] = []
        seen: set[str] = set()
        for item in failures:
            if item in seen:
                continue
            seen.add(item)
            deduplicated.append(item)
            if len(deduplicated) >= 10:
                break
        return deduplicated

    def _collect_failure_names(self, value: Any, failures: list[str]) -> None:
        if len(failures) >= 10:
            return
        if isinstance(value, list):
            for item in value:
                self._collect_failure_names(item, failures)
                if len(failures) >= 10:
                    return
            return
        if not isinstance(value, dict):
            return

        status = str(value.get("status") or "").lower()
        name = value.get("name")
        if status in {"failed", "broken"} and isinstance(name, str) and name.strip():
            failures.append(name.strip())
            if len(failures) >= 10:
                return

        for child_key in ("children", "items"):
            children = value.get(child_key)
            if children is not None:
                self._collect_failure_names(children, failures)
                if len(failures) >= 10:
                    return

    def _find_first_int_by_key(self, value: Any, keys: set[str]) -> int | None:
        if isinstance(value, dict):
            for key in keys:
                found = self._as_int(value.get(key))
                if found is not None:
                    return found
            for nested in value.values():
                found = self._find_first_int_by_key(nested, keys)
                if found is not None:
                    return found
        if isinstance(value, list):
            for item in value:
                found = self._find_first_int_by_key(item, keys)
                if found is not None:
                    return found
        return None

    def _as_int(self, value: object) -> int | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        return None

    def _is_sensitive_part(self, part: str) -> bool:
        lowered = part.lower()
        return any(pattern in lowered for pattern in self._SENSITIVE_PARTS)

    def _failure(self, report_dir: str, reason: str) -> AllureReportSummary:
        return AllureReportSummary(
            allowed=False,
            report_dir=report_dir,
            total=None,
            passed=None,
            failed=None,
            broken=None,
            skipped=None,
            unknown=None,
            duration_ms=None,
            top_failures=[],
            reason=reason,
        )
