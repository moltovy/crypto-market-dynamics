from __future__ import annotations

import pandas as pd

from cqresearch.optional_data import (
    coin_market_chart_url,
    defillama_chains_url,
    defillama_protocol_tvl_url,
    fred_observations_url,
    klines_url,
    normalize_defillama_chains,
    normalize_defillama_protocol_tvl,
    normalize_fred_observations,
    normalize_klines,
    normalize_market_chart,
    optional_source_registry,
)


def test_optional_url_builders_are_deterministic() -> None:
    assert defillama_chains_url() == "https://api.llama.fi/v2/chains"
    assert defillama_protocol_tvl_url("aave") == "https://api.llama.fi/protocol/aave"
    assert "coins/bitcoin/market_chart" in coin_market_chart_url("bitcoin", days="365")
    assert "symbol=BTCUSDT" in klines_url("btcusdt")
    assert "series_id=DGS10" in fred_observations_url("DGS10", observation_start="2020-01-01")


def test_defillama_normalizers_use_static_payloads() -> None:
    chains = normalize_defillama_chains(
        [{"name": "Ethereum", "tvl": 10_000_000.0, "tokenSymbol": "ETH"}]
    )
    protocol = normalize_defillama_protocol_tvl(
        {
            "slug": "aave",
            "tvl": [{"date": 1_704_067_200, "totalLiquidityUSD": 123.45}],
        }
    )

    assert chains.loc[0, "chain"] == "Ethereum"
    assert float(chains.loc[0, "tvl_usd"]) == 10_000_000.0
    assert protocol.loc[0, "protocol"] == "aave"
    assert pd.notna(protocol.loc[0, "date"])


def test_coingecko_market_chart_normalizer_merges_series() -> None:
    ts = 1_704_067_200_000
    out = normalize_market_chart(
        {
            "prices": [[ts, 42_000.0]],
            "market_caps": [[ts, 820_000_000_000.0]],
            "total_volumes": [[ts, 20_000_000_000.0]],
        },
        "bitcoin",
    )

    assert out.loc[0, "coin_id"] == "bitcoin"
    assert float(out.loc[0, "price_usd"]) == 42_000.0
    assert float(out.loc[0, "volume_usd"]) == 20_000_000_000.0


def test_binance_klines_normalizer_types_ohlcv() -> None:
    out = normalize_klines(
        [
            [
                1_704_067_200_000,
                "1.0",
                "2.0",
                "0.5",
                "1.5",
                "100",
                1_704_153_599_999,
                "150",
                10,
                "50",
                "75",
                "0",
            ]
        ],
        "btcusdt",
    )

    assert out.loc[0, "symbol"] == "BTCUSDT"
    assert float(out.loc[0, "close"]) == 1.5
    assert "open_time" in out.columns


def test_fred_normalizer_handles_missing_value_marker() -> None:
    out = normalize_fred_observations(
        {"observations": [{"date": "2024-01-01", "value": "."}, {"date": "2024-01-02", "value": "4.5"}]},
        "DGS10",
    )

    assert out.loc[0, "series_id"] == "DGS10"
    assert pd.isna(out.loc[0, "value"])
    assert float(out.loc[1, "value"]) == 4.5


def test_optional_source_registry_documents_recommendations() -> None:
    registry = optional_source_registry()

    assert {"source", "value", "overlap", "auth_rate_limit", "maintenance", "recommendation"}.issubset(
        registry.columns
    )
    assert len(registry) == 4
