#!/usr/bin/env python3
"""Run Robot Framework acceptance suites and exit with their status."""

from __future__ import annotations

import sys
from pathlib import Path

from robot import run_cli

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "tests" / "acceptance.robot"
OUTPUT_DIR = Path(__file__).resolve().parent / "results"


def main() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    args = [
        "--outputdir",
        str(OUTPUT_DIR),
        "--pythonpath",
        str(ROOT / "src"),
        str(SUITE),
    ]
    return int(run_cli(args, exit=False))


if __name__ == "__main__":
    raise SystemExit(main())
