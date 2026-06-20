"""Build the six README figures, gallery appendix, and QA contact sheet."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.viz.public_figures import build_public_figures

if __name__ == "__main__":
    build_public_figures()
