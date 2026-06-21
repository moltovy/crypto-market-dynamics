"""Compatibility wrapper for building canonical research figures."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.pipelines.research import build_research_figures

if __name__ == "__main__":
    build_research_figures(module="all", root=ROOT)
