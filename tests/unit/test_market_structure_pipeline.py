from __future__ import annotations

from pathlib import Path

import pandas as pd

from cqresearch.analysis.market_structure_pipeline import build_outputs, normalize_cache_to_curated


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
