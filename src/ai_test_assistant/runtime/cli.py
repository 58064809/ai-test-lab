from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from ai_test_assistant.filesystem import FilesystemMcpReadClient, LocalFilesystemReadAdapter
from ai_test_assistant.github import GitHubMcpReadClient
from ai_test_assistant.intent.router import IntentRouter
from ai_test_assistant.orchestrator.graph import TaskOrchestrator
from ai_test_assistant.reporting import AllureReportGenerator, AllureReportReader
from ai_test_assistant.runtime.output import (
    render_error,
    render_intent_only,
    render_orchestrator_result,
)
from ai_test_assistant.testing import PytestRunner
from ai_test_assistant.tool_registry.permissions import ToolPermissionContext


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-test-assistant",
        description="个人执行型 AI 测试助手的最小 runtime CLI。",
    )
    parser.add_argument("task_text", help="用户自然语言任务")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", default=True, help="只输出计划，不执行工具")
    parser.add_argument("--intent-only", action="store_true", help="只做意图识别，不进入 orchestrator")
    parser.add_argument("--write-memory", action="store_true", help="允许写入任务结果记忆")
    file_read_group = parser.add_mutually_exclusive_group()
    file_read_group.add_argument(
        "--read-file",
        help="显式读取单个仓库相对路径文件，只支持白名单文本文件，使用本地 fallback adapter",
    )
    file_read_group.add_argument(
        "--mcp-read-file",
        help="显式通过 filesystem MCP 读取单个仓库相对路径文件，只支持白名单文本文件",
    )
    parser.add_argument("--github-repo", help="显式指定 GitHub 仓库，格式为 owner/repo")
    parser.add_argument("--github-read-file", help="显式通过 GitHub MCP 读取单个仓库相对路径文件")
    parser.add_argument("--github-ref", help="可选指定 GitHub ref，例如 master 或 main")
    parser.add_argument(
        "--run-pytest",
        nargs="?",
        const="tests",
        help="显式执行仓库内 pytest；不传 target 时默认运行 tests",
    )
    parser.add_argument(
        "--read-allure-report",
        nargs="?",
        const="allure-report",
        metavar="REPORT_DIR",
        help="显式只读读取已有 Allure report 目录摘要；不传 REPORT_DIR 时默认 allure-report",
    )
    parser.add_argument(
        "--generate-allure-report",
        nargs="?",
        const="allure-results",
        metavar="RESULTS_DIR",
        help="显式受控调用 Allure CLI 生成报告；不传 RESULTS_DIR 时默认 allure-results",
    )
    parser.add_argument(
        "--allure-output-dir",
        default="allure-report",
        metavar="REPORT_DIR",
        help="Allure 生成输出目录，默认 allure-report；仅配合 --generate-allure-report 使用",
    )
    parser.add_argument("--show-file-content", action="store_true", help="显式展示允许读取文件的完整内容")
    parser.add_argument("--config", default="configs/assistant.yaml", help="指定配置文件路径")
    return parser


