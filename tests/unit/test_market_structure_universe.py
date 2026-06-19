from __future__ import annotations

import pandas as pd

from cqresearch.analysis.asset_classification import classify_asset, classify_symbol_frame
from cqresearch.analysis.market_universe import (
    build_binance_liquidity_ranks,
    market_cap_top100_gap_report,
)


def test_asset_classification_and_liquidity_universe_are_not_market_cap() -> None:
    overrides = {"stablecoins": {"USDC"}, "base_assets": {"BTC"}}
    assert classify_asset("USDC", overrides) == "stablecoins"
    assert classify_asset("BTC", overrides) == "base_assets"

    symbols = classify_symbol_frame(
        pd.DataFrame({"symbol": ["BTCUSDT", "USDCUSDT"], "base_asset": ["BTC", "USDC"]}),
        overrides,
    )
    assert set(symbols["asset_class"]) == {"base_assets", "stablecoins"}

    klines = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=40, freq="D").tolist() * 2,
            "symbol": ["BTCUSDT"] * 40 + ["ETHUSDT"] * 40,
            "quote_asset_volume": [100.0] * 40 + [50.0] * 40,
        }
    )
    ranks = build_binance_liquidity_ranks(klines, top_n=1, window_days=30)
    assert ranks["universe_label"].str.contains("exchange-liquidity").all()
    assert ranks["symbol"].iloc[-1] == "BTCUSDT"

    gap = market_cap_top100_gap_report(False)
    assert gap.loc[0, "status"] == "skipped"
    assert "current top100 backfill" in gap.loc[0, "reason"]
