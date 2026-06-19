"""Canonical public reproduction entry point.

The maintained analytics artifacts are tracked in the repository. This wrapper
exports the clean public packet under outputs/ without refreshing raw Data/.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.export_outputs import main as export_outputs_main  # noqa: E402
from cqresearch.analysis.market_structure_pipeline import (  # noqa: E402
    build_outputs as build_market_structure_outputs,
    normalize_cache_to_curated,
)


def main() -> int:
    status = export_outputs_main()
    if status != 0:
        return status
    normalize_cache_to_curated(ROOT, cache_only=True)
    build_market_structure_outputs(ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
