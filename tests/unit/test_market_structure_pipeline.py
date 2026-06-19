from __future__ import annotations

from pathlib import Path

import pandas as pd

from cqresearch.analysis.market_structure_pipeline import (
    build_blended_fear_greed,
    build_outputs,
    normalize_cache_to_curated,
    sentiment_overlap_summary,
)
from cqresearch.analysis.market_universe import (
    MONTHLY_UNIVERSE_CURATED,
    normalize_defillama_monthly_universe,
)


def _seed_project(root: Path) -> None:
    (root / "Data" / "AlternativeMe").mkdir(parents=True)
    pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "fng_value": [40, 45],
            "fng_classification": ["Fear", "Neutral"],
        }
    ).to_csv(root / "Data" / "AlternativeMe" / "fear_greed_index__daily.csv", index=False)

    (root / "Data" / "DefiLlama" / "ChainMetrics").mkdir(parents=True)
    pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=40, freq="D"),
            "TVL": range(100, 140),
            "DEXs Volume": range(10, 50),
            "Stablecoins Mcap": range(200, 240),
        }
    ).to_csv(root / "Data" / "DefiLlama" / "ChainMetrics" / "all_dex_metrics__daily.csv", index=False)

    (root / "Data" / "DefiLlama" / "TVL" / "Daily").mkdir(parents=True)
    pd.DataFrame({"date": pd.date_range("2024-01-01", periods=40, freq="D"), "TVL": range(100, 140)}).to_csv(
        root / "Data" / "DefiLlama" / "TVL" / "Daily" / "tvl_all_chains_daily.csv",
        index=False,
    )

    (root / "Data" / "DefiLlama" / "CEX").mkdir(parents=True)
    pd.DataFrame({"date": pd.date_range("2024-01-01", periods=40, freq="D"), "binance-cex": range(40)}).to_csv(
        root / "Data" / "DefiLlama" / "CEX" / "cex_net_inflows_by_exchange__daily.csv",
        index=False,
    )

    (root / "Data" / "Tradingview" / "Daily").mkdir(parents=True)
    pd.DataFrame({"date": pd.date_range("2024-01-01", periods=40, freq="D"), "close": range(50, 90)}).to_csv(
        root / "Data" / "Tradingview" / "Daily" / "CRYPTOCAP_BTC_dominance__daily.csv",
        index=False,
    )

    (root / "Data").mkdir(exist_ok=True)
    pd.DataFrame(
        columns=[
            "source",
            "relpath",
            "topic",
            "start_date",
            "end_date",
            "row_count",
            "col_count",
            "frequency",
            "missing_days",
            "size_bytes",
            "sha256_12",
            "columns",
        ]
    ).to_csv(root / "Data" / "MASTER_DATA.csv", index=False)
    (root / "Data" / "MASTER_DATA.md").write_text("# Master Data Inventory\n", encoding="utf-8")


def test_market_structure_pipeline_runs_without_keys_or_cache(tmp_path) -> None:
    _seed_project(tmp_path)

    curated = normalize_cache_to_curated(tmp_path, cache_only=True)
    built = build_outputs(tmp_path)

    assert (tmp_path / "Data" / "MarketStructure" / "SourceRegistry" / "market_structure_source_registry.csv").exists()
    assert (tmp_path / "outputs" / "tables" / "T36_market_cap_top100_gap.csv").exists()
    assert (tmp_path / "outputs" / "figures" / "F30_market_structure_dashboard.png").exists()
    assert any("CMC Fear & Greed cache unavailable" in item for item in curated.skipped)
    assert any("Binance liquidity top100 skipped" in item for item in built.skipped)


