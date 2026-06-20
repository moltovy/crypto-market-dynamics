"""Build canonical daily, weekly, and monthly feature stores."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.pipelines.final_research import build_feature_store, write_config_files

if __name__ == "__main__":
    write_config_files()
    build_feature_store()
