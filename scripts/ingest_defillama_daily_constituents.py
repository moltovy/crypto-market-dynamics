"""Ingest a local DefiLlama daily constituent OHLCV sample."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.analysis.constituent_rotation import (  # noqa: E402
    ingest_defillama_daily_constituents,
)
from cqresearch.analysis.market_structure_pipeline import update_master_inventory  # noqa: E402


def main() -> int:
    out_path, skipped = ingest_defillama_daily_constituents(ROOT)
    if out_path:
        print(f"[ok] {out_path.relative_to(ROOT)}")
        update_master_inventory(ROOT)
    for item in skipped:
        print(f"[skip] {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