def test_fear_greed_blend_uses_altme_before_cmc_start(tmp_path) -> None:
    (tmp_path / "Data" / "AlternativeMe").mkdir(parents=True)
    pd.DataFrame(
        {
            "date": ["2023-06-28", "2023-06-29", "2023-06-30"],
            "fng_value": [62, 54, 55],
            "fng_classification": ["Greed", "Neutral", "Neutral"],
        }
    ).to_csv(tmp_path / "Data" / "AlternativeMe" / "fear_greed_index__daily.csv", index=False)

    (tmp_path / "Data" / "MarketStructure" / "CoinMarketCap").mkdir(parents=True)
    pd.DataFrame(
        {
            "source": ["coinmarketcap", "coinmarketcap"],
            "date": ["2023-06-29", "2023-06-30"],
            "fng_value": [59, 58],
            "fng_classification": ["Neutral", "Neutral"],
        }
    ).to_csv(
        tmp_path / "Data" / "MarketStructure" / "CoinMarketCap" / "cmc_fear_greed__daily.csv",
        index=False,
    )

    blended = build_blended_fear_greed(tmp_path)
    summary = sentiment_overlap_summary(tmp_path).set_index("metric")["value"]

    assert blended["source"].tolist() == ["alternative_me", "coinmarketcap", "coinmarketcap"]
    assert blended["fng_value"].tolist() == [62, 59, 58]
    assert float(summary["splice_jump_alt_prev_day_to_cmc_start"]) == -3
    assert float(summary["same_day_cmc_minus_alt_on_splice_date"]) == 5
    assert summary["recommendation"] == "acceptable_with_source_flag"


def test_market_structure_outputs_include_monthly_universe_when_normalized(tmp_path) -> None:
    _seed_project(tmp_path)
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "asset_classification_overrides.yml").write_text(
        """
stablecoins: [USDT]
wrapped_assets: [WBTC]
lst_restaking: [STETH]
tokenized_commodities: [PAXG]
base_assets: [BTC, ETH, SOL]
""".strip()
        + "\n",
        encoding="utf-8",
    )
    raw = pd.DataFrame(
        [
            ["2024-01-31", "BTC", "Bitcoin", 1000, 1],
            ["2024-01-31", "ETH", "Ethereum", 900, 2],
            ["2024-01-31", "USDT", "Tether", 800, 3],
            ["2024-01-31", "WBTC", "Wrapped BTC", 700, 4],
            ["2024-01-31", "STETH", "Staked ETH", 600, 5],
            ["2024-01-31", "PAXG", "Pax Gold", 500, 6],
            ["2024-01-31", "DOGE", "Dogecoin", 400, 7],
            ["2024-01-31", "SOL", "Solana", 300, 8],
            ["2024-02-16", "BTC", "Bitcoin", 1100, 1],
            ["2024-02-16", "ETH", "Ethereum", 950, 2],
            ["2024-02-16", "USDT", "Tether", 850, 3],
            ["2024-02-16", "WBTC", "Wrapped BTC", 750, 4],
            ["2024-02-16", "STETH", "Staked ETH", 650, 5],
            ["2024-02-16", "PAXG", "Pax Gold", 550, 6],
            ["2024-02-16", "ADA", "Cardano", 450, 7],
            ["2024-02-16", "DOGE", "Dogecoin", 350, 8],
        ],
        columns=["date", "symbol", "name", "market_cap_usd", "rank"],
    )
    normalized = normalize_defillama_monthly_universe(
        raw,
        expected_snapshots=2,
        rows_per_snapshot=8,
        partial_month_date="2024-02-16",
    )
    out_path = tmp_path / MONTHLY_UNIVERSE_CURATED
    out_path.parent.mkdir(parents=True)
    normalized.to_csv(out_path, index=False)

    build_outputs(tmp_path)

    gap = pd.read_csv(tmp_path / "outputs" / "tables" / "T36_market_cap_top100_gap.csv")
    assert gap.loc[0, "status"] == "available"
    assert (tmp_path / "outputs" / "tables" / "T40_crypto_universe_monthly.csv").exists()
    assert (tmp_path / "outputs" / "tables" / "T45_market_evolution_summary.md").exists()
    assert (tmp_path / "outputs" / "figures" / "F38_market_structure_composition.png").exists()
