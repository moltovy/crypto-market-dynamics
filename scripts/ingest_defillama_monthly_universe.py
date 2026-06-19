"""Ingest a local DefiLlama monthly top200 point-in-time universe CSV."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.analysis.market_structure_pipeline import update_master_inventory  # noqa: E402
from cqresearch.analysis.market_universe import (  # noqa: E402
    UniverseValidationError,
    ingest_defillama_monthly_universe,
)


def main() -> int:
    try:
        out_path, skipped = ingest_defillama_monthly_universe(ROOT)
    except UniverseValidationError as exc:
        print(f"[error] {exc}")
        return 1
    if out_path is None:
        for item in skipped:
            print(f"[skip] {item}")
        return 0
    update_master_inventory(ROOT)
    print(f"[ok] {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
