"""Offline placeholder for future optional sample fetches.

This script deliberately does not make network requests. It prints the URLs that
a future cache-backed fetcher could request after explicit approval.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.optional_data import (  # noqa: E402
    coin_market_chart_url,
    defillama_chains_url,
    defillama_protocol_tvl_url,
    fred_observations_url,
    klines_url,
)


def main() -> int:
    examples = {
        "DefiLlama chains": defillama_chains_url(),
        "DefiLlama Aave TVL": defillama_protocol_tvl_url("aave"),
        "CoinGecko BTC market chart": coin_market_chart_url("bitcoin", days="365"),
        "Binance BTCUSDT klines": klines_url("btcusdt", interval="1d", limit=1000),
        "FRED DGS10 observations": fred_observations_url("DGS10", observation_start="2020-01-01"),
    }
    for label, url in examples.items():
        print(f"{label}: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
