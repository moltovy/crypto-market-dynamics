"""Validate the canonical public output surface."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.pipelines.final_research import check_public_surface

if __name__ == "__main__":
    check_public_surface()