def run_cli(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config_path = Path(args.config)

    if not config_path.exists():
        print(render_error("配置文件不存在", {"config": str(config_path)}))
        return 2

    if args.intent_only:
        router = IntentRouter.from_assistant_config(config_path)
        result = router.route(args.task_text)
        print(render_intent_only(args.task_text, result))
        return 0

    pytest_result = None
    input_files: list[dict[str, object]] = []
    allure_generates: list[dict[str, object]] = []
    allure_reports: list[dict[str, object]] = []
    explicit_tool_executions: list[dict[str, object]] = []
    if args.github_read_file and not args.github_repo:
        print(render_error("GitHub read requires explicit --github-repo.", {"github_read_file": args.github_read_file}))
        return 2

    orchestrator = TaskOrchestrator.from_config(config_path)

    if args.read_file:
        adapter = LocalFilesystemReadAdapter(repo_root=Path.cwd())
        file_read_result = adapter.read_text(args.read_file)
        input_files.append(_build_input_file_entry(args.read_file, file_read_result, source="local_adapter"))
        explicit_tool_executions.append(
            _build_explicit_tool_execution(
                tool_name="filesystem_read",
                source="local_adapter",
                operation="read_file",
                allowed=bool(file_read_result.allowed),
                risk_level="read_only",
                reason="Executed explicitly by CLI argument --read-file.",
            )
        )
    elif args.mcp_read_file:
        client = FilesystemMcpReadClient(repo_root=Path.cwd())
        file_read_result = asyncio.run(client.read_text(args.mcp_read_file))
        input_files.append(_build_input_file_entry(args.mcp_read_file, file_read_result, source="filesystem_mcp"))
        explicit_tool_executions.append(
            _build_explicit_tool_execution(
                tool_name="filesystem_mcp_read",
                source="filesystem_mcp",
                operation="read_file",
                allowed=bool(file_read_result.allowed),
                risk_level="read_only",
                reason="Executed explicitly by CLI argument --mcp-read-file.",
            )
        )
    elif args.github_read_file:
        if orchestrator.tool_registry is None:
            print(render_error("github_read is not authorized.", {"tool_registry": "tool registry config is missing."}))
            return 2

        try:
            permission = orchestrator.tool_registry.evaluate_execution(
                "github_read",
                context=ToolPermissionContext(dry_run=False, allow_external_network=True),
            )
        except KeyError as exc:
            print(render_error("github_read is not authorized.", {"reason": str(exc)}))
            return 2
        if not permission.allowed:
            print(render_error("github_read is not authorized.", {"reason": "; ".join(permission.reasons)}))
            return 2

        client = GitHubMcpReadClient()
        file_read_result = asyncio.run(client.read_file(args.github_repo, args.github_read_file, ref=args.github_ref))
        input_files.append(_build_github_input_file_entry(args.github_read_file, file_read_result))
        explicit_tool_executions.append(
            _build_explicit_tool_execution(
                tool_name="github_read",
                source="github_mcp",
                operation="read_file",
                allowed=bool(file_read_result.allowed),
                risk_level="external_network",
                reason="Executed explicitly by CLI argument --github-read-file.",
            )
        )

    if args.run_pytest is not None:
        if orchestrator.tool_registry is None:
            print(render_error("pytest_runner 未加载", {"tool_registry": "tool registry 配置不存在"}))
            return 2

        permission = orchestrator.tool_registry.evaluate_execution(
            "pytest_runner",
            context=ToolPermissionContext(dry_run=False, allow_execute_local_command=True),
        )
        if not permission.allowed:
            print(render_error("pytest_runner 不允许执行", {"reason": "；".join(permission.reasons)}))
            return 2

        try:
            pytest_result = PytestRunner(repo_root=Path.cwd()).run(args.run_pytest)
        except ValueError as exc:
            print(render_error("pytest target 不合法", {"target": str(args.run_pytest), "reason": str(exc)}))
            return 2
        explicit_tool_executions.append(
            _build_explicit_tool_execution(
                tool_name="pytest_runner",
                source="pytest_runner",
                operation="run_pytest",
                allowed=True,
                risk_level="execute_local_command",
                reason="Executed explicitly by CLI argument --run-pytest.",
            )
        )

    if args.generate_allure_report is not None:
        if orchestrator.tool_registry is None:
            print(render_error("allure_generate is not authorized.", {"tool_registry": "tool registry config is missing."}))
            return 2

        try:
            permission = orchestrator.tool_registry.evaluate_execution(
                "allure_generate",
                context=ToolPermissionContext(
                    dry_run=False,
                    allow_execute_local_command=True,
                    allow_write_project_files=True,
                ),
            )
        except KeyError as exc:
            print(render_error("allure_generate is not authorized.", {"reason": str(exc)}))
            return 2
        if not permission.allowed:
            print(render_error("allure_generate is not authorized.", {"reason": "; ".join(permission.reasons)}))
            return 2

        generate_result = AllureReportGenerator(repo_root=Path.cwd()).generate(
            args.generate_allure_report,
            args.allure_output_dir,
        )
        allure_generates.append(generate_result.to_dict())
        explicit_tool_executions.append(
            _build_explicit_tool_execution(
                tool_name="allure_generate",
                source="allure_cli",
                operation="generate_report",
                allowed=bool(generate_result.generated),
                risk_level="execute_local_command",
                reason=generate_result.reason,
            )
        )

    if args.read_allure_report is not None:
        if orchestrator.tool_registry is None:
            print(render_error("allure_report is not authorized.", {"tool_registry": "tool registry config is missing."}))
            return 2

        try:
            permission = orchestrator.tool_registry.evaluate_execution(
                "allure_report",
                context=ToolPermissionContext(dry_run=False),
            )
        except KeyError as exc:
            print(render_error("allure_report is not authorized.", {"reason": str(exc)}))
            return 2
        if not permission.allowed:
            print(render_error("allure_report is not authorized.", {"reason": "; ".join(permission.reasons)}))
            return 2

        allure_summary = AllureReportReader(repo_root=Path.cwd()).read_summary(args.read_allure_report)
        allure_reports.append(allure_summary.to_dict())
        explicit_tool_executions.append(
            _build_explicit_tool_execution(
                tool_name="allure_report",
                source="allure_report",
                operation="read_summary",
                allowed=bool(allure_summary.allowed),
                risk_level="read_only",
                reason=allure_summary.reason,
            )
        )

    result = orchestrator.run(
        args.task_text,
        dry_run=args.dry_run,
        write_memory=args.write_memory,
        input_files=input_files,
        allure_generates=allure_generates,
        allure_reports=allure_reports,
        explicit_tool_executions=explicit_tool_executions,
    )

    print(
        render_orchestrator_result(
            result,
            write_memory=args.write_memory,
            show_file_content=args.show_file_content,
            pytest_result=pytest_result,
        )
    )
    return 0


def _build_input_file_entry(
    requested_path: str,
    file_read_result,
    *,
    source: str,
) -> dict[str, object]:
    return {
        "requested_path": requested_path,
        "path": file_read_result.path,
        "allowed": file_read_result.allowed,
        "content": file_read_result.content,
        "reason": file_read_result.reason,
        "truncated": file_read_result.truncated,
        "source": source,
    }


def _build_github_input_file_entry(requested_path: str, file_read_result) -> dict[str, object]:
    return {
        "requested_path": requested_path,
        "path": file_read_result.target,
        "repository": file_read_result.repository,
        "operation": file_read_result.operation,
        "allowed": file_read_result.allowed,
        "content": file_read_result.content,
        "reason": file_read_result.reason,
        "truncated": file_read_result.truncated,
        "source": "github_mcp",
    }


def _build_explicit_tool_execution(
    *,
    tool_name: str,
    source: str,
    operation: str,
    allowed: bool,
    risk_level: str,
    reason: str,
) -> dict[str, object]:
    return {
        "tool_name": tool_name,
        "source": source,
        "operation": operation,
        "allowed": allowed,
        "risk_level": risk_level,
        "authorization": "CLI explicit approval",
        "reason": reason,
    }
