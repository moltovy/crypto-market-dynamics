"""Idempotent full-pipeline runner.

Execute in order to reproduce every artifact in this repo:

    python scripts/run_full_pipeline.py

Each sub-script writes to a dated folder (``YYYY-MM-DD``) so reruns never
overwrite prior results.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    "scripts/inspect_core_files.py",
    "scripts/01_build_master_panel.py",
    "scripts/02_run_analyses.py",
    "scripts/03_make_figures.py",
    "scripts/04_descriptives_and_summaries.py",
    "scripts/05_robustness.py",
]


def main() -> int:
    for rel in STEPS:
        path = ROOT / rel
        print(f"\n== running {rel} ==")
        rc = subprocess.call([sys.executable, str(path)], cwd=str(ROOT))
        if rc != 0:
            print(f"[FAIL] {rel} exited {rc}")
            return rc
    print("\n[ok] full pipeline complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
