"""Normalize market-structure cache into tracked curated CSVs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.analysis.market_structure_pipeline import normalize_cache_to_curated  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-only", action="store_true", help="Normalize available cache only; no network calls.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_dotenv(ROOT / ".env")
    result = normalize_cache_to_curated(ROOT, cache_only=args.cache_only)
    for path in result.curated_files:
        print(f"[ok] {path.relative_to(ROOT)}")
    for item in result.skipped:
        print(f"[skip] {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
