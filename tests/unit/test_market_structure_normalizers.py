from __future__ import annotations

import pandas as pd

from cqresearch.data.market_structure_normalizers import (
    normalize_alternative_me_fear_greed,
    normalize_binance_exchange_info,
    normalize_binance_klines,
    normalize_cmc_fear_greed,
    normalize_defillama_stablecoins,
)


def test_market_structure_normalizers_use_static_payloads() -> None:
    symbols = normalize_binance_exchange_info(
        {"symbols": [{"symbol": "BTCUSDT", "status": "TRADING", "baseAsset": "BTC", "quoteAsset": "USDT"}]}
    )
    assert symbols.loc[0, "base_asset"] == "BTC"

    klines = normalize_binance_klines(
        [[1_704_067_200_000, "1", "2", "0.5", "1.5", "10", 1_704_153_599_999, "15", 1, "5", "7", "0"]],
        "btcusdt",
    )
    assert klines.loc[0, "symbol"] == "BTCUSDT"
    assert float(klines.loc[0, "quote_asset_volume"]) == 15

    stable = normalize_defillama_stablecoins(
        {"peggedAssets": [{"id": 1, "name": "Tether", "symbol": "USDT", "circulating": {"peggedUSD": 100}}]}
    )
    assert stable.loc[0, "symbol"] == "USDT"

    cmc = normalize_cmc_fear_greed(
        {"data": [{"timestamp": "2024-09-02T12:00:00.000Z", "value": 50, "value_classification": "Neutral"}]}
    )
    assert cmc.loc[0, "source"] == "coinmarketcap"

    alt = normalize_alternative_me_fear_greed(
        pd.DataFrame({"date": ["2024-01-01"], "fng_value": [42], "fng_classification": ["Fear"]})
    )
    assert alt.loc[0, "source"] == "alternative_me"
