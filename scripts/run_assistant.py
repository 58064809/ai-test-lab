from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
SRC_ROOT_STR = str(SRC_ROOT)

if SRC_ROOT_STR not in sys.path:
    sys.path.insert(0, SRC_ROOT_STR)

from ai_test_assistant.runtime.cli import run_cli


if __name__ == "__main__":
    raise SystemExit(run_cli())
