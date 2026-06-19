"""Fetch optional market-structure raw payloads into gitignored data_cache."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.data.market_structure_cache import CacheLayout  # noqa: E402
from cqresearch.data.market_structure_clients import fetch_many  # noqa: E402
from cqresearch.data.market_structure_endpoints import (  # noqa: E402
    binance_specs,
    cmc_specs,
    defillama_specs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Do not network; write only redacted manifest rows.")
    parser.add_argument("--cache-only", action="store_true", help="Do not network; report cache hits/misses.")
    parser.add_argument("--source", choices=["all", "defillama", "binance", "coinmarketcap"], default="all")
    parser.add_argument(
        "--core-symbols",
        default="BTCUSDT,ETHUSDT",
        help="Comma-separated Binance symbols for core kline/funding requests.",
    )
    return parser.parse_args()


def selected_specs(source: str, core_symbols: list[str]):
    specs = []
    if source in {"all", "defillama"}:
        specs.extend(defillama_specs())
    if source in {"all", "binance"}:
        specs.extend(binance_specs(core_symbols))
    if source in {"all", "coinmarketcap"}:
        specs.extend(cmc_specs())
    return specs


def main() -> int:
    args = parse_args()
    load_dotenv(ROOT / ".env")
    core_symbols = [item.strip().upper() for item in args.core_symbols.split(",") if item.strip()]
    layout = CacheLayout.from_env(ROOT)
    secrets = [os.getenv("DEFILLAMA_API_KEY", ""), os.getenv("CMC_API_KEY", "")]
    results = fetch_many(
        selected_specs(args.source, core_symbols),
        layout,
        dry_run=args.dry_run,
        cache_only=args.cache_only,
        secrets=secrets,
    )
    frame = pd.DataFrame([result.as_dict() for result in results])
    print(frame[["source", "dataset", "status", "message"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
