"""Build the canonical data-foundation research module."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.research.data_foundation import build_data_foundation

if __name__ == "__main__":
    build_data_foundation(ROOT)
