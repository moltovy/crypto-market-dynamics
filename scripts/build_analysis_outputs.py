"""Compatibility wrapper for the canonical research-surface build."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.pipelines.research import run_research

if __name__ == "__main__":
    run_research(module="all", root=ROOT)
