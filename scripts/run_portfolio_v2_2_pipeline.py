"""Build the Portfolio v2.2 advanced diagnostics packet.

The pipeline uses the frozen committed panel and writes all v2.2 artifacts
under ``reports/portfolio_v2_2/``. It does not refresh or mutate raw ``Data/``.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.analysis.portfolio_v2_2 import run_portfolio_v2_2_pipeline  # noqa: E402


def main() -> int:
    try:
        result = run_portfolio_v2_2_pipeline()
    except Exception as exc:
        print(f"[FAIL] portfolio_v2_2 pipeline: {exc}")
        return 1

    print("[ok] portfolio_v2_2 complete")
    print(f"[ok] tables: {len(result.tables)}")
    print(f"[ok] figures: {len(result.figures)}")
    print(f"[ok] reports: {len(result.reports)}")
    print(f"[ok] model cards: {len(result.model_cards)}")
    print(f"[ok] manifest: {result.manifest_path}")
    if result.optional_failures:
        print("[warn] optional failures were recorded in diagnostics/optional_failures.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
