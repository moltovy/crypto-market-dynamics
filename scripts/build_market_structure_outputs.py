"""Build public market-structure tables, figures, reports, and manifest patch."""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.analysis.market_structure_pipeline import build_outputs  # noqa: E402


def main() -> int:
    load_dotenv(ROOT / ".env")
    result = build_outputs(ROOT)
    for path in result.output_files:
        print(f"[ok] {path.relative_to(ROOT)}")
    for item in result.skipped:
        print(f"[skip] {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
