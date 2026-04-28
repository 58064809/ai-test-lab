from __future__ import annotations

import argparse
from pathlib import Path

from ai_test_assistant.filesystem import LocalFilesystemReadAdapter
from ai_test_assistant.intent.router import IntentRouter
from ai_test_assistant.orchestrator.graph import TaskOrchestrator
from ai_test_assistant.runtime.output import render_error, render_intent_only, render_orchestrator_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-test-assistant",
        description="个人执行型 AI 测试助手的最小 runtime CLI。",
    )
    parser.add_argument("task_text", help="用户自然语言任务")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", default=True, help="只输出计划，不执行工具")
    parser.add_argument("--intent-only", action="store_true", help="只做意图识别，不进入 orchestrator")
    parser.add_argument("--write-memory", action="store_true", help="允许写入任务结果记忆")
    parser.add_argument("--read-file", help="显式读取单个仓库相对路径文件，只支持白名单文本文件")
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

    input_files: list[dict[str, object]] = []
    if args.read_file:
        adapter = LocalFilesystemReadAdapter(repo_root=Path.cwd())
        file_read_result = adapter.read_text(args.read_file)
        input_files.append(
            {
                "requested_path": args.read_file,
                "path": file_read_result.path,
                "allowed": file_read_result.allowed,
                "content": file_read_result.content,
                "reason": file_read_result.reason,
                "truncated": file_read_result.truncated,
            }
        )

    orchestrator = TaskOrchestrator.from_config(config_path)
    result = orchestrator.run(
        args.task_text,
        dry_run=args.dry_run,
        write_memory=args.write_memory,
        input_files=input_files,
    )

    print(
        render_orchestrator_result(
            result,
            write_memory=args.write_memory,
            show_file_content=args.show_file_content,
        )
    )
    return 0
