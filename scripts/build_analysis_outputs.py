"""Build canonical analysis tables, reports, and model cards."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.pipelines.final_research import build_analysis_outputs

if __name__ == "__main__":
    build_analysis_outputs()
