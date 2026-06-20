"""Build data inventory and source coverage outputs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.pipelines.final_research import build_data_inventory

if __name__ == "__main__":
    build_data_inventory()
