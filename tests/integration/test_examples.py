from __future__ import annotations

from pathlib import Path

import pytest

from robot import run_cli

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = sorted((ROOT / "examples").glob("*.robot"))


@pytest.mark.parametrize("suite", EXAMPLES, ids=lambda p: p.name)
def test_example_suite(suite: Path) -> None:
    output_dir = ROOT / "tests" / "robot" / "results" / "examples" / suite.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    rc = run_cli(
        [
            "--outputdir",
            str(output_dir),
            "--pythonpath",
            str(ROOT / "src"),
            str(suite),
        ],
        exit=False,
    )
    assert rc == 0, f"Robot example failed: {suite}"
