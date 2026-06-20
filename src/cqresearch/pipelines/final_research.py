"""Canonical offline pipeline for Crypto Market Dynamics.

This module is the maintained public build path. It uses local provider
data when available, writes semantic outputs, and keeps legacy release artifacts out of the
public surface.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib.image as mpimg
import numpy as np
import pandas as pd
import statsmodels.api as sm
import yaml
from config.paths import DATA_LOCAL_METADATA_DIR, DATA_LOCAL_PROCESSED_DIR, PROJECT_ROOT

from cqresearch.data.panel_builder import build_master_panel as build_source_master_panel
from cqresearch.data.panel_builder import write_panel as write_source_panel

TABLE_SCHEMA_COLUMNS = {
    "evidence_ledger": [
        "claim_id",
        "module",
        "claim_text",
        "outcome",
        "exposure_or_state",
        "sample",
        "frequency",
        "method",
        "source_tables",
        "source_figures",
        "estimate_summary",
        "uncertainty_summary",
        "robustness_checks",
        "mechanical_link_risk",
        "endogeneity_risk",
        "valuation_contamination_risk",
        "multiple_testing_status",
        "evidence_grade",
        "approved_public_language",
        "prohibited_language",
        "limitations",
        "status",
    ],
}

SELECTED_ASSETS: list[dict[str, Any]] = [
    {
        "asset_key": "coingecko:bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
        "coingecko_id": "bitcoin",
        "defillama_id": "bitcoin",
        "asset_type": "base_network_asset",
        "primary_chain": "Bitcoin",
        "first_valid_date": "2009-01-03",
        "selected_major": True,
        "stable_like": False,
        "wrapped_or_productized": False,
        "aliases": ["BTC", "XBT"],
    },
    {
        "asset_key": "coingecko:ethereum",
        "symbol": "ETH",
        "name": "Ethereum",
        "coingecko_id": "ethereum",
        "defillama_id": "ethereum",
        "asset_type": "base_network_asset",
        "primary_chain": "Ethereum",
        "first_valid_date": "2015-07-30",
        "selected_major": True,
        "stable_like": False,
        "wrapped_or_productized": False,
        "aliases": ["ETH"],
    },
    {
        "asset_key": "coingecko:binancecoin",
        "symbol": "BNB",
        "name": "BNB",
        "coingecko_id": "binancecoin",
        "defillama_id": "binancecoin",
        "asset_type": "exchange_chain_asset",
        "primary_chain": "BNB Chain",
        "first_valid_date": "2017-07-25",
        "selected_major": True,
        "stable_like": False,
        "wrapped_or_productized": False,
        "aliases": ["BNB"],
    },
    {
        "asset_key": "coingecko:solana",
        "symbol": "SOL",
        "name": "Solana",
        "coingecko_id": "solana",
        "defillama_id": "solana",
        "asset_type": "base_network_asset",
        "primary_chain": "Solana",
        "first_valid_date": "2020-04-10",
        "selected_major": True,
        "stable_like": False,
        "wrapped_or_productized": False,
        "aliases": ["SOL"],
    },
    {
        "asset_key": "coingecko:ripple",
        "symbol": "XRP",
        "name": "XRP",
        "coingecko_id": "ripple",
        "defillama_id": "ripple",
        "asset_type": "base_network_asset",
        "primary_chain": "XRPL",
        "first_valid_date": "2013-08-04",
        "selected_major": True,
        "stable_like": False,
        "wrapped_or_productized": False,
        "aliases": ["XRP"],
    },
    {
        "asset_key": "coingecko:dogecoin",
        "symbol": "DOGE",
        "name": "Dogecoin",
        "coingecko_id": "dogecoin",
        "defillama_id": "dogecoin",
        "asset_type": "base_network_asset",
        "primary_chain": "Dogecoin",
        "first_valid_date": "2013-12-06",
        "selected_major": True,
        "stable_like": False,
        "wrapped_or_productized": False,
        "aliases": ["DOGE"],
    },
    {
        "asset_key": "coingecko:tron",
        "symbol": "TRX",
        "name": "TRON",
        "coingecko_id": "tron",
        "defillama_id": "tron",
        "asset_type": "base_network_asset",
        "primary_chain": "Tron",
        "first_valid_date": "2017-09-13",
        "selected_major": True,
        "stable_like": False,
        "wrapped_or_productized": False,
        "aliases": ["TRX"],
    },
    {
        "asset_key": "coingecko:the-open-network",
        "symbol": "TON",
        "name": "Toncoin",
        "coingecko_id": "the-open-network",
        "defillama_id": "ton",
        "asset_type": "base_network_asset",
        "primary_chain": "TON",
        "first_valid_date": "2021-08-26",
        "selected_major": True,
        "stable_like": False,
        "wrapped_or_productized": False,
        "aliases": ["TON", "Toncoin"],
        "not_aliases": ["Tokamak Network"],
    },
    {
        "asset_key": "coingecko:cardano",
        "symbol": "ADA",
        "name": "Cardano",
        "coingecko_id": "cardano",
        "defillama_id": "cardano",
        "asset_type": "base_network_asset",
        "primary_chain": "Cardano",
        "first_valid_date": "2017-10-01",
        "selected_major": True,
        "stable_like": False,
        "wrapped_or_productized": False,
        "aliases": ["ADA"],
    },
    {
        "asset_key": "coingecko:hyperliquid",
        "symbol": "HYPE",
        "name": "Hyperliquid",
        "coingecko_id": "hyperliquid",
        "defillama_id": "hyperliquid",
        "asset_type": "base_network_asset",
        "primary_chain": "Hyperliquid",
        "first_valid_date": "2024-11-29",
        "selected_major": True,
        "stable_like": False,
        "wrapped_or_productized": False,
        "aliases": ["HYPE"],
    },
]

NESTED_TOL = 1e-10
BTC_ETF_START = pd.Timestamp("2024-01-11")
ETH_ETF_START = pd.Timestamp("2024-07-23")

CALENDAR_ASSUMPTIONS = {
    "crypto_calendar_daily": "BTC/ETH returns are seven-day crypto close-to-close returns.",
    "tradfi_business_daily": (
        "BTC/ETH returns are computed between consecutive common TradFi business-date "
        "closes; TradFi returns/changes use the same business dates."
    ),
    "tradfi_friday_weekly": "Weekly TradFi models use Friday-to-Friday BTC/ETH and TradFi moves.",
    "crypto_week_sunday": (
        "Crypto-native weekly state panel uses Sunday-ended crypto weeks; returns sum daily "
        "log returns and state variables use week-end or prior week-end values by semantic type."
    ),
    "etf_trading_daily": (
        "ETF-era daily panel uses dates with ETF flow observations; BTC/ETH returns run from "
        "the prior ETF trading date to the current ETF trading date."
    ),
}

CLOSE_TIME_ASSUMPTION = (
    "Local curated close timestamps are treated as provider daily closes; cross-market close-time "
    "mismatches are not intraday-adjusted."
)

CANONICAL_SELECTED_BY_KEY = {
    str(asset["asset_key"]).lower(): asset for asset in SELECTED_ASSETS
}
CANONICAL_SELECTED_BY_ID = {
    f"coingecko:{asset['coingecko_id']}".lower(): asset for asset in SELECTED_ASSETS
}
STABLE_ASSET_IDS = {
    "coingecko:tether",
    "coingecko:usd-coin",
    "coingecko:dai",
    "coingecko:binance-usd",
    "coingecko:first-digital-usd",
    "coingecko:true-usd",
    "coingecko:usde",
    "coingecko:usds",
    "coingecko:paypal-usd",
    "coingecko:paxos-standard",
    "coingecko:usdd",
    "coingecko:usdt0",
}
PRODUCTIZED_ASSET_IDS = {
    "coingecko:wrapped-bitcoin",
    "coingecko:weth",
    "coingecko:wrapped-sol",
    "coingecko:staked-ether",
    "coingecko:wrapped-steth",
    "coingecko:rocket-pool-eth",
    "coingecko:wrapped-eeth",
    "coingecko:wrapped-beacon-eth",
    "coingecko:coinbase-wrapped-staked-eth",
    "coingecko:coinbase-wrapped-btc",
    "coingecko:pax-gold",
    "coingecko:tether-gold",
    "coingecko:binance-peg-xrp",
    "coingecko:binance-peg-dogecoin",
}
GOVERNANCE_RISK_IDS = {
    "coingecko:lido-dao",
    "coingecko:rocket-pool",
    "coingecko:eigenlayer",
    "coingecko:ether-fi",
}

LOCAL_PROVIDER_DIRS = {
    "cryptoquant": "cryptoquant",
    "artemis": "artemis",
    "tradingview": "tradingview",
    "defillama": "defillama",
    "farside": "farside",
    "fred": "fred",
    "alternativeme": "alternativeme",
    "market_structure": "market_structure",
}
LEGACY_PROVIDER_DIRS = {
    "cryptoquant": "CryptoQuant",
    "artemis": "Artemis",
    "tradingview": "Tradingview",
    "defillama": "DefiLlama",
    "farside": "Farside ETF Data",
    "fred": "FRED",
    "alternativeme": "AlternativeMe",
    "market_structure": "MarketStructure",
}

PUBLIC_FIGURES = [
    (
        "mvrv_mechanics",
        "01_mvrv_mechanics.png",
        "How mechanically linked is MVRV to BTC returns?",
        "outputs/tables/mvrv_identity_points.csv; outputs/tables/mvrv_regime_outcomes.csv",
        "Same-day MVRV is a mechanics diagnostic; lagged state is used only as conditioning context.",
    ),
    (
        "tradfi_exposure_shift",
        "02_tradfi_exposure_shift.png",
        "How did equity co-movement change across periods?",
        "outputs/tables/block_delta_r2.csv",
        "Pre-specified pre-BTC-ETF versus BTC-ETF-era comparison; not an ETF-effect estimate.",
    ),
    (
        "etf_market_plumbing",
        "03_etf_market_plumbing.png",
        "How do ETF flow measures line up with same-day and lagged returns?",
        "outputs/tables/etf_absorption_metrics.csv; outputs/tables/etf_flow_associations.csv",
        "ETF flow intensity is market-plumbing association, not causal price impact.",
    ),
    (
        "leverage_tail_stress",
        "04_leverage_tail_stress.png",
        "Where do lagged leverage states and liquidation stress show up?",
        "outputs/tables/leverage_tail_risk_summary.csv; outputs/tables/liquidation_event_responses.csv",
        "Lagged leverage state is separated from same-day liquidation signatures.",
    ),
    (
        "point_in_time_market_structure",
        "05_point_in_time_market_structure.png",
        "How did PIT composition and concentration evolve?",
        "outputs/tables/pit_composition.csv; outputs/tables/pit_concentration.csv",
        "Monthly PIT data supports composition/turnover, not daily performance.",
    ),
    (
        "selected_major_asset_risk",
        "06_selected_major_asset_risk.png",
        "How do selected major assets differ in risk?",
        "outputs/tables/selected_major_risk_metrics.csv",
        "Coverage differs by asset; HYPE is short-history.",
    ),
]


@dataclass(frozen=True)
class BuildPaths:
    root: Path
    outputs: Path
    tables: Path
    figures: Path
    public_figures: Path
    gallery_figures: Path
    report: Path
    model_cards: Path
    panels: Path


def paths(root: Path = PROJECT_ROOT) -> BuildPaths:
    out = root / "outputs"
    local_processed = root / "data_local" / "processed"
    return BuildPaths(
        root=root,
        outputs=out,
        tables=out / "tables",
        figures=out / "figures",
        public_figures=out / "figures" / "public",
        gallery_figures=out / "figures" / "gallery",
        report=out / "report",
        model_cards=out / "model_cards",
        panels=local_processed if local_processed.exists() else DATA_LOCAL_PROCESSED_DIR,
    )


def raw_data_root(root: Path = PROJECT_ROOT) -> Path:
    local = root / "data_local" / "raw"
    return local if local.exists() else root / "Data"


def local_metadata_root(root: Path = PROJECT_ROOT) -> Path:
    local = root / "data_local" / "metadata"
    return local if local.exists() else DATA_LOCAL_METADATA_DIR


def provider_root(root: Path, provider: str) -> Path:
    key = provider.lower()
    if key not in LOCAL_PROVIDER_DIRS:
        raise KeyError(f"Unknown provider: {provider}")
    local = root / "data_local" / "raw" / LOCAL_PROVIDER_DIRS[key]
    return local if local.exists() else root / "Data" / LEGACY_PROVIDER_DIRS[key]


def ensure_output_dirs(p: BuildPaths) -> None:
    for directory in [
        p.outputs,
        p.tables,
        p.figures,
        p.public_figures,
        p.gallery_figures,
        p.report,
        p.model_cards,
        p.panels,
        p.root / "data_local" / "raw",
        p.root / "data_local" / "interim",
        p.root / "data_local" / "processed",
        p.root / "data_local" / "curated",
        p.root / "data_local" / "metadata",
        p.root / "config",
        p.root / "docs" / "architecture",
        p.root / "docs" / "data",
        p.root / "docs" / "decisions",
        p.root / "docs" / "methodology",
    ]:
        directory.mkdir(parents=True, exist_ok=True)


def clean_legacy_outputs(p: BuildPaths) -> None:
    """Remove legacy public-output clutter before generating canonical outputs."""

    ensure_output_dirs(p)
    for pattern in ["F*.png", "F*.svg", "T*.png", "T*.svg"]:
        for item in p.figures.glob(pattern):
            if item.is_file():
                item.unlink()
    for name in [
        "current_contact_sheet.png",
        "triage_before_contact_sheet.png",
        "visual_gallery.png",
    ]:
        item = p.figures / name
        if item.exists():
            item.unlink()
    for item in p.gallery_figures.glob("*"):
        if item.is_file():
            item.unlink()
    dashboard = p.outputs / "dashboard"
    if dashboard.exists():
        shutil.rmtree(dashboard)
    for item in p.tables.glob("T*"):
        if item.is_file():
            item.unlink()
    for name in ["bootstrap_robustness.csv"]:
        item = p.tables / name
        if item.exists():
            item.unlink()
    for name in ["key_results.html", "key_results.md", "README.md"]:
        item = p.tables / name
        if item.exists():
            item.unlink()
    allowed_reports = {
        "executive_summary.md",
        "limitations.md",
        "market_structure_public_surface_check.md",
        "methodology.md",
        "provider_data_disposition.md",
        "reproducibility_report.md",
        "results_and_interpretation.md",
        "visual_quality_audit.md",
    }
    for item in p.report.glob("*.md"):
        if item.name not in allowed_reports:
            item.unlink()
    for item in p.report.glob("visual_*.md"):
        item.unlink()
    for item in p.model_cards.glob("*.md"):
        item.unlink()


def utc_stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def write_csv(path: Path, frame: pd.DataFrame) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    return path


def write_md(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def read_date_csv(path: Path, date_col: str = "date") -> pd.DataFrame:
    frame = pd.read_csv(path)
    if date_col in frame.columns:
        frame[date_col] = pd.to_datetime(frame[date_col], errors="coerce")
        frame = frame.dropna(subset=[date_col]).sort_values(date_col)
        frame = frame.set_index(date_col)
        frame.index.name = "date"
    for column in frame.columns:
        if column != date_col:
            converted = pd.to_numeric(frame[column], errors="coerce")
            if converted.notna().sum() > 0:
                frame[column] = converted
    return frame


def numeric_series(path: Path, column: str, output: str) -> pd.Series:
    if not path.exists():
        return pd.Series(dtype=float, name=output)
    frame = read_date_csv(path)
    if column not in frame.columns:
        numeric_cols = frame.select_dtypes("number").columns
        if len(numeric_cols) == 0:
            return pd.Series(dtype=float, name=output)
        column = str(numeric_cols[0])
    series = pd.to_numeric(frame[column], errors="coerce").rename(output)
    return series.sort_index()


def log_return(series: pd.Series) -> pd.Series:
    clean = pd.to_numeric(series, errors="coerce")
    clean = clean.where(clean > 0)
    return np.log(clean).diff()


def safe_log(series: pd.Series) -> pd.Series:
    clean = pd.to_numeric(series, errors="coerce")
    return np.log(clean.where(clean > 0))


def pct_change(series: pd.Series) -> pd.Series:
    clean = pd.to_numeric(series, errors="coerce")
    clean = clean.where(clean > 0)
    return clean.pct_change()


def rolling_z(series: pd.Series, window: int = 90) -> pd.Series:
    mean = series.rolling(window, min_periods=max(20, window // 3)).mean()
    std = series.rolling(window, min_periods=max(20, window // 3)).std()
    return (series - mean) / std.replace(0, np.nan)


def expanding_percentile(series: pd.Series) -> pd.Series:
    values = series.shift(1)

    def pct(window: pd.Series) -> float:
        current = window.iloc[-1]
        prior = window.iloc[:-1].dropna()
        if pd.isna(current) or prior.empty:
            return np.nan
        return float((prior <= current).mean())

    return values.expanding(min_periods=30).apply(pct, raw=False)


def clean_label(value: str) -> str:
    labels = {
        "qqq_ret": "QQQ return",
        "spy_ret": "SPY return",
        "iwm_ret": "IWM return",
        "vix_d1": "VIX change",
        "dxy_ret": "DXY return",
        "real_yield_d1": "Real-yield change",
        "nominal_10y_d1": "10Y yield change",
        "gold_ret": "Gold return",
        "btc_etf_flow_intensity": "BTC ETF flow / lag mcap",
        "btc_etf_flow_intensity_lag0": "BTC ETF flow / lag mcap, t",
        "btc_etf_flow_intensity_lag1": "BTC ETF flow / lag mcap, t-1",
        "eth_etf_flow_intensity": "ETH ETF flow / lag mcap",
        "eth_etf_flow_intensity_lag0": "ETH ETF flow / lag mcap, t",
        "eth_etf_flow_intensity_lag1": "ETH ETF flow / lag mcap, t-1",
        "stablecoin_supply_growth": "Stablecoin supply growth",
        "stablecoin_supply_growth_lag1": "Stablecoin supply growth, t-1",
        "defi_tvl_growth": "Raw USD DeFi TVL growth",
        "defi_tvl_growth_lag1": "Raw USD DeFi TVL growth, t-1",
        "valuation_sensitive_defi_tvl_growth": "Valuation-sensitive DeFi TVL growth",
        "valuation_sensitive_defi_tvl_growth_lag1": "Valuation-sensitive DeFi TVL growth, t-1",
        "btc_oi_growth": "BTC OI growth",
        "btc_oi_growth_lag1": "BTC OI growth, t-1",
        "btc_oi_to_mcap": "BTC OI / market cap",
        "btc_oi_to_mcap_growth_lag1": "BTC OI/market-cap growth, t-1",
        "eth_oi_to_mcap": "ETH OI / market cap",
        "eth_oi_to_mcap_growth_lag1": "ETH OI/market-cap growth, t-1",
        "btc_funding_z": "BTC funding z-score",
        "btc_funding_z_lag1": "BTC funding z-score, t-1",
        "eth_oi_growth_lag1": "ETH OI growth, t-1",
        "eth_funding_z_lag1": "ETH funding z-score, t-1",
        "btc_exchange_netflow_scaled": "BTC exchange netflow / lag mcap",
        "btc_exchange_netflow_scaled_lag1": "BTC exchange netflow / lag mcap, t-1",
        "fear_greed_altme_lag1": "Fear & Greed state, t-1",
        "fear_greed_change_lag1": "Fear & Greed change, t-1",
        "btc_total_liq_to_lag_oi_pct": "BTC liquidation / lag OI (%)",
        "btc_total_liq_to_lag_mcap_bps": "BTC liquidation / lag mcap (bp)",
        "eth_total_liq_to_lag_oi_pct": "ETH liquidation / lag OI (%)",
        "eth_total_liq_to_lag_mcap_bps": "ETH liquidation / lag mcap (bp)",
    }
    return labels.get(value, value.replace("_", " ").title())


def source_file_inventory(root: Path = PROJECT_ROOT) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    columns = ["relpath", "source_group", "size_bytes", "suffix", "rows", "columns", "start_date", "end_date", "status"]
    raw_root = raw_data_root(root)
    if not raw_root.exists():
        return pd.DataFrame(columns=columns)
    for path in sorted(raw_root.rglob("*")):
        if not path.is_file():
            continue
        data_rel = path.relative_to(raw_root).as_posix()
        if data_rel in {"MASTER_DATA.csv", "MASTER_DATA.md", "MASTER_DATA.txt"}:
            continue
        source_group_raw = path.relative_to(raw_root).parts[0]
        source_group = LEGACY_PROVIDER_DIRS.get(source_group_raw.lower(), source_group_raw)
        rel = path.relative_to(root).as_posix()
        row: dict[str, Any] = {
            "relpath": rel,
            "source_group": source_group,
            "size_bytes": path.stat().st_size,
            "suffix": path.suffix.lower(),
            "rows": "",
            "columns": "",
            "start_date": "",
            "end_date": "",
            "status": "indexed",
        }
        if path.suffix.lower() == ".csv":
            try:
                frame = pd.read_csv(path, low_memory=False)
                row["rows"] = int(len(frame))
                row["columns"] = int(len(frame.columns))
                date_columns = [c for c in frame.columns if str(c).lower() in {"date", "snapshot_date", "month"}]
                if date_columns:
                    dates = pd.to_datetime(frame[date_columns[0]], errors="coerce").dropna()
                    if not dates.empty:
                        row["start_date"] = dates.min().date().isoformat()
                        row["end_date"] = dates.max().date().isoformat()
            except Exception as exc:
                row["status"] = f"read_error:{type(exc).__name__}"
        rows.append(row)
    return pd.DataFrame(rows, columns=columns)


def build_data_inventory(root: Path = PROJECT_ROOT) -> pd.DataFrame:
    p = paths(root)
    ensure_output_dirs(p)
    inventory = source_file_inventory(root)
    metadata_dir = local_metadata_root(root)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    write_csv(metadata_dir / "MASTER_DATA.csv", inventory)
    lines = [
        "# MASTER DATA Inventory",
        "",
        "Generated by: scripts/run_all.py",
        "",
        "This inventory is generated from files currently present under `data_local/raw/`.",
        "",
        inventory.groupby("source_group").size().rename("file_count").reset_index().to_markdown(index=False),
        "",
    ]
    write_md(metadata_dir / "MASTER_DATA.md", "\n".join(lines))
    write_md(metadata_dir / "MASTER_DATA.txt", "\n".join(lines))

    coverage_rows = []
    for group, sub in inventory.groupby("source_group"):
        starts = pd.to_datetime(sub["start_date"], errors="coerce").dropna()
        ends = pd.to_datetime(sub["end_date"], errors="coerce").dropna()
        coverage_rows.append(
            {
                "source_group": group,
                "file_count": int(len(sub)),
                "csv_count": int((sub["suffix"] == ".csv").sum()),
                "total_bytes": int(sub["size_bytes"].sum()),
                "first_date": starts.min().date().isoformat() if not starts.empty else "",
                "last_date": ends.max().date().isoformat() if not ends.empty else "",
                "license_note": license_note(group),
            }
        )
    coverage = pd.DataFrame(coverage_rows).sort_values("source_group")
    write_csv(p.tables / "data_source_coverage.csv", coverage)
    disposition = provider_data_disposition(coverage)
    write_csv(p.tables / "provider_data_disposition.csv", disposition)
    write_md(
        p.report / "provider_data_disposition.md",
        "# Provider Data Disposition\n\n"
        "This report does not resolve redistribution rights. It classifies the current provider groups for public-release handling and flags where derived-only publication is recommended.\n\n"
        + disposition.to_markdown(index=False),
    )
    return coverage


def provider_data_disposition(coverage: pd.DataFrame) -> pd.DataFrame:
    rules = {
        "FRED": ("public/re-distributable", "Public Federal Reserve Economic Data series; cite source."),
        "CryptoQuant": ("uncertain/restricted", "Provider export; do not newly redistribute raw files without explicit permission."),
        "Artemis": ("uncertain/restricted", "Provider/export data; do not newly redistribute raw files without explicit permission."),
        "Tradingview": ("uncertain/restricted", "Chart/export data; redistribution rights may be restricted."),
        "DefiLlama": ("derived-only recommended", "Public API/web source; publish derived outputs and verify terms before raw redistribution."),
        "Farside ETF Data": ("derived-only recommended", "Public web source; publish derived outputs and verify reuse terms."),
        "AlternativeMe": ("derived-only recommended", "Public Fear and Greed source; publish derived outputs with attribution."),
        "MarketStructure": ("derived-only recommended", "Curated local data assembled from public/optional sources; prefer derived summaries."),
    }
    rows = []
    for _, row in coverage.iterrows():
        source = str(row["source_group"])
        disposition, note = rules.get(source, ("derived-only recommended", "Repository-local or mixed-source data; verify provenance before raw redistribution."))
        rows.append(
            {
                "source_group": source,
                "disposition": disposition,
                "file_count": int(row["file_count"]),
                "first_date": row["first_date"],
                "last_date": row["last_date"],
                "release_recommendation": note,
            }
        )
    return pd.DataFrame(rows)


def license_note(source_group: str) -> str:
    notes = {
        "CryptoQuant": "Provider export; redistribution rights may be restricted.",
        "Artemis": "Provider/export data; redistribution rights may be restricted.",
        "DefiLlama": "Public API and curated files; cite DefiLlama and respect terms.",
        "FRED": "Federal Reserve Economic Data; generally public source with attribution.",
        "Farside ETF Data": "Public web data; cite Farside Investors and verify reuse terms.",
        "Tradingview": "Chart/export data; redistribution rights may be restricted.",
        "AlternativeMe": "Public Fear and Greed index data; cite provider.",
        "MarketStructure": "Curated local summaries from public/optional sources.",
    }
    return notes.get(source_group, "Repository-local metadata or generated inventory.")


def write_config_files(root: Path = PROJECT_ROOT) -> None:
    config = root / "config"
    config.mkdir(parents=True, exist_ok=True)
    assets_doc = {"assets": SELECTED_ASSETS}
    (config / "assets.yml").write_text(yaml.safe_dump(assets_doc, sort_keys=False), encoding="utf-8")

    public_rows = []
    for fig_id, filename, question, sources, caveat in PUBLIC_FIGURES:
        public_rows.append(
            {
                "figure_id": fig_id,
                "filename": f"outputs/figures/public/{filename}",
                "status": "public",
                "research_question": question,
                "source_tables": sources,
                "chart_type": "generated",
                "units": "see axes",
                "caption": question,
                "caveat": caveat,
                "width_px": 1800,
                "height_px": 1200,
                "svg_required": True,
                "readme_section": fig_id,
                "visual_qa_status": "manual_pass_after_contact_sheet_review",
            }
        )
    (config / "public_figures.yml").write_text(
        yaml.safe_dump({"figures": public_rows}, sort_keys=False),
        encoding="utf-8",
    )

    features = feature_registry_rows()
    (config / "feature_registry.yml").write_text(
        yaml.safe_dump({"features": features}, sort_keys=False),
        encoding="utf-8",
    )
    taxonomy = {
        "stable_like": [
            "USDT",
            "USDC",
            "DAI",
            "FDUSD",
            "BUSD",
            "TUSD",
            "USDE",
            "USDS",
            "PYUSD",
            "USDP",
            "USDD",
            "USDT0",
            "USDC.E",
        ],
        "productized_wrapped": [
            "WBTC",
            "WETH",
            "CBBTC",
            "STETH",
            "WSTETH",
            "RETH",
            "WEETH",
            "WBETH",
            "CBETH",
            "PAXG",
            "XAUT",
        ],
        "governance_or_infrastructure_risk": ["LDO", "RPL", "EIGEN", "ETHFI"],
        "selected_majors_ex_btc_eth": ["BNB", "SOL", "XRP", "DOGE", "TRX", "TON", "ADA", "HYPE"],
    }
    (config / "asset_taxonomy.yml").write_text(yaml.safe_dump(taxonomy, sort_keys=False), encoding="utf-8")


def feature_registry_rows() -> list[dict[str, Any]]:
    rows = []
    registry = [
        ("btc_ret", "BTC log return", "target", "CryptoQuant", "BTC price close", "daily", "log return", 0, "", "Return outcome."),
        ("eth_ret", "ETH log return", "target", "CryptoQuant", "ETH price close", "daily", "log return", 0, "", "Return outcome."),
        ("btc_realized_vol_30d", "BTC 30-day realized volatility", "target", "CryptoQuant", "BTC close", "daily", "rolling volatility", 0, "", "Volatility outcome."),
        ("qqq_ret", "QQQ return", "macro_risk", "TradingView", "QQQ close", "daily", "business-date log return", 0, "", "Contemporaneous equity-growth exposure proxy."),
        ("spy_ret", "SPY return", "macro_risk", "TradingView", "SPY close", "daily", "business-date log return", 0, "", "Contemporaneous US equity-market exposure proxy."),
        ("iwm_ret", "IWM return", "macro_risk", "TradingView", "IWM close", "daily", "business-date log return", 0, "", "Contemporaneous small-cap equity exposure proxy where supported."),
        ("vix_d1", "VIX change", "macro_risk", "FRED", "VIXCLS", "daily", "business-date first difference", 0, "", "Contemporaneous equity-volatility exposure proxy."),
        ("dxy_ret", "DXY return", "macro_risk", "TradingView", "DXY close", "daily", "business-date log return", 0, "", "Contemporaneous dollar index exposure proxy."),
        ("real_yield_d1", "Real-yield change", "macro_risk", "FRED", "DFII10", "daily", "business-date first difference", 0, "", "Contemporaneous real-rate exposure proxy."),
        ("nominal_10y_d1", "Nominal 10Y yield change", "macro_risk", "FRED", "DGS10", "daily", "business-date first difference", 0, "", "Contemporaneous nominal-rate exposure proxy."),
        ("gold_ret", "Gold return", "macro_risk", "TradingView/FRED", "GLD or XAUUSD close", "daily", "business-date log return", 0, "", "Contemporaneous gold exposure proxy."),
        ("btc_etf_flow_intensity_lag0", "BTC ETF flow intensity, t", "etf_institutional", "Farside", "BTC ETF total", "daily", "flow / lagged market cap", 0, "prior-day BTC market cap", "Market-plumbing flow proxy."),
        ("btc_etf_flow_intensity_lag1", "BTC ETF flow intensity, t-1", "etf_institutional", "Farside", "BTC ETF total", "daily", "flow / lagged market cap then lag one day", 1, "prior-day BTC market cap", "Lagged market-plumbing flow proxy."),
        ("eth_etf_flow_intensity_lag0", "ETH ETF flow intensity, t", "etf_institutional", "Farside", "ETH ETF total", "daily", "flow / lagged market cap", 0, "prior-day ETH market cap", "Market-plumbing flow proxy."),
        ("eth_etf_flow_intensity_lag1", "ETH ETF flow intensity, t-1", "etf_institutional", "Farside", "ETH ETF total", "daily", "flow / lagged market cap then lag one day", 1, "prior-day ETH market cap", "Lagged market-plumbing flow proxy."),
        ("btc_oi_growth_lag1", "BTC raw open-interest growth, t-1", "leverage", "CryptoQuant", "BTC open interest", "daily", "log difference lagged one day", 1, "", "Raw leverage-state proxy; retained for audit, not preferred if OI is USD-valued."),
        ("btc_oi_to_mcap_growth_lag1", "BTC OI/market-cap growth, t-1", "leverage", "CryptoQuant", "BTC open interest and market cap", "daily", "log difference of OI/market-cap ratio lagged one panel step", 1, "BTC market cap", "Preferred lagged leverage-state proxy when OI is USD/notional-valued."),
        ("eth_oi_to_mcap_growth_lag1", "ETH OI/market-cap growth, t-1", "leverage", "CryptoQuant", "ETH open interest and market cap", "daily", "log difference of OI/market-cap ratio lagged one panel step", 1, "ETH market cap", "Preferred lagged leverage-state proxy when OI is USD/notional-valued."),
        ("btc_funding_z_lag1", "BTC funding z-score, t-1", "leverage", "CryptoQuant", "BTC funding rates", "daily", "rolling z-score lagged one day", 1, "", "Positioning stress proxy."),
        ("btc_total_liq_to_lag_oi_pct", "BTC liquidation / lagged OI", "leverage", "CryptoQuant", "BTC liquidations USD", "daily", "liquidation USD / prior-day open interest, percent", 0, "prior-day open interest", "Same-day liquidation stress signature."),
        ("btc_total_liq_to_lag_mcap_bps", "BTC liquidation / lagged market cap", "leverage", "CryptoQuant", "BTC liquidations USD", "daily", "liquidation USD / prior-day market cap, basis points", 0, "prior-day BTC market cap", "Same-day liquidation stress signature."),
        ("stablecoin_supply_growth", "Stablecoin supply growth", "liquidity", "DefiLlama", "stablecoin market caps", "weekly", "log difference", 1, "", "Liquidity-state proxy."),
        ("stablecoin_supply_growth_lag1", "Lagged stablecoin supply growth", "liquidity", "DefiLlama", "stablecoin market caps", "weekly", "weekly log difference lagged one week", 1, "", "Lagged liquidity-state proxy."),
        ("valuation_sensitive_defi_tvl_growth", "Valuation-sensitive DeFi TVL growth", "liquidity", "DefiLlama", "USD TVL", "weekly", "log difference of USD TVL", 0, "", "Valuation-sensitive DeFi balance-sheet proxy, not pure capital inflow."),
        ("valuation_sensitive_defi_tvl_growth_lag1", "Lagged valuation-sensitive DeFi TVL growth", "liquidity", "DefiLlama", "USD TVL", "weekly", "weekly log difference lagged one week", 1, "", "Lagged valuation-sensitive DeFi balance-sheet proxy, not pure capital inflow."),
        ("btc_mvrv_lag1", "Lagged BTC MVRV", "onchain_state", "CryptoQuant", "MVRV Ratio", "daily", "lagged level/percentile", 1, "", "Valuation-state conditioning variable."),
        ("d_log_mvrv", "BTC d-log MVRV", "onchain_state", "CryptoQuant", "MVRV Ratio", "daily", "same-interval log difference", 0, "", "Measurement-mechanics diagnostic only."),
        ("d_log_market_cap", "BTC d-log market cap", "onchain_state", "CryptoQuant", "BTC market cap", "daily", "same-interval log difference", 0, "", "MVRV identity component."),
        ("d_log_realized_cap", "BTC d-log realized cap", "onchain_state", "CryptoQuant", "BTC realized cap", "daily", "same-interval log difference", 0, "", "MVRV identity component."),
        ("identity_residual", "MVRV identity residual", "onchain_state", "CryptoQuant", "MVRV and realized cap", "daily", "d_log_mvrv - (d_log_market_cap - d_log_realized_cap)", 0, "", "Source-convention residual diagnostic."),
        ("pit_hhi", "PIT top-100 HHI", "market_structure", "DefiLlama", "monthly top-200 universe", "monthly", "market-cap concentration", 0, "", "Composition outcome."),
    ]
    for feature_id, label, block, source, raw_field, frequency, transform, lag, denom, interp in registry:
        rows.append(
            {
                "feature_id": feature_id,
                "clean_label": label,
                "research_block": block,
                "raw_source": source,
                "raw_path_or_endpoint": "tracked local repository file",
                "raw_field": raw_field,
                "frequency": frequency,
                "transformation": transform,
                "lag_days": lag,
                "scaling_denominator": denom,
                "first_valid_date": "",
                "last_valid_date": "",
                "missing_policy": "drop from model sample; report effective n",
                "mechanical_link_risk": (
                    "direct_target_component"
                    if feature_id == "btc_mvrv_d1"
                    else "high"
                    if "mvrv" in feature_id
                    else "medium"
                    if "tvl" in feature_id or "oi_growth" in feature_id
                    else "low"
                ),
                "valuation_contamination_risk": (
                    "high_usd_price_content"
                    if "valuation_sensitive_defi_tvl" in feature_id
                    else "medium_if_usd_notional"
                    if "oi" in feature_id
                    else "none_identified"
                ),
                "contemporaneous_endogeneity_risk": "medium" if "etf" in feature_id or "liq" in feature_id else "low",
                "permitted_model_families": "descriptive, exposure, state conditioning",
                "prohibited_uses": "price forecasting; causal claims; same-day MVRV as primary BTC-return factor",
                "interpretation": interp,
            }
        )
    return rows


def load_master_panel(root: Path = PROJECT_ROOT) -> pd.DataFrame:
    panel_path = paths(root).panels / "master_daily.parquet"
    if not panel_path.exists():
        panel, report = build_source_master_panel()
        write_source_panel(panel, report, panel_path.parent)
    panel = pd.read_parquet(panel_path)
    panel.index = pd.to_datetime(panel.index)
    panel.index.name = "date"
    return panel.sort_index()


def add_extra_series(panel: pd.DataFrame, root: Path = PROJECT_ROOT) -> pd.DataFrame:
    data = panel.copy()
    cq = provider_root(root, "cryptoquant")
    tradingview = provider_root(root, "tradingview")
    extra = {
        "btc_realized_cap": numeric_series(cq / "BTC/Market Data/Bitcoin Realized Cap - Day.csv", "Realized Cap", "btc_realized_cap"),
        "btc_realized_price": numeric_series(cq / "BTC/Market Indicator/Bitcoin Realized Price - Day.csv", "Realized Price", "btc_realized_price"),
        "btc_nupl": numeric_series(cq / "BTC/Market Indicator/Bitcoin Net Unrealized Profit_Loss (NUPL) - Day.csv", "Net Unrealized Profit/Loss (NUPL)", "btc_nupl"),
        "btc_sopr": numeric_series(cq / "BTC/Market Indicator/Bitcoin Spent Output Profit Ratio (SOPR) - Day.csv", "Spent Output Profit Ratio (SOPR)", "btc_sopr"),
        "btc_asopr": numeric_series(cq / "BTC/Market Indicator/Bitcoin Adjusted SOPR (aSOPR) - Day.csv", "Adjusted SOPR (aSOPR)", "btc_asopr"),
        "btc_supply_profit_pct": numeric_series(cq / "BTC/Market Indicator/Bitcoin Supply in Profit (%) - Day.csv", "Supply in Profit (%)", "btc_supply_profit_pct"),
        "btc_oi": numeric_series(cq / "BTC/Derivatives/Bitcoin Open Interest - All Exchanges, All Symbol - Day.csv", "Open Interest", "btc_oi"),
        "btc_funding": numeric_series(cq / "BTC/Derivatives/Bitcoin Funding Rates - All Exchanges - Day.csv", "Funding Rates", "btc_funding"),
        "btc_leverage_ratio": numeric_series(cq / "BTC/Derivatives/Bitcoin Estimated Leverage Ratio - All Exchanges - Day.csv", "Estimated Leverage Ratio", "btc_leverage_ratio"),
        "btc_long_liq_usd": numeric_series(cq / "BTC/Derivatives/Bitcoin Long Liquidations USD - All Exchanges, All Symbol - Day.csv", "Long Liquidations USD", "btc_long_liq_usd"),
        "btc_short_liq_usd": numeric_series(cq / "BTC/Derivatives/Bitcoin Short Liquidations USD - All Exchanges, All Symbol - Day.csv", "Short Liquidations USD", "btc_short_liq_usd"),
        "btc_taker_buy_ratio": numeric_series(cq / "BTC/Market Data/Bitcoin Taker Buy Ratio - All Exchanges - Day.csv", "Taker Buy Ratio", "btc_taker_buy_ratio"),
        "btc_taker_buy_sell_ratio": numeric_series(cq / "BTC/Market Data/Bitcoin Taker Buy Sell Ratio - All Exchanges - Day.csv", "Taker Buy Sell Ratio", "btc_taker_buy_sell_ratio"),
        "eth_oi": numeric_series(cq / "ETH/Derivatives/Ethereum Open Interest - All Exchanges, All Symbol - Day.csv", "Open Interest", "eth_oi"),
        "eth_funding": numeric_series(cq / "ETH/Derivatives/Ethereum Funding Rates - All Exchanges - Day.csv", "Funding Rates", "eth_funding"),
        "eth_leverage_ratio": numeric_series(cq / "ETH/Derivatives/Ethereum Estimated Leverage Ratio - All Exchanges - Day.csv", "Estimated Leverage Ratio", "eth_leverage_ratio"),
        "eth_long_liq_usd": numeric_series(cq / "ETH/Derivatives/Ethereum Long Liquidations USD - All Exchanges, All Symbol - Day.csv", "Long Liquidations USD", "eth_long_liq_usd"),
        "eth_short_liq_usd": numeric_series(cq / "ETH/Derivatives/Ethereum Short Liquidations USD - All Exchanges, All Symbol - Day.csv", "Short Liquidations USD", "eth_short_liq_usd"),
        "btc_dominance": load_close(tradingview / "Daily/CRYPTOCAP_BTC_dominance__daily.csv", "btc_dominance"),
        "eth_dominance": load_close(tradingview / "Daily/CRYPTOCAP_ETH_dominance__daily.csv", "eth_dominance"),
        "total3_close": load_close(tradingview / "Daily/CRYPTOCAP_TOTAL3__daily.csv", "total3_close"),
        "iwm_close": load_close(tradingview / "Daily/IWM_russell2000_etf__daily.csv", "iwm_close"),
        "xauusd_close": load_close(tradingview / "Daily/XAUUSD_gold_spot__daily.csv", "xauusd_close"),
        "ibit_spot_ratio": load_close(tradingview / "Daily/IBIT_ETF_over_SPOT_BTC__daily.csv", "ibit_spot_ratio"),
        "etha_spot_ratio": load_close(tradingview / "Daily/ETHA_ETF_over_SPOT_ETH__daily.csv", "etha_spot_ratio"),
    }
    for name, series in extra.items():
        if not series.empty:
            data[name] = series.reindex(data.index)
    return data


def load_close(path: Path, output: str) -> pd.Series:
    if not path.exists():
        return pd.Series(dtype=float, name=output)
    frame = read_date_csv(path)
    column = "close" if "close" in frame.columns else "Close"
    if column not in frame.columns:
        numeric_cols = frame.select_dtypes("number").columns
        if len(numeric_cols) == 0:
            return pd.Series(dtype=float, name=output)
        column = str(numeric_cols[0])
    return pd.to_numeric(frame[column], errors="coerce").rename(output)


def build_feature_store(root: Path = PROJECT_ROOT) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    p = paths(root)
    ensure_output_dirs(p)
    panel = add_extra_series(load_master_panel(root), root)
    daily = pd.DataFrame(index=panel.index)
    daily["btc_close"] = panel["btc_close"]
    daily["eth_close"] = panel["eth_close"]
    daily["spy_close"] = panel.get("spy_close")
    daily["qqq_close"] = panel.get("qqq_close")
    daily["iwm_close"] = panel.get("iwm_close")
    gld_close = panel.get("gld_close", pd.Series(index=panel.index, dtype=float))
    xauusd_close = panel.get("xauusd_close", pd.Series(index=panel.index, dtype=float))
    daily["gold_close"] = gld_close.combine_first(xauusd_close)
    daily["dxy_close"] = panel.get("dxy_tv_close")
    daily["vix_level"] = panel.get("VIXCLS", pd.Series(index=panel.index, dtype=float))
    daily["real_yield_level"] = panel.get("DFII10", pd.Series(index=panel.index, dtype=float))
    daily["nominal_10y_level"] = panel.get("DGS10", pd.Series(index=panel.index, dtype=float))
    daily["btc_ret"] = log_return(panel["btc_close"])
    daily["eth_ret"] = log_return(panel["eth_close"])
    daily["spy_ret"] = log_return(daily["spy_close"])
    daily["qqq_ret"] = log_return(daily["qqq_close"])
    daily["iwm_ret"] = log_return(daily["iwm_close"])
    daily["gold_ret"] = log_return(daily["gold_close"])
    daily["dxy_ret"] = log_return(daily["dxy_close"])
    daily["total3_ret"] = log_return(panel.get("total3_close"))
    daily["vix_d1"] = panel.get("VIXCLS", pd.Series(index=panel.index, dtype=float)).diff()
    daily["real_yield_d1"] = panel.get("DFII10", pd.Series(index=panel.index, dtype=float)).diff()
    daily["nominal_10y_d1"] = panel.get("DGS10", pd.Series(index=panel.index, dtype=float)).diff()
    daily["term_spread_d1"] = panel.get("T10Y2Y", pd.Series(index=panel.index, dtype=float)).diff()
    daily["hy_oas_d1"] = panel.get("BAMLH0A0HYM2", pd.Series(index=panel.index, dtype=float)).diff()
    daily["oil_ret"] = log_return(panel.get("DCOILWTICO"))
    daily["policy_uncertainty_d1"] = panel.get("USEPUINDXD", pd.Series(index=panel.index, dtype=float)).diff()
    daily["btc_realized_vol_30d"] = daily["btc_ret"].rolling(30, min_periods=20).std() * math.sqrt(365)
    daily["eth_realized_vol_30d"] = daily["eth_ret"].rolling(30, min_periods=20).std() * math.sqrt(365)
    daily["btc_drawdown"] = panel["btc_close"] / panel["btc_close"].cummax() - 1
    daily["eth_drawdown"] = panel["eth_close"] / panel["eth_close"].cummax() - 1
    daily["btc_bottom5"] = (daily["btc_ret"] <= daily["btc_ret"].quantile(0.05)).astype(float)
    daily["eth_bottom5"] = (daily["eth_ret"] <= daily["eth_ret"].quantile(0.05)).astype(float)
    daily["btc_vol_spike"] = (daily["btc_realized_vol_30d"] >= daily["btc_realized_vol_30d"].quantile(0.90)).astype(float)
    daily["btc_market_cap_usd"] = panel["btc_mcap_usd"]
    daily["eth_market_cap_usd"] = panel["eth_mcap_usd"]
    daily["btc_mcap_lag1"] = daily["btc_market_cap_usd"].shift(1)
    daily["eth_mcap_lag1"] = daily["eth_market_cap_usd"].shift(1)
    daily["btc_etf_net_flow_usd"] = panel.get("btc_etf_total", pd.Series(index=panel.index, dtype=float)) * 1e6
    daily["eth_etf_net_flow_usd"] = panel.get("eth_etf_total", pd.Series(index=panel.index, dtype=float)) * 1e6
    daily["btc_etf_flow_intensity_lag0"] = daily["btc_etf_net_flow_usd"] / daily["btc_mcap_lag1"]
    daily["eth_etf_flow_intensity_lag0"] = daily["eth_etf_net_flow_usd"] / daily["eth_mcap_lag1"]
    daily["btc_etf_flow_intensity_lag1"] = daily["btc_etf_flow_intensity_lag0"].shift(1)
    daily["eth_etf_flow_intensity_lag1"] = daily["eth_etf_flow_intensity_lag0"].shift(1)
    daily["btc_etf_flow_intensity"] = daily["btc_etf_flow_intensity_lag0"]
    daily["eth_etf_flow_intensity"] = daily["eth_etf_flow_intensity_lag0"]
    daily["btc_etf_cumulative_flow_usd"] = daily["btc_etf_net_flow_usd"].fillna(0).cumsum()
    daily["eth_etf_cumulative_flow_usd"] = daily["eth_etf_net_flow_usd"].fillna(0).cumsum()
    daily["btc_mvrv"] = panel.get("btc_mvrv")
    daily["btc_mvrv_lag1"] = daily["btc_mvrv"].shift(1)
    daily["btc_mvrv_log"] = safe_log(daily["btc_mvrv"])
    daily["d_log_mvrv"] = daily["btc_mvrv_log"].diff()
    daily["btc_mvrv_d1"] = daily["d_log_mvrv"]
    daily["btc_mvrv_percentile_lagged"] = expanding_percentile(daily["btc_mvrv"])
    daily["btc_mvrv_z_365_lagged"] = rolling_z(daily["btc_mvrv"], 365).shift(1)
    daily["btc_realized_cap"] = panel.get("btc_realized_cap")
    daily["btc_realized_cap_usd"] = daily["btc_realized_cap"]
    daily["d_log_market_cap"] = log_return(daily["btc_market_cap_usd"])
    daily["d_log_realized_cap"] = log_return(daily["btc_realized_cap_usd"])
    daily["identity_residual"] = daily["d_log_mvrv"] - (daily["d_log_market_cap"] - daily["d_log_realized_cap"])
    daily["btc_realized_price"] = panel.get("btc_realized_price")
    daily["btc_realized_price_gap_lag1"] = (panel["btc_close"] / panel.get("btc_realized_price")).shift(1)
    daily["btc_nupl_lag1"] = panel.get("btc_nupl", pd.Series(index=panel.index, dtype=float)).shift(1)
    daily["btc_sopr_lag1"] = panel.get("btc_sopr", pd.Series(index=panel.index, dtype=float)).shift(1)
    daily["btc_supply_profit_pct_lag1"] = panel.get("btc_supply_profit_pct", pd.Series(index=panel.index, dtype=float)).shift(1)
    daily["stablecoin_supply_usd"] = panel.get("stables_total_usd")
    daily["defi_tvl_usd"] = panel.get("defi_tvl_usd")
    daily["stablecoin_supply_growth"] = log_return(panel.get("stables_total_usd"))
    daily["defi_tvl_growth"] = log_return(panel.get("defi_tvl_usd"))
    daily["valuation_sensitive_defi_tvl_growth"] = daily["defi_tvl_growth"]
    daily["stablecoin_supply_growth_lag1"] = daily["stablecoin_supply_growth"].shift(1)
    daily["defi_tvl_growth_lag1"] = daily["defi_tvl_growth"].shift(1)
    daily["valuation_sensitive_defi_tvl_growth_lag1"] = daily["valuation_sensitive_defi_tvl_growth"].shift(1)
    daily["stablecoin_to_tvl"] = panel.get("stables_total_usd") / panel.get("defi_tvl_usd")
    daily["stablecoin_share_crypto_proxy"] = panel.get("stables_total_usd") / (panel["btc_mcap_usd"] + panel["eth_mcap_usd"] + panel.get("total3_close"))
    daily["btc_oi"] = panel.get("btc_oi")
    daily["btc_oi_growth"] = log_return(panel.get("btc_oi"))
    daily["btc_oi_growth_lag1"] = daily["btc_oi_growth"].shift(1)
    daily["btc_oi_to_mcap"] = panel.get("btc_oi") / daily["btc_mcap_lag1"]
    daily["btc_oi_to_mcap_current"] = panel.get("btc_oi") / daily["btc_market_cap_usd"]
    daily["btc_oi_to_mcap_growth"] = log_return(daily["btc_oi_to_mcap_current"])
    daily["btc_oi_to_mcap_growth_lag1"] = daily["btc_oi_to_mcap_growth"].shift(1)
    daily["btc_oi_unit_assumption"] = "CryptoQuant all-exchange OI export treated as USD/notional-valued for scaling audit."
    daily["btc_funding"] = panel.get("btc_funding")
    daily["btc_abs_funding"] = daily["btc_funding"].abs()
    daily["btc_funding_z"] = rolling_z(daily["btc_funding"], 90)
    daily["btc_funding_z_lag1"] = daily["btc_funding_z"].shift(1)
    daily["btc_leverage_ratio_percentile"] = expanding_percentile(panel.get("btc_leverage_ratio", pd.Series(index=panel.index, dtype=float)))
    daily["btc_leverage_ratio_percentile_lag1"] = daily["btc_leverage_ratio_percentile"].shift(1)
    btc_long_liq = panel.get("btc_long_liq_usd", pd.Series(index=panel.index, dtype=float))
    btc_short_liq = panel.get("btc_short_liq_usd", pd.Series(index=panel.index, dtype=float))
    daily["btc_total_liq_usd"] = pd.concat([btc_long_liq, btc_short_liq], axis=1).sum(axis=1, min_count=1)
    btc_lag_oi = panel.get("btc_oi", pd.Series(index=panel.index, dtype=float)).shift(1)
    daily["btc_long_liq_to_lag_mcap_bps"] = btc_long_liq / daily["btc_mcap_lag1"] * 10000
    daily["btc_short_liq_to_lag_mcap_bps"] = btc_short_liq / daily["btc_mcap_lag1"] * 10000
    daily["btc_total_liq_to_lag_oi_pct"] = daily["btc_total_liq_usd"] / btc_lag_oi * 100
    daily["btc_total_liq_to_lag_mcap_bps"] = daily["btc_total_liq_usd"] / daily["btc_mcap_lag1"] * 10000
    daily["btc_total_liq_to_lag_oi_log1p"] = np.log1p(daily["btc_total_liq_usd"] / btc_lag_oi)
    daily["btc_total_liq_intensity"] = daily["btc_total_liq_to_lag_oi_pct"]
    daily["btc_basis_z"] = rolling_z(panel.get("cme_btc_basis_close", pd.Series(index=panel.index, dtype=float)), 90)
    daily["btc_taker_buy_ratio"] = panel.get("btc_taker_buy_ratio")
    daily["btc_exchange_netflow_scaled"] = panel.get("btc_exchange_netflow") / daily["btc_mcap_lag1"]
    daily["btc_exchange_netflow_scaled_lag1"] = daily["btc_exchange_netflow_scaled"].shift(1)
    daily["eth_oi"] = panel.get("eth_oi")
    daily["eth_oi_growth"] = log_return(daily["eth_oi"])
    daily["eth_oi_growth_lag1"] = daily["eth_oi_growth"].shift(1)
    daily["eth_oi_to_mcap"] = panel.get("eth_oi") / daily["eth_mcap_lag1"]
    daily["eth_oi_to_mcap_current"] = panel.get("eth_oi") / daily["eth_market_cap_usd"]
    daily["eth_oi_to_mcap_growth"] = log_return(daily["eth_oi_to_mcap_current"])
    daily["eth_oi_to_mcap_growth_lag1"] = daily["eth_oi_to_mcap_growth"].shift(1)
    daily["eth_oi_unit_assumption"] = "CryptoQuant all-exchange OI export treated as USD/notional-valued for scaling audit."
    daily["eth_funding_z"] = rolling_z(panel.get("eth_funding", pd.Series(index=panel.index, dtype=float)), 90)
    daily["eth_funding_z_lag1"] = daily["eth_funding_z"].shift(1)
    eth_long_liq = panel.get("eth_long_liq_usd", pd.Series(index=panel.index, dtype=float))
    eth_short_liq = panel.get("eth_short_liq_usd", pd.Series(index=panel.index, dtype=float))
    daily["eth_total_liq_usd"] = pd.concat([eth_long_liq, eth_short_liq], axis=1).sum(axis=1, min_count=1)
    eth_lag_oi = panel.get("eth_oi", pd.Series(index=panel.index, dtype=float)).shift(1)
    daily["eth_total_liq_to_lag_oi_pct"] = daily["eth_total_liq_usd"] / eth_lag_oi * 100
    daily["eth_total_liq_to_lag_mcap_bps"] = daily["eth_total_liq_usd"] / daily["eth_mcap_lag1"] * 10000
    daily["eth_total_liq_to_lag_oi_log1p"] = np.log1p(daily["eth_total_liq_usd"] / eth_lag_oi)
    daily["eth_total_liq_intensity"] = daily["eth_total_liq_to_lag_oi_pct"]
    daily["btc_dominance"] = panel.get("btc_dominance")
    daily["eth_dominance"] = panel.get("eth_dominance")
    daily["fear_greed_altme"] = panel.get("fng_value")
    daily["fear_greed_change"] = daily["fear_greed_altme"].diff()
    daily["fear_greed_altme_lag1"] = daily["fear_greed_altme"].shift(1)
    daily["fear_greed_change_lag1"] = daily["fear_greed_change"].shift(1)

    quintile_source = daily["btc_mvrv_percentile_lagged"]
    daily["btc_mvrv_quintile_lagged"] = pd.cut(
        quintile_source,
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1],
        labels=["Q1 low", "Q2", "Q3", "Q4", "Q5 high"],
        include_lowest=True,
    ).astype(str).replace("nan", np.nan)
    daily["btc_ret_fwd_1d"] = daily["btc_ret"].shift(-1)
    daily["btc_ret_fwd_7d"] = daily["btc_ret"].rolling(7).sum().shift(-7)
    daily["btc_future_30d_min_drawdown"] = (panel["btc_close"].shift(-30).rolling(30).min() / panel["btc_close"] - 1)

    daily["calendar"] = "crypto_calendar_daily"
    daily["calendar_assumption"] = CALENDAR_ASSUMPTIONS["crypto_calendar_daily"]
    daily["close_time_assumption"] = CLOSE_TIME_ASSUMPTION

    weekly = weekly_features(daily)
    tradfi_daily = tradfi_business_daily_features(daily)
    tradfi_weekly = tradfi_friday_weekly_features(daily)
    etf_daily = etf_trading_daily_features(daily)
    etf_weekly = tradfi_friday_weekly_features(daily, calendar_name="etf_friday_weekly")
    monthly = build_market_structure_monthly(root)

    daily.to_parquet(p.panels / "feature_store_daily.parquet")
    weekly.to_parquet(p.panels / "feature_store_weekly.parquet")
    weekly.to_parquet(p.panels / "feature_store_crypto_weekly.parquet")
    tradfi_daily.to_parquet(p.panels / "feature_store_tradfi_daily.parquet")
    tradfi_weekly.to_parquet(p.panels / "feature_store_tradfi_weekly.parquet")
    etf_daily.to_parquet(p.panels / "feature_store_etf_trading_daily.parquet")
    etf_weekly.to_parquet(p.panels / "feature_store_etf_trading_weekly.parquet")
    monthly.to_parquet(p.panels / "market_structure_monthly.parquet")

    feature_registry = pd.DataFrame(feature_registry_rows())
    for frame_col, which in [("first_valid_date", "first"), ("last_valid_date", "last")]:
        feature_registry[frame_col] = feature_registry["feature_id"].map(
            lambda f, which=which: feature_date(daily, weekly, monthly, f, which)
        )
    write_csv(p.tables / "feature_registry.csv", feature_registry)
    coverage = feature_coverage_table(daily, weekly, monthly)
    write_csv(p.tables / "feature_coverage.csv", coverage)
    return daily, weekly, monthly


def feature_date(daily: pd.DataFrame, weekly: pd.DataFrame, monthly: pd.DataFrame, feature: str, which: str) -> str:
    for frame in [daily, weekly, monthly]:
        if feature in frame.columns:
            dates = frame.index[pd.notna(frame[feature])]
            if len(dates) == 0:
                return ""
            value = dates.min() if which == "first" else dates.max()
            return pd.Timestamp(value).date().isoformat()
    return ""


def feature_coverage_table(daily: pd.DataFrame, weekly: pd.DataFrame, monthly: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, frame in [("daily", daily), ("weekly", weekly), ("monthly", monthly)]:
        for column in frame.columns:
            series = frame[column]
            valid = series.dropna()
            rows.append(
                {
                    "feature_id": column,
                    "frequency": label,
                    "observations": int(len(valid)),
                    "first_valid_date": valid.index.min().date().isoformat() if not valid.empty else "",
                    "last_valid_date": valid.index.max().date().isoformat() if not valid.empty else "",
                    "missing_pct": round(float(series.isna().mean()), 4),
                }
            )
    return pd.DataFrame(rows)


def weekly_features(daily: pd.DataFrame) -> pd.DataFrame:
    weekly = pd.DataFrame(index=daily.resample("W-SUN").size().index)

    for col in [c for c in daily.columns if c.endswith("_ret")]:
        weekly[col] = daily[col].resample("W-SUN").sum(min_count=1)

    for col in [c for c in daily.columns if c.endswith("_d1") or c.startswith("d_log_")]:
        weekly[col] = daily[col].resample("W-SUN").sum(min_count=1)

    level_cols = [
        "btc_close",
        "eth_close",
        "spy_close",
        "qqq_close",
        "iwm_close",
        "gold_close",
        "dxy_close",
        "vix_level",
        "real_yield_level",
        "nominal_10y_level",
        "btc_market_cap_usd",
        "eth_market_cap_usd",
        "stablecoin_supply_usd",
        "defi_tvl_usd",
        "btc_oi",
        "btc_oi_to_mcap_current",
        "btc_funding",
        "btc_funding_z",
        "eth_oi",
        "eth_oi_to_mcap_current",
        "eth_funding_z",
        "btc_leverage_ratio_percentile",
        "btc_exchange_netflow_scaled",
        "btc_mvrv",
        "btc_mvrv_percentile_lagged",
        "btc_mvrv_z_365_lagged",
        "btc_realized_cap_usd",
        "btc_realized_price_gap_lag1",
        "btc_dominance",
        "eth_dominance",
        "fear_greed_altme",
        "stablecoin_to_tvl",
        "stablecoin_share_crypto_proxy",
    ]
    for col in [c for c in level_cols if c in daily.columns]:
        weekly[col] = daily[col].resample("W-SUN").last()

    for col in ["btc_etf_net_flow_usd", "eth_etf_net_flow_usd", "btc_total_liq_usd", "eth_total_liq_usd"]:
        if col in daily.columns:
            weekly[col] = daily[col].resample("W-SUN").sum(min_count=1)

    weekly["btc_mcap_lag1"] = weekly["btc_market_cap_usd"].shift(1)
    weekly["eth_mcap_lag1"] = weekly["eth_market_cap_usd"].shift(1)
    weekly["stablecoin_supply_growth"] = log_return(weekly["stablecoin_supply_usd"])
    weekly["defi_tvl_growth"] = log_return(weekly["defi_tvl_usd"])
    weekly["valuation_sensitive_defi_tvl_growth"] = weekly["defi_tvl_growth"]
    weekly["stablecoin_supply_growth_lag1"] = weekly["stablecoin_supply_growth"].shift(1)
    weekly["defi_tvl_growth_lag1"] = weekly["defi_tvl_growth"].shift(1)
    weekly["valuation_sensitive_defi_tvl_growth_lag1"] = weekly["valuation_sensitive_defi_tvl_growth"].shift(1)
    weekly["btc_oi_growth"] = log_return(weekly["btc_oi"])
    weekly["btc_oi_growth_lag1"] = weekly["btc_oi_growth"].shift(1)
    weekly["btc_oi_to_mcap"] = weekly["btc_oi"] / weekly["btc_mcap_lag1"]
    weekly["btc_oi_to_mcap_current"] = weekly["btc_oi"] / weekly["btc_market_cap_usd"]
    weekly["btc_oi_to_mcap_growth"] = log_return(weekly["btc_oi_to_mcap_current"])
    weekly["btc_oi_to_mcap_growth_lag1"] = weekly["btc_oi_to_mcap_growth"].shift(1)
    weekly["btc_funding_z_lag1"] = weekly["btc_funding_z"].shift(1)
    weekly["eth_oi_growth"] = log_return(weekly["eth_oi"])
    weekly["eth_oi_growth_lag1"] = weekly["eth_oi_growth"].shift(1)
    weekly["eth_oi_to_mcap"] = weekly["eth_oi"] / weekly["eth_mcap_lag1"]
    weekly["eth_oi_to_mcap_current"] = weekly["eth_oi"] / weekly["eth_market_cap_usd"]
    weekly["eth_oi_to_mcap_growth"] = log_return(weekly["eth_oi_to_mcap_current"])
    weekly["eth_oi_to_mcap_growth_lag1"] = weekly["eth_oi_to_mcap_growth"].shift(1)
    weekly["eth_funding_z_lag1"] = weekly["eth_funding_z"].shift(1)
    weekly["btc_exchange_netflow_scaled_lag1"] = weekly["btc_exchange_netflow_scaled"].shift(1)
    weekly["fear_greed_change"] = weekly["fear_greed_altme"].diff()
    weekly["fear_greed_altme_lag1"] = weekly["fear_greed_altme"].shift(1)
    weekly["fear_greed_change_lag1"] = weekly["fear_greed_change"].shift(1)
    weekly["btc_etf_flow_intensity_lag0"] = weekly["btc_etf_net_flow_usd"] / weekly["btc_mcap_lag1"]
    weekly["eth_etf_flow_intensity_lag0"] = weekly["eth_etf_net_flow_usd"] / weekly["eth_mcap_lag1"]
    weekly["btc_etf_flow_intensity_lag1"] = weekly["btc_etf_flow_intensity_lag0"].shift(1)
    weekly["eth_etf_flow_intensity_lag1"] = weekly["eth_etf_flow_intensity_lag0"].shift(1)
    weekly["btc_etf_flow_intensity"] = weekly["btc_etf_flow_intensity_lag0"]
    weekly["eth_etf_flow_intensity"] = weekly["eth_etf_flow_intensity_lag0"]
    weekly["btc_total_liq_to_lag_oi_pct"] = weekly["btc_total_liq_usd"] / weekly["btc_oi"].shift(1) * 100
    weekly["btc_total_liq_to_lag_mcap_bps"] = weekly["btc_total_liq_usd"] / weekly["btc_mcap_lag1"] * 10000
    weekly["eth_total_liq_to_lag_oi_pct"] = weekly["eth_total_liq_usd"] / weekly["eth_oi"].shift(1) * 100
    weekly["eth_total_liq_to_lag_mcap_bps"] = weekly["eth_total_liq_usd"] / weekly["eth_mcap_lag1"] * 10000
    weekly["btc_realized_vol_30d"] = daily["btc_ret"].resample("W-SUN").std() * math.sqrt(365)
    weekly["eth_realized_vol_30d"] = daily["eth_ret"].resample("W-SUN").std() * math.sqrt(365)
    weekly["btc_ret_fwd_1d"] = weekly["btc_ret"].shift(-1)
    weekly["btc_ret_fwd_7d"] = weekly["btc_ret"].shift(-1)
    weekly["calendar"] = "crypto_week_sunday"
    weekly["calendar_assumption"] = CALENDAR_ASSUMPTIONS["crypto_week_sunday"]
    weekly["close_time_assumption"] = CLOSE_TIME_ASSUMPTION
    return weekly


def annotate_calendar(frame: pd.DataFrame, calendar: str, assumption: str | None = None) -> pd.DataFrame:
    out = frame.copy()
    out["calendar"] = calendar
    out["calendar_assumption"] = assumption or CALENDAR_ASSUMPTIONS.get(calendar, "")
    out["close_time_assumption"] = CLOSE_TIME_ASSUMPTION
    return out


def recompute_lagged_state_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    lag_pairs = {
        "stablecoin_supply_growth": "stablecoin_supply_growth_lag1",
        "valuation_sensitive_defi_tvl_growth": "valuation_sensitive_defi_tvl_growth_lag1",
        "defi_tvl_growth": "defi_tvl_growth_lag1",
        "btc_oi_growth": "btc_oi_growth_lag1",
        "eth_oi_growth": "eth_oi_growth_lag1",
        "btc_oi_to_mcap_growth": "btc_oi_to_mcap_growth_lag1",
        "eth_oi_to_mcap_growth": "eth_oi_to_mcap_growth_lag1",
        "btc_funding_z": "btc_funding_z_lag1",
        "eth_funding_z": "eth_funding_z_lag1",
        "btc_exchange_netflow_scaled": "btc_exchange_netflow_scaled_lag1",
        "fear_greed_altme": "fear_greed_altme_lag1",
        "fear_greed_change": "fear_greed_change_lag1",
    }
    for source, lagged in lag_pairs.items():
        if source in out:
            out[lagged] = out[source].shift(1)
    return out


def recompute_tradfi_features_on_index(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for asset in ["btc", "eth"]:
        close_col = f"{asset}_close"
        if close_col in out:
            out[f"{asset}_ret"] = log_return(out[close_col])
    close_return_pairs = {
        "spy_close": "spy_ret",
        "qqq_close": "qqq_ret",
        "iwm_close": "iwm_ret",
        "gold_close": "gold_ret",
        "dxy_close": "dxy_ret",
    }
    for close_col, ret_col in close_return_pairs.items():
        if close_col in out:
            out[ret_col] = log_return(out[close_col])
    level_change_pairs = {
        "vix_level": "vix_d1",
        "real_yield_level": "real_yield_d1",
        "nominal_10y_level": "nominal_10y_d1",
    }
    for level_col, change_col in level_change_pairs.items():
        if level_col in out:
            out[change_col] = pd.to_numeric(out[level_col], errors="coerce").diff()
    return out


def tradfi_business_daily_features(daily: pd.DataFrame) -> pd.DataFrame:
    level_cols = [
        "spy_close",
        "qqq_close",
        "iwm_close",
        "gold_close",
        "dxy_close",
        "vix_level",
        "real_yield_level",
        "nominal_10y_level",
    ]
    present = [col for col in level_cols if col in daily.columns]
    mask = daily[present].notna().any(axis=1) if present else pd.Series(False, index=daily.index)
    panel = recompute_tradfi_features_on_index(daily.loc[mask].copy())
    panel = recompute_lagged_state_features(panel)
    return annotate_calendar(panel, "tradfi_business_daily")


def tradfi_friday_weekly_features(daily: pd.DataFrame, calendar_name: str = "tradfi_friday_weekly") -> pd.DataFrame:
    level_cols = [
        "btc_close",
        "eth_close",
        "spy_close",
        "qqq_close",
        "iwm_close",
        "gold_close",
        "dxy_close",
        "vix_level",
        "real_yield_level",
        "nominal_10y_level",
        "btc_market_cap_usd",
        "eth_market_cap_usd",
        "stablecoin_supply_usd",
        "defi_tvl_usd",
        "btc_oi",
        "eth_oi",
        "btc_funding_z",
        "eth_funding_z",
        "btc_exchange_netflow_scaled",
        "fear_greed_altme",
        "stablecoin_to_tvl",
        "stablecoin_share_crypto_proxy",
    ]
    weekly = pd.DataFrame(index=daily.resample("W-FRI").size().index)
    for col in [c for c in level_cols if c in daily.columns]:
        weekly[col] = daily[col].resample("W-FRI").last()
    for col in ["btc_etf_net_flow_usd", "eth_etf_net_flow_usd", "btc_total_liq_usd", "eth_total_liq_usd"]:
        if col in daily.columns:
            weekly[col] = daily[col].resample("W-FRI").sum(min_count=1)
    weekly = recompute_tradfi_features_on_index(weekly)
    weekly["btc_mcap_lag1"] = weekly["btc_market_cap_usd"].shift(1)
    weekly["eth_mcap_lag1"] = weekly["eth_market_cap_usd"].shift(1)
    weekly["stablecoin_supply_growth"] = log_return(weekly["stablecoin_supply_usd"])
    weekly["defi_tvl_growth"] = log_return(weekly["defi_tvl_usd"])
    weekly["valuation_sensitive_defi_tvl_growth"] = weekly["defi_tvl_growth"]
    weekly["btc_oi_growth"] = log_return(weekly["btc_oi"])
    weekly["eth_oi_growth"] = log_return(weekly["eth_oi"])
    weekly["btc_oi_to_mcap_current"] = weekly["btc_oi"] / weekly["btc_market_cap_usd"]
    weekly["eth_oi_to_mcap_current"] = weekly["eth_oi"] / weekly["eth_market_cap_usd"]
    weekly["btc_oi_to_mcap"] = weekly["btc_oi"] / weekly["btc_mcap_lag1"]
    weekly["eth_oi_to_mcap"] = weekly["eth_oi"] / weekly["eth_mcap_lag1"]
    weekly["btc_oi_to_mcap_growth"] = log_return(weekly["btc_oi_to_mcap_current"])
    weekly["eth_oi_to_mcap_growth"] = log_return(weekly["eth_oi_to_mcap_current"])
    weekly["fear_greed_change"] = weekly["fear_greed_altme"].diff()
    weekly["btc_etf_flow_intensity_lag0"] = weekly["btc_etf_net_flow_usd"] / weekly["btc_mcap_lag1"]
    weekly["eth_etf_flow_intensity_lag0"] = weekly["eth_etf_net_flow_usd"] / weekly["eth_mcap_lag1"]
    weekly["btc_etf_flow_intensity"] = weekly["btc_etf_flow_intensity_lag0"]
    weekly["eth_etf_flow_intensity"] = weekly["eth_etf_flow_intensity_lag0"]
    weekly["btc_total_liq_to_lag_oi_pct"] = weekly["btc_total_liq_usd"] / weekly["btc_oi"].shift(1) * 100
    weekly["eth_total_liq_to_lag_oi_pct"] = weekly["eth_total_liq_usd"] / weekly["eth_oi"].shift(1) * 100
    weekly = recompute_lagged_state_features(weekly)
    weekly["btc_realized_vol_30d"] = weekly["btc_ret"].rolling(4, min_periods=3).std() * math.sqrt(52)
    weekly["eth_realized_vol_30d"] = weekly["eth_ret"].rolling(4, min_periods=3).std() * math.sqrt(52)
    assumption = CALENDAR_ASSUMPTIONS["tradfi_friday_weekly"]
    if calendar_name != "tradfi_friday_weekly":
        assumption = assumption + " ETF-era weekly rows are Friday-ended trading-week summaries."
    return annotate_calendar(weekly, calendar_name, assumption)


def etf_trading_daily_features(daily: pd.DataFrame) -> pd.DataFrame:
    flow_cols = ["btc_etf_net_flow_usd", "eth_etf_net_flow_usd"]
    present = [col for col in flow_cols if col in daily.columns]
    mask = daily[present].notna().any(axis=1) if present else pd.Series(False, index=daily.index)
    panel = recompute_tradfi_features_on_index(daily.loc[mask].copy())
    panel["btc_mcap_lag1"] = panel["btc_market_cap_usd"].shift(1)
    panel["eth_mcap_lag1"] = panel["eth_market_cap_usd"].shift(1)
    panel["btc_etf_flow_intensity_lag0"] = panel["btc_etf_net_flow_usd"] / panel["btc_mcap_lag1"]
    panel["eth_etf_flow_intensity_lag0"] = panel["eth_etf_net_flow_usd"] / panel["eth_mcap_lag1"]
    panel["btc_etf_flow_intensity_lag1"] = panel["btc_etf_flow_intensity_lag0"].shift(1)
    panel["eth_etf_flow_intensity_lag1"] = panel["eth_etf_flow_intensity_lag0"].shift(1)
    panel["btc_etf_flow_intensity"] = panel["btc_etf_flow_intensity_lag0"]
    panel["eth_etf_flow_intensity"] = panel["eth_etf_flow_intensity_lag0"]
    panel = recompute_lagged_state_features(panel)
    return annotate_calendar(panel, "etf_trading_daily")


def classify_pit_asset(row: pd.Series) -> str:
    symbol = str(row.get("symbol", "")).upper().strip()
    name = str(row.get("asset_name", "")).upper()
    coingecko_id = str(row.get("coingecko_id", "")).lower().strip()
    asset_key = str(row.get("asset_key", "")).lower().strip()
    token_id = str(row.get("token_id", "")).lower().strip()
    canonical_key = asset_key if asset_key.startswith("coingecko:") else coingecko_id
    if canonical_key in CANONICAL_SELECTED_BY_KEY or coingecko_id in CANONICAL_SELECTED_BY_ID:
        asset = CANONICAL_SELECTED_BY_KEY.get(canonical_key, CANONICAL_SELECTED_BY_ID.get(coingecko_id))
        if asset and asset["symbol"] == "BTC":
            return "BTC"
        if asset and asset["symbol"] == "ETH":
            return "ETH"
        return "selected majors ex BTC/ETH"
    if coingecko_id in PRODUCTIZED_ASSET_IDS or canonical_key in PRODUCTIZED_ASSET_IDS:
        return "productized/wrapped assets"
    if coingecko_id in GOVERNANCE_RISK_IDS or canonical_key in GOVERNANCE_RISK_IDS:
        return "governance/infrastructure risk assets"
    if coingecko_id in STABLE_ASSET_IDS or canonical_key in STABLE_ASSET_IDS:
        return "stable-like assets"
    stable = {
        "USDT",
        "USDC",
        "DAI",
        "FDUSD",
        "BUSD",
        "TUSD",
        "USDE",
        "USDS",
        "PYUSD",
        "USDP",
        "USDD",
        "USDT0",
        "USD0",
        "USD1",
    }
    productized = {
        "WBTC",
        "WETH",
        "CBBTC",
        "STETH",
        "WSTETH",
        "RETH",
        "WEETH",
        "WBETH",
        "CBETH",
        "PAXG",
        "XAUT",
    }
    if symbol in stable or "STABLE" in name or token_id in {"tether", "usd-coin", "dai"}:
        return "stable-like assets"
    if symbol in productized or "WRAPPED" in name or "STAKED" in name or "LIQUID STAK" in name:
        return "productized/wrapped assets"
    return "other risk assets"


def build_market_structure_monthly(root: Path = PROJECT_ROOT) -> pd.DataFrame:
    source = root / "Data" / "MarketStructure" / "DefiLlama" / "crypto_universe_monthly_2020_2026.csv"
    frame = pd.read_csv(source)
    frame["snapshot_date"] = pd.to_datetime(frame["snapshot_date"], errors="coerce")
    frame["month"] = pd.to_datetime(frame["month"].astype(str) + "-01", errors="coerce")
    if "is_partial_month" not in frame:
        frame["is_partial_month"] = frame["snapshot_date"].dt.to_period("M").dt.to_timestamp("M") != frame["snapshot_date"]
    if frame["is_partial_month"].dtype == object:
        frame["is_partial_month"] = frame["is_partial_month"].astype(str).str.lower().isin({"true", "1", "yes"})
    else:
        frame["is_partial_month"] = frame["is_partial_month"].fillna(False).astype(bool)
    frame = frame.dropna(subset=["month", "market_cap_usd"])
    frame["asset_class_final"] = frame.apply(classify_pit_asset, axis=1)
    frame = frame.sort_values(["month", "market_cap_usd"], ascending=[True, False])
    frame["rank_full_market"] = frame.groupby("month")["market_cap_usd"].rank(ascending=False, method="first")
    frame["in_full_top100"] = frame["rank_full_market"] <= 100
    frame = frame.set_index("month", drop=False).sort_index()
    return frame


def standardize(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.astype(float).copy()
    return (out - out.mean()) / out.std(ddof=0).replace(0, np.nan)


def fit_hac_ols(y: pd.Series, x: pd.DataFrame, hac_lags: int = 5) -> dict[str, Any]:
    df = pd.concat([y.rename("target"), x], axis=1).replace([np.inf, -np.inf], np.nan).dropna()
    if len(df) < max(30, x.shape[1] + 5):
        return {"n": len(df), "r2": np.nan, "adj_r2": np.nan, "params": pd.Series(dtype=float), "t": pd.Series(dtype=float), "p": pd.Series(dtype=float), "sse": np.nan}
    xmat = sm.add_constant(df[x.columns], has_constant="add")
    result = sm.OLS(df["target"], xmat).fit(cov_type="HAC", cov_kwds={"maxlags": hac_lags})
    resid = result.resid
    return {
        "n": len(df),
        "r2": float(result.rsquared),
        "adj_r2": float(result.rsquared_adj),
        "params": result.params.drop("const", errors="ignore"),
        "t": result.tvalues.drop("const", errors="ignore"),
        "p": result.pvalues.drop("const", errors="ignore"),
        "sse": float(np.square(resid).sum()),
    }


def index_signature(index: pd.Index) -> str:
    dates = pd.to_datetime(index).strftime("%Y-%m-%d").tolist()
    payload = "|".join(dates).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def make_estimation_frame(
    frame: pd.DataFrame,
    target: str,
    features: list[str],
    mask: pd.Series | None = None,
) -> pd.DataFrame:
    cols = [target, *features]
    if len(set(cols)) != len(cols):
        raise ValueError(f"duplicate columns in model specification: {cols}")
    if missing := [col for col in cols if col not in frame.columns]:
        raise ValueError(f"missing model columns: {missing}")
    data = frame.loc[mask] if mask is not None else frame
    estimation = data[cols].replace([np.inf, -np.inf], np.nan).dropna().copy()
    estimation.sort_index(inplace=True)
    estimation.attrs["immutable_estimation_frame"] = True
    return estimation


def fit_ols_estimation_frame(
    estimation: pd.DataFrame,
    target: str,
    features: list[str],
    hac_lags: int,
) -> dict[str, Any]:
    if len(estimation) < max(30, len(features) + 5):
        return {
            "n": len(estimation),
            "r2": np.nan,
            "adj_r2": np.nan,
            "params": pd.Series(dtype=float),
            "t": pd.Series(dtype=float),
            "p": pd.Series(dtype=float),
            "sse": np.nan,
        }
    y = estimation[target].astype(float)
    y_std = (y - y.mean()) / y.std(ddof=0)
    if features:
        x_std = standardize(estimation[features])
        xmat = sm.add_constant(x_std, has_constant="add")
    else:
        xmat = pd.DataFrame({"const": np.ones(len(estimation))}, index=estimation.index)
    result = sm.OLS(y_std, xmat).fit(cov_type="HAC", cov_kwds={"maxlags": hac_lags})
    resid = result.resid
    return {
        "n": len(estimation),
        "r2": float(result.rsquared),
        "adj_r2": float(result.rsquared_adj),
        "params": result.params.drop("const", errors="ignore"),
        "t": result.tvalues.drop("const", errors="ignore"),
        "p": result.pvalues.drop("const", errors="ignore"),
        "sse": float(np.square(resid).sum()),
    }


def conventional_partial_r2(full: dict[str, Any], reduced: dict[str, Any]) -> float:
    reduced_sse = float(reduced.get("sse", np.nan))
    full_sse = float(full.get("sse", np.nan))
    if not np.isfinite(reduced_sse) or not np.isfinite(full_sse) or reduced_sse <= 0:
        return np.nan
    value = (reduced_sse - full_sse) / reduced_sse
    if value < -NESTED_TOL or value > 1 + NESTED_TOL:
        raise ValueError(f"conventional partial R2 outside [0,1]: {value}")
    if -NESTED_TOL <= value < 0:
        return 0.0
    if 1 < value <= 1 + NESTED_TOL:
        return 1.0
    return float(value)


def assert_nested_result(
    full: dict[str, Any],
    reduced: dict[str, Any],
    context: str,
) -> tuple[float, float]:
    if int(full["n"]) != int(reduced["n"]):
        raise ValueError(f"{context}: full/reduced sample mismatch {full['n']} vs {reduced['n']}")
    full_r2 = float(full.get("r2", np.nan))
    reduced_r2 = float(reduced.get("r2", np.nan))
    if np.isfinite(full_r2) and np.isfinite(reduced_r2) and full_r2 + NESTED_TOL < reduced_r2:
        raise ValueError(f"{context}: full R2 {full_r2} below reduced R2 {reduced_r2}")
    delta = full_r2 - reduced_r2 if np.isfinite(full_r2) and np.isfinite(reduced_r2) else np.nan
    if np.isfinite(delta) and delta < -NESTED_TOL:
        raise ValueError(f"{context}: negative drop-block delta R2 {delta}")
    partial = conventional_partial_r2(full, reduced)
    return float(delta), partial


def bh_fdr(pvals: pd.Series) -> pd.Series:
    clean = pvals.dropna().astype(float)
    if clean.empty:
        return pd.Series(index=pvals.index, dtype=float)
    order = clean.sort_values().index
    ranked = clean.loc[order]
    m = len(ranked)
    adjusted = ranked * m / np.arange(1, m + 1)
    adjusted = adjusted.iloc[::-1].cummin().iloc[::-1].clip(upper=1)
    return adjusted.reindex(pvals.index)


def tradfi_contemporaneous_blocks() -> dict[str, list[str]]:
    return {
        "equity_beta": ["qqq_ret", "spy_ret", "iwm_ret"],
        "macro_rates_fx_vol": ["dxy_ret", "gold_ret", "vix_d1", "real_yield_d1", "nominal_10y_d1"],
    }


def lagged_state_blocks(asset: str) -> dict[str, list[str]]:
    native = [f"{asset}_oi_to_mcap_growth_lag1", f"{asset}_funding_z_lag1"]
    if asset == "btc":
        native.append("btc_exchange_netflow_scaled_lag1")
    return {
        "liquidity_state": ["stablecoin_supply_growth_lag1", "valuation_sensitive_defi_tvl_growth_lag1"],
        "sentiment_state": ["fear_greed_altme_lag1", "fear_greed_change_lag1"],
        "lagged_leverage_state": native,
    }


def etf_augmented_blocks(asset: str) -> dict[str, list[str]]:
    blocks = tradfi_contemporaneous_blocks()
    blocks.update(
        {
            "etf_flow_lag0": [f"{asset}_etf_flow_intensity_lag0"],
            "etf_flow_lag1": [f"{asset}_etf_flow_intensity_lag1"],
            "lagged_state": [feature for values in lagged_state_blocks(asset).values() for feature in values],
        }
    )
    return blocks


def model_feature_blocks(asset: str = "btc", model_family: str = "long_sample_lagged_state_association") -> dict[str, list[str]]:
    if model_family == "long_sample_contemporaneous_exposure":
        return tradfi_contemporaneous_blocks()
    if model_family == "etf_era_augmented":
        return etf_augmented_blocks(asset)
    return lagged_state_blocks(asset)


def available_features(frame: pd.DataFrame, features: list[str], min_obs: int = 40) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for feature in features:
        if feature in seen:
            continue
        seen.add(feature)
        if feature in frame.columns and frame[feature].replace([np.inf, -np.inf], np.nan).notna().sum() >= min_obs:
            out.append(feature)
    return out


def model_regime_masks(frame: pd.DataFrame, asset: str, model_family: str) -> dict[str, pd.Series]:
    all_rows = pd.Series(True, index=frame.index)
    btc_era = pd.Series(frame.index >= BTC_ETF_START, index=frame.index)
    pre_btc_era = pd.Series(frame.index < BTC_ETF_START, index=frame.index)
    if model_family == "long_sample_contemporaneous_exposure":
        return {
            "full_common_sample": all_rows,
            "pre_btc_etf": pre_btc_era,
            "btc_etf_era": btc_era,
        }
    if model_family == "etf_era_augmented":
        start = BTC_ETF_START if asset == "btc" else ETH_ETF_START
        return {f"{asset}_etf_era": pd.Series(frame.index >= start, index=frame.index)}
    return {"full_common_sample": all_rows}


def model_acceptance_threshold(frequency: str, model_family: str, regime: str) -> int:
    if frequency == "weekly" and model_family != "etf_era_augmented":
        return 100
    if frequency == "weekly":
        return 40
    if model_family == "etf_era_augmented" or regime.endswith("_etf_era"):
        return 80
    return 120


def model_specs_for(asset: str) -> list[dict[str, Any]]:
    return [
        {
            "model_family": "long_sample_contemporaneous_exposure",
            "target": f"{asset}_ret",
            "purpose": "co_movement_integration",
            "blocks": tradfi_contemporaneous_blocks(),
        },
        {
            "model_family": "long_sample_lagged_state_association",
            "target": f"{asset}_ret",
            "purpose": "lagged_state_association",
            "blocks": lagged_state_blocks(asset),
        },
        {
            "model_family": "etf_era_augmented",
            "target": f"{asset}_ret",
            "purpose": "etf_era_market_plumbing",
            "blocks": etf_augmented_blocks(asset),
        },
    ]


def panel_calendar_value(frame: pd.DataFrame, column: str) -> str:
    if column in frame.columns:
        values = frame[column].dropna()
        if not values.empty:
            return str(values.iloc[0])
    return ""


def exposure_tables(
    daily: pd.DataFrame,
    tradfi_daily: pd.DataFrame,
    tradfi_weekly: pd.DataFrame,
    crypto_weekly: pd.DataFrame,
    etf_daily: pd.DataFrame,
    etf_weekly: pd.DataFrame,
    p: BuildPaths,
) -> dict[str, pd.DataFrame]:
    outputs: dict[str, pd.DataFrame] = {}
    strength_frames = []
    block_frames = []
    partial_frames = []
    fdr_frames = []
    multi_frames = []
    ridge_frames = []
    freq_frames = []
    frame_routes = {
        ("long_sample_contemporaneous_exposure", "daily"): (tradfi_daily, 5),
        ("long_sample_contemporaneous_exposure", "weekly"): (tradfi_weekly, 4),
        ("long_sample_lagged_state_association", "daily"): (daily, 5),
        ("long_sample_lagged_state_association", "weekly"): (crypto_weekly, 4),
        ("etf_era_augmented", "daily"): (etf_daily, 5),
        ("etf_era_augmented", "weekly"): (etf_weekly, 4),
    }
    for asset, target in [("btc", "btc_ret"), ("eth", "eth_ret")]:
        for spec in model_specs_for(asset):
            model_family = spec["model_family"]
            for frequency in ["daily", "weekly"]:
                frame, hac = frame_routes[(model_family, frequency)]
                if target not in frame:
                    continue
                calendar = panel_calendar_value(frame, "calendar")
                calendar_assumption = panel_calendar_value(frame, "calendar_assumption")
                close_time_assumption = panel_calendar_value(frame, "close_time_assumption")
                model_family = spec["model_family"]
                blocks = {
                    block: available_features(frame, features, min_obs=30 if frequency == "weekly" else 40)
                    for block, features in spec["blocks"].items()
                }
                blocks = {block: features for block, features in blocks.items() if features}
                flat_features = available_features(frame, [f for values in blocks.values() for f in values], min_obs=30 if frequency == "weekly" else 40)
                if not flat_features:
                    continue
                for regime, mask in model_regime_masks(frame, asset, model_family).items():
                    threshold = model_acceptance_threshold(frequency, model_family, regime)
                    estimation = make_estimation_frame(frame, target, flat_features, mask)
                    if len(estimation) < threshold:
                        freq_frames.append(
                            {
                                "asset": asset.upper(),
                                "frequency": frequency,
                                "model_family": model_family,
                                "regime": regime,
                                "n": int(len(estimation)),
                                "acceptance_threshold": threshold,
                                "full_r2": np.nan,
                                "feature_count": len(flat_features),
                                "calendar": calendar,
                                "calendar_assumption": calendar_assumption,
                                "close_time_assumption": close_time_assumption,
                                "status": "skipped_insufficient_common_sample",
                            }
                        )
                        continue
                    full = fit_ols_estimation_frame(estimation, target, flat_features, hac)
                    if not np.isfinite(full["r2"]):
                        raise ValueError(f"{asset} {frequency} {model_family} {regime}: full model did not fit")
                    pvals = full["p"].reindex(flat_features)
                    qvals = bh_fdr(pvals)
                    sample_start = estimation.index.min().date().isoformat()
                    sample_end = estimation.index.max().date().isoformat()
                    row_hash = index_signature(estimation.index)
                    feature_list = "|".join(flat_features)
                    for feature in flat_features:
                        reduced_features = [f for f in flat_features if f != feature]
                        reduced = fit_ols_estimation_frame(estimation, target, reduced_features, hac)
                        delta, _ = assert_nested_result(full, reduced, f"{asset} {frequency} {model_family} {regime} drop {feature}")
                        uni = fit_ols_estimation_frame(estimation, target, [feature], hac)
                        corr = estimation[target].corr(estimation[feature])
                        strength_frames.append(
                            {
                                "asset": asset.upper(),
                                "frequency": frequency,
                                "model_family": model_family,
                                "regime": regime,
                                "purpose": spec["purpose"],
                                "target": target,
                                "feature_id": feature,
                                "feature_label": clean_label(feature),
                                "block": next((block for block, values in blocks.items() if feature in values), "other"),
                                "n": int(full["n"]),
                                "n_full": int(full["n"]),
                                "n_reduced": int(reduced["n"]),
                                "same_support": int(full["n"]) == int(reduced["n"]),
                                "sample_start": sample_start,
                                "sample_end": sample_end,
                                "calendar": calendar,
                                "calendar_assumption": calendar_assumption,
                                "close_time_assumption": close_time_assumption,
                                "feature_list": feature_list,
                                "row_index_hash": row_hash,
                                "correlation": corr,
                                "univariate_r2": uni["r2"],
                                "standardized_beta": full["params"].get(feature, np.nan),
                                "hac_t": full["t"].get(feature, np.nan),
                                "p_value": pvals.get(feature, np.nan),
                                "fdr_q_value": qvals.get(feature, np.nan),
                                "drop_feature_delta_r2": delta,
                            }
                        )
                        fdr_frames.append(
                            {
                                "asset": asset.upper(),
                                "frequency": frequency,
                                "model_family": model_family,
                                "regime": regime,
                                "target": target,
                                "feature_id": feature,
                                "n": int(full["n"]),
                                "sample_start": sample_start,
                                "sample_end": sample_end,
                                "calendar": calendar,
                                "calendar_assumption": calendar_assumption,
                                "close_time_assumption": close_time_assumption,
                                "p_value": pvals.get(feature, np.nan),
                                "fdr_q_value": qvals.get(feature, np.nan),
                            }
                        )
                    for block, block_features in blocks.items():
                        reduced_features = [f for f in flat_features if f not in block_features]
                        reduced = fit_ols_estimation_frame(estimation, target, reduced_features, hac)
                        delta, partial = assert_nested_result(full, reduced, f"{asset} {frequency} {model_family} {regime} block {block}")
                        block_frames.append(
                            {
                                "asset": asset.upper(),
                                "frequency": frequency,
                                "model_family": model_family,
                                "regime": regime,
                                "purpose": spec["purpose"],
                                "block": block,
                                "target": target,
                                "n": int(full["n"]),
                                "n_full": int(full["n"]),
                                "n_reduced": int(reduced["n"]),
                                "same_support": int(full["n"]) == int(reduced["n"]),
                                "sample_start": sample_start,
                                "sample_end": sample_end,
                                "calendar": calendar,
                                "calendar_assumption": calendar_assumption,
                                "close_time_assumption": close_time_assumption,
                                "feature_list": feature_list,
                                "dropped_features": "|".join(block_features),
                                "row_index_hash": row_hash,
                                "full_r2": full["r2"],
                                "reduced_r2": reduced["r2"],
                                "drop_block_delta_r2": delta,
                                "method_note": "R2_full - R2_reduced on one complete-case estimation frame; not conventional partial R-squared",
                            }
                        )
                        partial_frames.append(
                            {
                                "asset": asset.upper(),
                                "frequency": frequency,
                                "model_family": model_family,
                                "regime": regime,
                                "block": block,
                                "target": target,
                                "n": int(full["n"]),
                                "n_full": int(full["n"]),
                                "n_reduced": int(reduced["n"]),
                                "same_support": int(full["n"]) == int(reduced["n"]),
                                "sample_start": sample_start,
                                "sample_end": sample_end,
                                "calendar": calendar,
                                "calendar_assumption": calendar_assumption,
                                "close_time_assumption": close_time_assumption,
                                "feature_list": feature_list,
                                "dropped_features": "|".join(block_features),
                                "row_index_hash": row_hash,
                                "full_sse": full["sse"],
                                "reduced_sse": reduced["sse"],
                                "conventional_partial_r2": partial,
                                "formula": "(SSE_reduced - SSE_full) / SSE_reduced on the same complete-case estimation frame",
                            }
                        )
                    multi_frames.extend(
                        multicollinearity_rows(
                            asset,
                            frequency,
                            standardize(estimation[flat_features]),
                            model_family,
                            regime,
                            row_hash,
                            calendar,
                            calendar_assumption,
                        )
                    )
                    ridge_frames.extend(
                        ridge_stability_rows(
                            asset,
                            frequency,
                            estimation[target],
                            standardize(estimation[flat_features]),
                            model_family,
                            regime,
                            row_hash,
                            calendar,
                            calendar_assumption,
                        )
                    )
                    freq_frames.append(
                        {
                            "asset": asset.upper(),
                            "frequency": frequency,
                            "model_family": model_family,
                            "regime": regime,
                            "n": int(full["n"]),
                            "acceptance_threshold": threshold,
                            "sample_start": sample_start,
                            "sample_end": sample_end,
                            "calendar": calendar,
                            "calendar_assumption": calendar_assumption,
                            "close_time_assumption": close_time_assumption,
                            "full_r2": full["r2"],
                            "feature_count": len(flat_features),
                            "status": "passed",
                        }
                    )

    strength = pd.DataFrame(strength_frames)
    btc_strength = strength[strength["asset"] == "BTC"].copy()
    eth_strength = strength[strength["asset"] == "ETH"].copy()
    block_delta = pd.DataFrame(block_frames)
    conventional_partial = pd.DataFrame(partial_frames)
    rolling = rolling_tradfi_exposures(tradfi_daily)
    regimes = exposure_regime_comparison(block_delta)
    multicollinearity = pd.DataFrame(multi_frames)
    ridge = pd.DataFrame(ridge_frames)
    fdr = pd.DataFrame(fdr_frames)
    frequency = pd.DataFrame(freq_frames)

    outputs.update(
        {
            "btc_ex_mvrv_feature_strength": btc_strength,
            "eth_feature_strength": eth_strength,
            "block_delta_r2": block_delta,
            "conventional_partial_r2": conventional_partial,
            "rolling_tradfi_exposures": rolling,
            "rolling_exposures": rolling,
            "rolling_exposure_summary": rolling.groupby(["asset", "feature_id", "window_days"], dropna=False).agg(
                beta_count=("beta", "count"),
                beta_median=("beta", "median"),
                beta_mean=("beta", "mean"),
                beta_std=("beta", "std"),
                correlation_median=("correlation", "median"),
                sample_count_median=("sample_count", "median"),
            ).reset_index() if not rolling.empty else pd.DataFrame(),
            "exposure_regime_comparison": regimes,
            "multicollinearity_diagnostics": multicollinearity,
            "ridge_stability": ridge,
            "fdr_adjusted_inference": fdr,
            "frequency_robustness": frequency,
        }
    )
    for name, frame in outputs.items():
        write_csv(p.tables / f"{name}.csv", frame)
    return outputs


def multicollinearity_rows(
    asset: str,
    frequency: str,
    x: pd.DataFrame,
    model_family: str = "",
    regime: str = "",
    row_index_hash: str = "",
    calendar: str = "",
    calendar_assumption: str = "",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    clean = x.replace([np.inf, -np.inf], np.nan).dropna()
    if clean.empty:
        return rows
    arr = clean.to_numpy()
    cond = float(np.linalg.cond(arr)) if arr.shape[0] > arr.shape[1] else np.nan
    corr = clean.corr().abs()
    for feature in clean.columns:
        others = [col for col in clean.columns if col != feature]
        vif = np.nan
        if others:
            y = clean[feature]
            regressors = sm.add_constant(clean[others], has_constant="add")
            res = sm.OLS(y, regressors).fit()
            vif = 1 / max(1e-12, 1 - float(res.rsquared))
        rows.append(
            {
                "asset": asset.upper(),
                "frequency": frequency,
                "model_family": model_family,
                "regime": regime,
                "feature_id": feature,
                "n": int(len(clean)),
                "row_index_hash": row_index_hash,
                "calendar": calendar,
                "calendar_assumption": calendar_assumption,
                "vif": vif,
                "condition_number": cond,
                "max_abs_pairwise_corr": corr[feature].drop(feature, errors="ignore").max(),
                "correlation_cluster": "high_corr" if corr[feature].drop(feature, errors="ignore").max() >= 0.75 else "not_high_corr",
            }
        )
    return rows


def ridge_stability_rows(
    asset: str,
    frequency: str,
    y: pd.Series,
    x: pd.DataFrame,
    model_family: str = "",
    regime: str = "",
    row_index_hash: str = "",
    calendar: str = "",
    calendar_assumption: str = "",
) -> list[dict[str, Any]]:
    df = pd.concat([y.rename("target"), x], axis=1).replace([np.inf, -np.inf], np.nan).dropna()
    if len(df) < 40:
        return []
    xmat = df[x.columns].to_numpy(dtype=float)
    yvec = df["target"].to_numpy(dtype=float)
    rows = []
    identity = np.eye(xmat.shape[1])
    for alpha in [0.1, 1.0, 10.0, 100.0]:
        beta = np.linalg.pinv(xmat.T @ xmat + alpha * identity) @ xmat.T @ yvec
        ranks = pd.Series(np.abs(beta), index=x.columns).rank(ascending=False, method="min")
        for feature, coef in zip(x.columns, beta, strict=True):
            rows.append(
                {
                    "asset": asset.upper(),
                    "frequency": frequency,
                    "model_family": model_family,
                    "regime": regime,
                    "alpha": alpha,
                    "feature_id": feature,
                    "n": int(len(df)),
                    "row_index_hash": row_index_hash,
                    "calendar": calendar,
                    "calendar_assumption": calendar_assumption,
                    "ridge_coef": float(coef),
                    "sign": "positive" if coef > 0 else "negative" if coef < 0 else "zero",
                    "abs_rank": int(ranks[feature]),
                }
            )
    return rows


def rolling_tradfi_exposures(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    features = available_features(daily, [f for values in tradfi_contemporaneous_blocks().values() for f in values], min_obs=120)
    calendar = panel_calendar_value(daily, "calendar")
    calendar_assumption = panel_calendar_value(daily, "calendar_assumption")
    close_time_assumption = panel_calendar_value(daily, "close_time_assumption")
    for asset, target in [("BTC", "btc_ret"), ("ETH", "eth_ret")]:
        for window in [180, 365]:
            for idx in range(window, len(daily), 14):
                chunk = daily.iloc[idx - window : idx]
                for feature in features:
                    df = chunk[[target, feature]].replace([np.inf, -np.inf], np.nan).dropna()
                    if len(df) < window * 0.55 or df[feature].var() == 0:
                        continue
                    beta = float(np.cov(df[target], df[feature])[0, 1] / np.var(df[feature]))
                    corr = float(df[target].corr(df[feature]))
                    rows.append(
                        {
                            "date": daily.index[idx].date().isoformat(),
                            "asset": asset,
                            "window_days": window,
                            "feature_id": feature,
                            "feature_label": clean_label(feature),
                            "beta": beta,
                            "correlation": corr,
                            "sample_count": int(len(df)),
                            "n": int(len(df)),
                            "timing": "contemporaneous",
                            "calendar": calendar,
                            "calendar_assumption": calendar_assumption,
                            "close_time_assumption": close_time_assumption,
                        }
                    )
    return pd.DataFrame(rows)


def exposure_regime_comparison(block: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if block.empty:
        return pd.DataFrame(rows)
    subset = block[
        block["model_family"].eq("long_sample_contemporaneous_exposure")
        & block["frequency"].eq("daily")
        & block["regime"].isin(["full_common_sample", "pre_btc_etf", "btc_etf_era"])
    ]
    for (asset, regime), group in subset.groupby(["asset", "regime"], dropna=False):
        rows.append(
            {
                "asset": asset,
                "regime": regime,
                "n": int(group["n"].max()),
                "r2": float(group["full_r2"].max()),
                "feature_count": len(str(group["feature_list"].iloc[0]).split("|")) if not group.empty else 0,
                "calendar": str(group["calendar"].iloc[0]) if "calendar" in group else "",
                "calendar_assumption": str(group["calendar_assumption"].iloc[0]) if "calendar_assumption" in group else "",
                "method_note": "Contemporaneous TradFi exposure model, descriptive regime split.",
            }
        )
    return pd.DataFrame(rows)


def mvrv_tables(daily: pd.DataFrame, p: BuildPaths) -> dict[str, pd.DataFrame]:
    audit_rows = []
    sub = daily[
        [
            "btc_ret",
            "d_log_mvrv",
            "d_log_market_cap",
            "d_log_realized_cap",
            "identity_residual",
            "btc_market_cap_usd",
            "btc_realized_cap_usd",
            "btc_mvrv",
        ]
    ].copy()
    clean = sub.replace([np.inf, -np.inf], np.nan).dropna(subset=["btc_ret", "d_log_mvrv"])
    residual = sub["identity_residual"].replace([np.inf, -np.inf], np.nan).dropna()
    same_day = fit_hac_ols(clean["btc_ret"], clean[["d_log_mvrv"]], 5)
    median_abs_ret = clean["btc_ret"].abs().median()
    residual_abs_median = residual.abs().median()
    relative_residual = residual_abs_median / median_abs_ret if median_abs_ret and np.isfinite(median_abs_ret) else np.nan
    audit_rows.extend(
        [
            {"metric": "corr_btc_return_d_log_mvrv", "value": clean["btc_ret"].corr(clean["d_log_mvrv"]), "n": len(clean), "interpretation": "Same-day BTC return and d-log MVRV correlation; diagnostic, not an independent factor."},
            {"metric": "same_day_mvrv_r2_diagnostic", "value": same_day["r2"], "n": same_day["n"], "interpretation": "HAC OLS diagnostic R-squared; same-day MVRV remains excluded from primary exposure models."},
            {"metric": "identity_residual_mean", "value": residual.mean(), "n": int(residual.notna().sum()), "interpretation": "Mean residual from d_log_mvrv - (d_log_market_cap - d_log_realized_cap), same date interval."},
            {"metric": "identity_residual_abs_median", "value": residual_abs_median, "n": int(residual.notna().sum()), "interpretation": "Median absolute identity residual; interpret only against the reported return-scale comparison."},
            {"metric": "identity_residual_abs_median_to_median_abs_btc_return", "value": relative_residual, "n": int(residual.notna().sum()), "interpretation": "Scale comparison: residual median absolute value divided by median absolute BTC return."},
            {"metric": "identity_residual_q01", "value": residual.quantile(0.01), "n": int(residual.notna().sum()), "interpretation": "Identity residual lower-tail quantile."},
            {"metric": "identity_residual_q05", "value": residual.quantile(0.05), "n": int(residual.notna().sum()), "interpretation": "Identity residual lower quantile."},
            {"metric": "identity_residual_q50", "value": residual.quantile(0.50), "n": int(residual.notna().sum()), "interpretation": "Identity residual median."},
            {"metric": "identity_residual_q95", "value": residual.quantile(0.95), "n": int(residual.notna().sum()), "interpretation": "Identity residual upper quantile."},
            {"metric": "identity_residual_q99", "value": residual.quantile(0.99), "n": int(residual.notna().sum()), "interpretation": "Identity residual upper-tail quantile."},
        ]
    )
    for feature in ["btc_nupl_lag1", "btc_supply_profit_pct_lag1", "btc_realized_price_gap_lag1"]:
        if feature in daily:
            valid = daily[["btc_ret", feature]].dropna()
            audit_rows.append(
                {"metric": f"corr_{feature}_btc_return", "value": valid["btc_ret"].corr(valid[feature]), "n": len(valid), "interpretation": "Related holder-profit state measure; not exogenous return factor."}
            )
    audit = pd.DataFrame(audit_rows)
    points = sub.reset_index().rename(columns={"index": "date"})
    points["date"] = pd.to_datetime(points["date"]).dt.date.astype(str)
    points["identity_convention_caveat"] = "MVRV, market cap, and realized cap are provider-exported series; source timing/conventions can leave residuals even when intervals are aligned."
    regime = daily.groupby("btc_mvrv_quintile_lagged", dropna=True).agg(
        n=("btc_ret_fwd_7d", "count"),
        next_week_return_mean=("btc_ret_fwd_7d", "mean"),
        next_day_return_mean=("btc_ret_fwd_1d", "mean"),
        realized_vol_30d_median=("btc_realized_vol_30d", "median"),
        future_30d_min_drawdown_median=("btc_future_30d_min_drawdown", "median"),
        funding_z_median=("btc_funding_z", "median"),
        leverage_percentile_median=("btc_leverage_ratio_percentile", "median"),
    ).reset_index().rename(columns={"btc_mvrv_quintile_lagged": "mvrv_state_quintile"})
    state = daily[["btc_mvrv", "btc_mvrv_lag1", "btc_mvrv_percentile_lagged", "btc_mvrv_z_365_lagged", "btc_realized_price_gap_lag1", "btc_mvrv_quintile_lagged"]].dropna(how="all").reset_index()
    write_csv(p.tables / "mvrv_mechanical_link_audit.csv", audit)
    write_csv(p.tables / "mvrv_identity_points.csv", points)
    write_csv(p.tables / "onchain_state_regimes.csv", state)
    write_csv(p.tables / "mvrv_regime_outcomes.csv", regime)
    return {"mvrv_mechanical_link_audit": audit, "mvrv_identity_points": points, "onchain_state_regimes": state, "mvrv_regime_outcomes": regime}


def leverage_tables(daily: pd.DataFrame, p: BuildPaths) -> dict[str, pd.DataFrame]:
    daily = daily.copy()
    features = [
        "btc_oi_to_mcap_growth_lag1",
        "btc_funding_z_lag1",
        "btc_leverage_ratio_percentile_lag1",
        "btc_basis_z",
        "btc_total_liq_to_lag_oi_pct",
        "btc_total_liq_to_lag_mcap_bps",
        "btc_taker_buy_ratio",
    ]
    registry = pd.DataFrame(
        [
            {
                "feature_id": feature,
                "clean_label": clean_label(feature),
                "frequency": "daily",
                "timing": "lagged state for *_lag1 features; same-day stress signature for liquidation ratios",
                "scaling": (
                    "liquidation_usd / prior-day open interest expressed as percent; "
                    "liquidation_usd / prior-day market cap expressed as basis points"
                    if "liq" in feature
                    else "see feature label"
                ),
                "denominator": (
                    "prior-day open interest or prior-day BTC market cap"
                    if "liq" in feature
                    else ""
                ),
            }
            for feature in features
            if feature in daily
        ]
    )
    daily["leverage_state_quintile"] = pd.qcut(daily["btc_leverage_ratio_percentile_lag1"], 5, labels=["Q1 low", "Q2", "Q3", "Q4", "Q5 high"], duplicates="drop")
    state = daily.groupby("leverage_state_quintile", dropna=True).agg(
        n=("btc_ret", "count"),
        realized_vol_30d_median=("btc_realized_vol_30d", "median"),
        abs_return_next_day_mean=("btc_ret_fwd_1d", lambda s: s.abs().mean()),
        bottom5_rate=("btc_bottom5", "mean"),
        same_day_liq_to_lag_oi_pct_median=("btc_total_liq_to_lag_oi_pct", "median"),
        same_day_liq_to_lag_mcap_bps_median=("btc_total_liq_to_lag_mcap_bps", "median"),
        funding_z_lag1_median=("btc_funding_z_lag1", "median"),
    ).reset_index().rename(columns={"leverage_state_quintile": "leverage_state"})

    model_rows = []
    lag_features = available_features(daily, ["btc_oi_to_mcap_growth_lag1", "btc_funding_z_lag1", "btc_leverage_ratio_percentile_lag1", "btc_basis_z"])
    if lag_features:
        df = pd.concat([daily["btc_bottom5"].rename("target"), daily[lag_features]], axis=1).replace([np.inf, -np.inf], np.nan).dropna()
        if len(df) >= 100 and df["target"].nunique() > 1:
            try:
                logit = sm.Logit(df["target"], sm.add_constant(df[lag_features], has_constant="add")).fit(disp=False)
                for feature in lag_features:
                    model_rows.append(
                        {
                            "model": "lagged_logit_bottom5",
                            "feature_id": feature,
                            "n": len(df),
                            "coef": logit.params.get(feature, np.nan),
                            "z_stat": logit.tvalues.get(feature, np.nan),
                            "p_value": logit.pvalues.get(feature, np.nan),
                            "class_balance": df["target"].mean(),
                            "interpretation": "Lagged leverage-state association with bottom-5pct BTC return days.",
                        }
                    )
            except Exception as exc:
                model_rows.append({"model": "lagged_logit_bottom5", "feature_id": "", "n": len(df), "coef": np.nan, "z_stat": np.nan, "p_value": np.nan, "class_balance": df["target"].mean(), "interpretation": f"skipped:{type(exc).__name__}"})
    tail = pd.DataFrame(model_rows)
    top_events = daily.nlargest(12, "btc_total_liq_usd")[
        [
            "btc_ret",
            "btc_realized_vol_30d",
            "btc_total_liq_usd",
            "btc_total_liq_to_lag_oi_pct",
            "btc_total_liq_to_lag_mcap_bps",
            "btc_funding_z_lag1",
        ]
    ].reset_index()
    top_events["event_id"] = [f"top_liquidation_{i + 1:02d}" for i in range(len(top_events))]
    top_events = top_events.rename(columns={"date": "event_date", "btc_ret": "same_day_btc_return"})
    post_returns = []
    for _, row in top_events.iterrows():
        event_date = pd.Timestamp(row["event_date"])
        loc = daily.index.get_loc(event_date)
        if isinstance(loc, slice):
            loc = loc.start
        post_returns.append(
            {
                "event_id": row["event_id"],
                "post_3d_return_plus1_to_plus3": daily.iloc[loc + 1 : loc + 4]["btc_ret"].sum(),
                "post_10d_return_plus1_to_plus10": daily.iloc[loc + 1 : loc + 11]["btc_ret"].sum(),
                "post_window_convention": "+1 through +10 excludes the same-day liquidation signature",
            }
        )
    post_response = pd.DataFrame(post_returns)
    top_events = top_events.merge(post_response, on="event_id", how="left")
    top_events["note"] = "Same-day liquidation signature with separate post-event response; not evidence that liquidation initiated the move."
    summary = state.copy()
    summary["method_note"] = "Lagged leverage/funding/OI state is separated from same-day liquidation signatures and post-event response."
    write_csv(p.tables / "leverage_feature_registry.csv", registry)
    write_csv(p.tables / "leverage_state_summary.csv", state)
    write_csv(p.tables / "tail_risk_models.csv", tail)
    write_csv(p.tables / "liquidation_event_responses.csv", top_events)
    write_csv(p.tables / "leverage_tail_risk_summary.csv", summary)
    return {"leverage_state_summary": state, "tail_risk_models": tail, "liquidation_event_responses": top_events, "leverage_tail_risk_summary": summary}


def etf_tables(daily: pd.DataFrame, etf_daily: pd.DataFrame, p: BuildPaths) -> dict[str, pd.DataFrame]:
    timing = []
    for asset in ["btc", "eth"]:
        flow_col = f"{asset}_etf_net_flow_usd"
        valid = daily[flow_col].dropna()
        timing.append(
            {
                "asset": asset.upper(),
                "first_flow_date": valid.index.min().date().isoformat() if not valid.empty else "",
                "last_flow_date": valid.index.max().date().isoformat() if not valid.empty else "",
                "observations": int(len(valid)),
                "nonzero_observations": int((valid != 0).sum()),
                "calendar": panel_calendar_value(etf_daily, "calendar"),
                "calendar_assumption": panel_calendar_value(etf_daily, "calendar_assumption"),
                "timing_note": "Farside daily issuer aggregates; holidays/non-reporting days are not treated as zero unless source reports zero.",
            }
        )
    assoc_rows = []
    for asset in ["btc", "eth"]:
        ret = etf_daily[f"{asset}_ret"]
        vol = etf_daily[f"{asset}_realized_vol_30d"] if f"{asset}_realized_vol_30d" in etf_daily else daily[f"{asset}_realized_vol_30d"].reindex(etf_daily.index)
        for lag, flow_col in [(0, f"{asset}_etf_flow_intensity_lag0"), (1, f"{asset}_etf_flow_intensity_lag1")]:
            flow = etf_daily[flow_col]
            ret_df = pd.concat([ret, flow.rename("flow")], axis=1).dropna()
            vol_df = pd.concat([vol, flow.rename("flow")], axis=1).dropna()
            assoc_rows.append(
                {
                    "asset": asset.upper(),
                    "flow_lag_days": lag,
                    "flow_feature": flow_col,
                    "return_corr": ret_df.iloc[:, 0].corr(ret_df["flow"]) if len(ret_df) else np.nan,
                    "volatility_corr": vol_df.iloc[:, 0].corr(vol_df["flow"]) if len(vol_df) else np.nan,
                    "n_return": len(ret_df),
                    "n_volatility": len(vol_df),
                    "calendar": panel_calendar_value(etf_daily, "calendar"),
                    "calendar_assumption": panel_calendar_value(etf_daily, "calendar_assumption"),
                    "close_time_assumption": panel_calendar_value(etf_daily, "close_time_assumption"),
                    "lag_convention": "lag 0 is current ETF trading-date reported flow intensity; lag 1 is prior ETF trading-date flow intensity",
                    "language": "association_grid_not_causal",
                }
            )
    shock = []
    for asset in ["btc", "eth"]:
        flow = daily[f"{asset}_etf_flow_intensity_lag0"]
        threshold = flow.abs().quantile(0.95)
        days = daily.loc[flow.abs() >= threshold, [f"{asset}_etf_net_flow_usd", f"{asset}_ret", f"{asset}_realized_vol_30d"]].copy()
        days = days.reset_index().tail(25)
        days["asset"] = asset.upper()
        shock.append(days)
    shock_days = pd.concat(shock, ignore_index=True) if shock else pd.DataFrame()
    absorption = daily[["btc_etf_cumulative_flow_usd", "eth_etf_cumulative_flow_usd", "btc_mcap_lag1", "eth_mcap_lag1"]].copy()
    absorption["btc_cum_flow_to_lag_mcap"] = absorption["btc_etf_cumulative_flow_usd"] / absorption["btc_mcap_lag1"]
    absorption["eth_cum_flow_to_lag_mcap"] = absorption["eth_etf_cumulative_flow_usd"] / absorption["eth_mcap_lag1"]
    absorption = absorption.reset_index()
    block_path = p.tables / "block_delta_r2.csv"
    if block_path.exists():
        era = pd.read_csv(block_path)
        era = era[era["model_family"].eq("etf_era_augmented")].copy()
    else:
        era = pd.DataFrame()
    summary = pd.DataFrame(
        [
            {
                "question": "BTC ETF market plumbing",
                "key_metric": "latest cumulative flow / lagged BTC mcap",
                "value": absorption["btc_cum_flow_to_lag_mcap"].dropna().iloc[-1] if absorption["btc_cum_flow_to_lag_mcap"].notna().any() else np.nan,
                "sample": "BTC ETF era",
                "calendar": panel_calendar_value(etf_daily, "calendar"),
                "interpretation": "Descriptive absorption ratio, not valuation model.",
            },
            {
                "question": "ETH ETF market plumbing",
                "key_metric": "latest cumulative flow / lagged ETH mcap",
                "value": absorption["eth_cum_flow_to_lag_mcap"].dropna().iloc[-1] if absorption["eth_cum_flow_to_lag_mcap"].notna().any() else np.nan,
                "sample": "ETH ETF era",
                "calendar": panel_calendar_value(etf_daily, "calendar"),
                "interpretation": "Descriptive absorption ratio, not valuation model.",
            },
        ]
    )
    write_csv(p.tables / "etf_data_timing_audit.csv", pd.DataFrame(timing))
    write_csv(p.tables / "etf_flow_associations.csv", pd.DataFrame(assoc_rows))
    write_csv(p.tables / "etf_flow_shock_days.csv", shock_days)
    write_csv(p.tables / "etf_absorption_metrics.csv", absorption)
    write_csv(p.tables / "etf_era_exposure_comparison.csv", era)
    write_csv(p.tables / "etf_market_plumbing_summary.csv", summary)
    return {"etf_market_plumbing_summary": summary, "etf_flow_associations": pd.DataFrame(assoc_rows), "etf_absorption_metrics": absorption}


def valuation_contamination_audit(daily: pd.DataFrame, weekly: pd.DataFrame, p: BuildPaths) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for asset in ["btc", "eth"]:
        ret_col = f"{asset}_ret"
        tvl_col = "valuation_sensitive_defi_tvl_growth"
        tvl_df = weekly[[ret_col, tvl_col]].replace([np.inf, -np.inf], np.nan).dropna()
        rows.append(
            {
                "feature_id": tvl_col,
                "asset": asset.upper(),
                "audit_scope": "same-week raw USD TVL price-content screen",
                "frequency": "weekly",
                "calendar": panel_calendar_value(weekly, "calendar"),
                "n": len(tvl_df),
                "correlation_with_return": tvl_df[ret_col].corr(tvl_df[tvl_col]) if len(tvl_df) else np.nan,
                "unit_disposition": "USD TVL embeds asset-price effects; label as valuation-sensitive DeFi balance-sheet proxy.",
                "mechanical_link_risk": "high_usd_price_content",
                "preferred_public_language": "valuation-sensitive DeFi balance-sheet proxy",
                "prohibited_public_language": "pure capital inflow; exogenous liquidity shock",
            }
        )
        raw_oi = f"{asset}_oi_growth"
        ratio_oi = f"{asset}_oi_to_mcap_growth"
        for feature, disposition, risk in [
            (raw_oi, "Raw OI growth is retained for audit only when OI is USD/notional-valued.", "medium_if_usd_notional"),
            (ratio_oi, "OI/market-cap growth is preferred as the price-scaled OI state measure.", "lower_after_mcap_scaling"),
        ]:
            if feature not in daily:
                continue
            oi_df = daily[[ret_col, feature]].replace([np.inf, -np.inf], np.nan).dropna()
            rows.append(
                {
                    "feature_id": feature,
                    "asset": asset.upper(),
                    "audit_scope": "open-interest unit and price-content screen",
                    "frequency": "daily",
                    "calendar": panel_calendar_value(daily, "calendar"),
                    "n": len(oi_df),
                    "correlation_with_return": oi_df[ret_col].corr(oi_df[feature]) if len(oi_df) else np.nan,
                    "unit_disposition": disposition + " CryptoQuant OI unit is treated as USD/notional unless provider metadata prove otherwise.",
                    "mechanical_link_risk": risk,
                    "preferred_public_language": "lagged OI/market-cap leverage-state association",
                    "prohibited_public_language": "pure leverage expansion independent of price",
                }
            )
    audit = pd.DataFrame(rows)
    write_csv(p.tables / "valuation_contamination_audit.csv", audit)
    return audit


def liquidity_tables(weekly: pd.DataFrame, p: BuildPaths) -> dict[str, pd.DataFrame]:
    features = weekly[
        [
            "stablecoin_supply_usd",
            "stablecoin_supply_growth",
            "defi_tvl_usd",
            "valuation_sensitive_defi_tvl_growth",
            "stablecoin_to_tvl",
            "btc_ret",
            "eth_ret",
            "btc_realized_vol_30d",
            "calendar",
            "calendar_assumption",
        ]
    ].copy()
    features = features.reset_index()
    features["date"] = pd.to_datetime(features["date"]).dt.date.astype(str)
    defifeat = features[["date", "defi_tvl_usd", "valuation_sensitive_defi_tvl_growth"]].copy()
    quantiles = pd.qcut(weekly["stablecoin_supply_growth"], 3, labels=["contraction/low", "middle", "expansion/high"], duplicates="drop")
    regime = weekly.assign(liquidity_regime=quantiles).groupby("liquidity_regime", dropna=True).agg(
        n=("btc_ret", "count"),
        stable_growth_mean=("stablecoin_supply_growth", "mean"),
        btc_return_mean=("btc_ret", "mean"),
        eth_return_mean=("eth_ret", "mean"),
        btc_vol_median=("btc_realized_vol_30d", "median"),
        stablecoin_to_tvl_median=("stablecoin_to_tvl", "median"),
    ).reset_index()
    assoc_rows = []
    for lhs in ["stablecoin_supply_growth", "valuation_sensitive_defi_tvl_growth", "stablecoin_to_tvl"]:
        for rhs in ["btc_ret", "eth_ret", "btc_realized_vol_30d"]:
            df = weekly[[lhs, rhs]].dropna()
            assoc_rows.append(
                {
                    "liquidity_feature": lhs,
                    "outcome": rhs,
                    "frequency": "weekly",
                    "calendar": panel_calendar_value(weekly, "calendar"),
                    "calendar_assumption": panel_calendar_value(weekly, "calendar_assumption"),
                    "n": len(df),
                    "correlation": df[lhs].corr(df[rhs]) if len(df) else np.nan,
                    "mechanical_link_risk": "high_usd_price_content" if "tvl" in lhs else "low",
                    "language": "descriptive_state_proxy_not_shock",
                }
            )
    assoc = pd.DataFrame(assoc_rows)
    summary = regime.copy()
    summary["calendar"] = panel_calendar_value(weekly, "calendar")
    summary["calendar_assumption"] = panel_calendar_value(weekly, "calendar_assumption")
    summary["method_note"] = "Sunday-ended crypto weekly aggregation; stablecoin supply is cleaner than raw USD TVL, while TVL is valuation-sensitive."
    write_csv(p.tables / "stablecoin_liquidity_features.csv", features)
    write_csv(p.tables / "defi_activity_features.csv", defifeat)
    write_csv(p.tables / "liquidity_regime_summary.csv", regime)
    write_csv(p.tables / "liquidity_associations.csv", assoc)
    write_csv(p.tables / "stablecoin_defi_liquidity_summary.csv", summary)
    return {"stablecoin_defi_liquidity_summary": summary, "liquidity_associations": assoc}


def selected_major_tables(root: Path, p: BuildPaths) -> dict[str, pd.DataFrame]:
    path = provider_root(root, "market_structure") / "DefiLlama/crypto_constituents_daily_ohlcv_top50_current_2020_2026.csv"
    daily = pd.read_csv(path, parse_dates=["date"])
    asset_by_key = {str(asset["asset_key"]).lower(): asset for asset in SELECTED_ASSETS}
    selected_keys = set(asset_by_key)
    daily["canonical_key"] = daily["coingecko_id"].astype(str).str.lower()
    subset = daily[daily["canonical_key"].isin(selected_keys)].copy()
    subset["canonical_symbol"] = subset["canonical_key"].map(lambda key: str(asset_by_key[key]["symbol"]))
    subset["canonical_name"] = subset["canonical_key"].map(lambda key: str(asset_by_key[key]["name"]))
    subset["source_symbol"] = subset["symbol"]
    subset["ret"] = subset.groupby("canonical_key")["close_usd"].transform(log_return)
    coverage = subset.groupby(["canonical_symbol", "canonical_name", "canonical_key"], dropna=False).agg(
        source_symbols=("source_symbol", lambda s: "|".join(sorted(set(map(str, s))))),
        first_valid_date=("date", "min"),
        last_valid_date=("date", "max"),
        observations=("close_usd", "count"),
    ).reset_index()
    coverage = coverage.rename(columns={"canonical_symbol": "symbol", "canonical_key": "coingecko_id"})
    coverage["first_valid_date"] = coverage["first_valid_date"].dt.date.astype(str)
    coverage["last_valid_date"] = coverage["last_valid_date"].dt.date.astype(str)
    coverage["coverage_note"] = np.where(
        coverage["symbol"] == "HYPE",
        "Short-history asset; do not compare as full-cycle history.",
        "Current daily constituent coverage begins 2022-12-31/2023 for most selected assets; use comparable-window metrics for cross-asset comparisons.",
    )
    ton_mask = coverage["symbol"].eq("TON")
    coverage.loc[ton_mask, "coverage_note"] = (
        "Sourced by canonical coingecko_id coingecko:the-open-network; local source symbol is "
        + coverage.loc[ton_mask, "source_symbols"].astype(str)
        + "."
    )
    missing_rows = []
    present = set(coverage["coingecko_id"].astype(str).str.lower())
    for asset in SELECTED_ASSETS:
        canonical_key = str(asset["asset_key"]).lower()
        if canonical_key not in present:
            missing_rows.append(
                {
                    "symbol": asset["symbol"],
                    "canonical_name": asset["name"],
                    "coingecko_id": f"coingecko:{asset['coingecko_id']}",
                    "source_symbols": "",
                    "first_valid_date": "",
                    "last_valid_date": "",
                    "observations": 0,
                    "coverage_note": "Skipped: requested selected major is not present in the current daily constituent source.",
                }
            )
    if missing_rows:
        coverage = pd.concat([coverage, pd.DataFrame(missing_rows)], ignore_index=True)
    risk_rows = []
    btc = subset[subset["canonical_symbol"] == "BTC"].set_index("date")["ret"]
    eth = subset[subset["canonical_symbol"] == "ETH"].set_index("date")["ret"]
    qqq = log_return(load_close(provider_root(root, "tradingview") / "Daily/QQQ_nasdaq100_etf__daily.csv", "qqq_close"))
    for symbol, group in subset.groupby("canonical_symbol"):
        series = group.set_index("date")["ret"].dropna()
        price = group.set_index("date")["close_usd"].dropna()
        if series.empty:
            continue
        dd = price / price.cummax() - 1
        source_symbols = "|".join(sorted(group["source_symbol"].astype(str).unique()))
        risk_rows.append(
            {
                "symbol": symbol,
                "canonical_name": group["canonical_name"].iloc[0],
                "source_symbols": source_symbols,
                "n": len(series),
                "first_date": series.index.min().date().isoformat(),
                "last_date": series.index.max().date().isoformat(),
                "annualized_volatility": series.std() * math.sqrt(365),
                "downside_volatility": series[series < 0].std() * math.sqrt(365),
                "max_drawdown": dd.min(),
                "positive_week_share": (series.resample("W-SUN").sum() > 0).mean(),
                "short_history_flag": symbol == "HYPE",
            }
        )
    for asset in SELECTED_ASSETS:
        if asset["symbol"] not in {row["symbol"] for row in risk_rows}:
            risk_rows.append(
                {
                    "symbol": asset["symbol"],
                    "canonical_name": asset["name"],
                    "source_symbols": "",
                    "n": 0,
                    "first_date": "",
                    "last_date": "",
                    "annualized_volatility": np.nan,
                    "downside_volatility": np.nan,
                    "max_drawdown": np.nan,
                    "positive_week_share": np.nan,
                    "short_history_flag": asset["symbol"] == "HYPE",
                    "status": "skipped_insufficient_data",
                }
            )
    risk = pd.DataFrame(risk_rows)
    if "status" not in risk:
        risk["status"] = "computed"
    risk["status"] = risk["status"].fillna("computed")
    beta_rows = []
    for symbol, group in subset.groupby("canonical_symbol"):
        series = group.set_index("date")["ret"].dropna()
        for bench_name, bench in [("BTC", btc), ("ETH", eth), ("QQQ", qqq)]:
            df = pd.concat([series.rename("asset"), bench.rename("bench")], axis=1).dropna()
            if len(df) < 60 or df["bench"].var() == 0:
                beta = np.nan
                corr = np.nan
            else:
                beta = float(np.cov(df["asset"], df["bench"])[0, 1] / np.var(df["bench"]))
                corr = df["asset"].corr(df["bench"])
            beta_rows.append({"symbol": symbol, "benchmark": bench_name, "n": len(df), "beta": beta, "correlation": corr})
    betas = pd.DataFrame(beta_rows)
    comparable_rows = []
    available_returns = {
        symbol: group.set_index("date")["ret"].dropna()
        for symbol, group in subset.groupby("canonical_symbol")
        if group["ret"].notna().sum() >= 60
    }
    if available_returns:
        common_start = max(series.index.min() for series in available_returns.values())
        common_end = min(series.index.max() for series in available_returns.values())
        for symbol, series in available_returns.items():
            window = series.loc[(series.index >= common_start) & (series.index <= common_end)].dropna()
            if len(window) < 60:
                continue
            prices = subset[subset["canonical_symbol"] == symbol].set_index("date")["close_usd"].loc[window.index].dropna()
            drawdown = prices / prices.cummax() - 1
            comparable_rows.append(
                {
                    "symbol": symbol,
                    "common_start": common_start.date().isoformat(),
                    "common_end": common_end.date().isoformat(),
                    "n": int(len(window)),
                    "annualized_volatility": window.std() * math.sqrt(365),
                    "max_drawdown": drawdown.min(),
                    "positive_week_share": (window.resample("W-SUN").sum() > 0).mean(),
                    "coverage_note": "Comparable-window metrics use the common date range across available selected canonical assets.",
                }
            )
    comparable = pd.DataFrame(comparable_rows)
    panel_summary, chain_assoc = chain_fundamentals(root)
    write_csv(p.tables / "selected_major_coverage.csv", coverage)
    write_csv(p.tables / "selected_major_risk_metrics.csv", risk)
    write_csv(p.tables / "selected_major_comparable_window_metrics.csv", comparable)
    write_csv(p.tables / "selected_major_betas.csv", betas)
    write_csv(p.tables / "chain_fundamental_panel_summary.csv", panel_summary)
    write_csv(p.tables / "chain_activity_associations.csv", chain_assoc)
    return {"selected_major_risk_metrics": risk, "selected_major_comparable_window_metrics": comparable, "selected_major_betas": betas}


def chain_fundamentals(root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    artemis = provider_root(root, "artemis")
    metric_files = {
        "market_cap": artemis / "Chains - Market Cap.csv",
        "fees": artemis / "Chains - Fees.csv",
        "revenue": artemis / "Chains - Revenue.csv",
        "stablecoin_supply": artemis / "Chains - Stablecoin Supply.csv",
        "active_addresses_new": artemis / "Chains - Daily Active Addresses (New Wallets).csv",
    }
    rows = []
    assoc = []
    for metric, file in metric_files.items():
        if not file.exists():
            continue
        frame = pd.read_csv(file, parse_dates=["date"])
        chains = [col for col in frame.columns if col != "date"]
        for chain in chains:
            series = pd.to_numeric(frame[chain], errors="coerce").dropna()
            if len(series) < 30:
                continue
            rows.append({"metric": metric, "chain": chain, "observations": len(series), "first_date": frame.loc[series.index, "date"].min().date().isoformat(), "last_date": frame.loc[series.index, "date"].max().date().isoformat()})
    summary = pd.DataFrame(rows)
    if not summary.empty:
        summary["panel_status"] = np.where(summary.groupby("metric")["chain"].transform("nunique") >= 4, "adequate_for_descriptive_panel", "limited_coverage")
    assoc.append({"analysis": "chain_panel", "status": "descriptive_summary_only", "method_note": "Asset/week fixed-effects panel is deferred unless broad chain mapping and aligned asset returns are available."})
    return summary, pd.DataFrame(assoc)


def pit_tables(monthly: pd.DataFrame, p: BuildPaths) -> dict[str, pd.DataFrame]:
    monthly = monthly.reset_index(drop=True)
    top100 = monthly[monthly["in_full_top100"]].copy()
    composition = top100.groupby(["month", "asset_class_final"], dropna=False)["market_cap_usd"].sum().reset_index()
    totals = composition.groupby("month")["market_cap_usd"].transform("sum")
    composition["share"] = composition["market_cap_usd"] / totals
    month_meta = top100.groupby("month", dropna=False).agg(
        snapshot_date=("snapshot_date", "max"),
        is_partial_month=("is_partial_month", "max"),
    ).reset_index()
    composition = composition.merge(month_meta, on="month", how="left")
    composition["snapshot_date"] = pd.to_datetime(composition["snapshot_date"]).dt.date.astype(str)
    composition["is_partial_month"] = composition["is_partial_month"].astype(bool)
    composition["month"] = composition["month"].dt.to_period("M").astype(str)
    concentration_rows = []
    turnover_rows = []
    previous_assets: set[str] | None = None
    for month, group in top100.groupby("month"):
        group = group.sort_values("rank_full_market")
        total = group["market_cap_usd"].sum()
        shares = group["market_cap_usd"] / total
        assets = set(group["asset_key"])
        snapshot_date = pd.to_datetime(group["snapshot_date"]).max()
        is_partial = bool(group["is_partial_month"].fillna(False).astype(bool).any())
        concentration_rows.append(
            {
                "month": month.to_period("M").strftime("%Y-%m"),
                "snapshot_date": snapshot_date.date().isoformat(),
                "is_partial_month": is_partial,
                "snapshot_count": len(group),
                "top5_share": shares.head(5).sum(),
                "top10_share": shares.head(10).sum(),
                "hhi": float(np.square(shares).sum()),
                "btc_share": shares[group["symbol"].eq("BTC")].sum(),
                "eth_share": shares[group["symbol"].eq("ETH")].sum(),
                "stable_like_share": shares[group["asset_class_final"].eq("stable-like assets")].sum(),
                "productized_wrapped_share": shares[group["asset_class_final"].eq("productized/wrapped assets")].sum(),
                "clean_risk_count": int(group["asset_class_final"].isin(["BTC", "ETH", "selected majors ex BTC/ETH", "other risk assets"]).sum()),
            }
        )
        if previous_assets is not None:
            turnover_rows.append(
                {
                    "month": month.to_period("M").strftime("%Y-%m"),
                    "entries": len(assets - previous_assets),
                    "exits": len(previous_assets - assets),
                    "rank_persistence": len(assets & previous_assets) / max(len(assets), 1),
                }
            )
        previous_assets = assets
    concentration = pd.DataFrame(concentration_rows)
    turnover = pd.DataFrame(turnover_rows)
    periods = {
        "2020_halving_to_2021_cycle": ("2020-05-01", "2021-12-31"),
        "2022_stress": ("2022-01-01", "2022-12-31"),
        "2023_recovery": ("2023-01-01", "2023-12-31"),
        "btc_etf_access": ("2024-01-11", "2026-04-30"),
        "eth_etf_era": ("2024-07-23", "2026-04-30"),
    }
    period_rows = []
    conc_dates = pd.to_datetime(concentration["month"])
    for period, (start, end) in periods.items():
        sub = concentration[(conc_dates >= start) & (conc_dates <= end)]
        period_rows.append(
            {
                "period": period,
                "snapshot_count": len(sub),
                "top10_share_mean": sub["top10_share"].mean(),
                "hhi_mean": sub["hhi"].mean(),
                "stable_like_share_mean": sub["stable_like_share"].mean(),
                "method_note": "Descriptive period comparison; not attributed to one event.",
            }
        )
    period = pd.DataFrame(period_rows)
    summary = concentration.merge(turnover, on="month", how="left")
    write_csv(p.tables / "pit_market_structure_monthly.csv", top100.reset_index(drop=True))
    write_csv(p.tables / "pit_composition.csv", composition)
    write_csv(p.tables / "pit_concentration.csv", concentration)
    write_csv(p.tables / "pit_turnover.csv", turnover)
    write_csv(p.tables / "pit_period_comparison.csv", period)
    write_csv(p.tables / "pit_market_structure_summary.csv", summary)
    return {"pit_market_structure_summary": summary, "pit_composition": composition, "pit_concentration": concentration}


def event_tables(root: Path, daily: pd.DataFrame, p: BuildPaths) -> dict[str, pd.DataFrame]:
    events = load_events(root)
    response_rows = []
    inference_rows = []
    event_dates = [pd.Timestamp(item["date"]) for item in events.to_dict("records")]
    for event in events.to_dict("records"):
        date = pd.Timestamp(event["date"])
        for asset, ret_col, vol_col in [("BTC", "btc_ret", "btc_realized_vol_30d"), ("ETH", "eth_ret", "eth_realized_vol_30d")]:
            if date not in daily.index:
                nearest = daily.index[daily.index.get_indexer([date], method="nearest")[0]]
            else:
                nearest = date
            loc = daily.index.get_loc(nearest)
            if isinstance(loc, slice):
                loc = loc.start
            before = daily.iloc[max(0, loc - 10) : loc][ret_col].sum()
            post_slice = daily.iloc[loc + 1 : loc + 11][ret_col].dropna()
            after = post_slice.sum() if len(post_slice) == 10 else np.nan
            vol_change = daily.iloc[loc + 1 : loc + 11][vol_col].mean() - daily.iloc[max(0, loc - 10) : loc][vol_col].mean()
            response_rows.append(
                {
                    "event_id": event["event_id"],
                    "event_date": date.date().isoformat(),
                    "category": event["category"],
                    "asset": asset,
                    "window_days": 10,
                    "actual_observations": int(len(post_slice)),
                    "pre_window_return": before,
                    "post_window_return": after,
                    "post_window_convention": "+1 through +10, excluding event day",
                    "volatility_change": vol_change,
                    "metric_family": "return_volatility",
                    "language": "descriptive_event_window",
                }
            )
            inference_rows.append(empirical_placebo_event_row(daily[ret_col].dropna(), nearest, event_dates, event["event_id"], asset))
    response = pd.DataFrame(response_rows)
    inference = pd.DataFrame(inference_rows)
    cycle = cycle_state_summary(daily)
    write_csv(p.tables / "cycle_state_summary.csv", cycle)
    write_csv(p.tables / "event_atlas.csv", events)
    write_csv(p.tables / "event_response_matrix.csv", response)
    write_csv(p.tables / "event_inference.csv", inference)
    return {"event_response_matrix": response, "event_inference": inference}


def load_events(root: Path) -> pd.DataFrame:
    raw = yaml.safe_load((root / "config/events.yml").read_text(encoding="utf-8"))
    rows = []
    for item in raw.get("primary_breaks", []):
        rows.append({"event_id": item["id"], "date": item["date"], "category": "primary", "description": item.get("description", ""), "source": item.get("source", ""), "confidence": "pre_registered"})
    for item in raw.get("secondary_candidates", []):
        rows.append({"event_id": item["id"], "date": item["date"], "category": "secondary", "description": item.get("description", ""), "source": item.get("source", ""), "confidence": "exploratory"})
    return pd.DataFrame(rows)


def empirical_placebo_event_row(series: pd.Series, event_date: pd.Timestamp, event_dates: list[pd.Timestamp], event_id: str, asset: str) -> dict[str, Any]:
    if event_date not in series.index:
        event_date = series.index[series.index.get_indexer([event_date], method="nearest")[0]]
    loc = series.index.get_loc(event_date)
    if isinstance(loc, slice):
        loc = loc.start
    block = 10
    actual_window = series.iloc[loc + 1 : loc + 1 + block].dropna()
    actual = actual_window.sum() if len(actual_window) == block else np.nan
    if len(series) < 80 or len(actual_window) != block:
        return {
            "event_id": event_id,
            "asset": asset,
            "actual_post_10d_return": actual,
            "actual_observations": int(len(actual_window)),
            "block_size": block,
            "placebo_window_count": 0,
            "placebo_p_value": np.nan,
            "eligible_start_date": "",
            "eligible_end_date": "",
            "event_window_convention": "+1 through +10, excluding event day",
            "method": "skipped_insufficient_sample",
        }
    excluded_positions: set[int] = set()
    for raw_date in event_dates:
        nearest = series.index[series.index.get_indexer([raw_date], method="nearest")[0]]
        event_loc = series.index.get_loc(nearest)
        if isinstance(event_loc, slice):
            event_loc = event_loc.start
        excluded_positions.update(range(max(0, event_loc - block), min(len(series), event_loc + block + 1)))
    draws = []
    starts = []
    values = series.to_numpy()
    for start in range(0, len(series) - block + 1):
        window_positions = set(range(start, start + block))
        if window_positions & excluded_positions:
            continue
        window = values[start : start + block]
        if np.isfinite(window).sum() == block:
            starts.append(start)
            draws.append(float(np.sum(window)))
    draws_arr = np.array(draws, dtype=float)
    p_value = float((np.abs(draws_arr) >= abs(actual)).mean()) if len(draws_arr) else np.nan
    return {
        "event_id": event_id,
        "asset": asset,
        "actual_post_10d_return": actual,
        "actual_observations": int(len(actual_window)),
        "block_size": block,
        "placebo_window_count": int(len(draws_arr)),
        "placebo_p_value": p_value,
        "eligible_start_date": series.index[min(starts)].date().isoformat() if starts else "",
        "eligible_end_date": series.index[max(starts)].date().isoformat() if starts else "",
        "event_window_convention": "+1 through +10, excluding event day",
        "method": "empirical_placebo_window_test_nonoverlapping_registered_events",
    }


def cycle_state_summary(daily: pd.DataFrame) -> pd.DataFrame:
    halvings = [pd.Timestamp("2020-05-11"), pd.Timestamp("2024-04-20")]
    rows = []
    for date, row in daily.iterrows():
        halving = max([h for h in halvings if h <= date], default=halvings[0])
        rows.append(
            {
                "date": date.date().isoformat(),
                "halving_epoch_start": halving.date().isoformat(),
                "days_since_halving": int((date - halving).days),
                "btc_drawdown": row.get("btc_drawdown", np.nan),
                "mvrv_percentile_lagged": row.get("btc_mvrv_percentile_lagged", np.nan),
                "realized_vol_30d": row.get("btc_realized_vol_30d", np.nan),
                "btc_dominance": row.get("btc_dominance", np.nan),
                "stablecoin_growth": row.get("stablecoin_supply_growth", np.nan),
                "leverage_state": row.get("btc_leverage_ratio_percentile", np.nan),
            }
        )
    return pd.DataFrame(rows)


def robustness_tables(daily: pd.DataFrame, weekly: pd.DataFrame, p: BuildPaths) -> dict[str, pd.DataFrame]:
    block = pd.read_csv(p.tables / "block_delta_r2.csv") if (p.tables / "block_delta_r2.csv").exists() else pd.DataFrame()
    local_windows = []
    for feature in ["qqq_ret", "vix_d1", "btc_etf_flow_intensity_lag0", "stablecoin_supply_growth_lag1"]:
        df = daily[["btc_ret", feature]].dropna()
        if len(df) < 80:
            continue
        corr = df["btc_ret"].corr(df[feature])
        samples = []
        dates = []
        vals = df.to_numpy()
        for start in range(0, max(1, len(vals) - 20 + 1)):
            chunk = vals[start : start + 20]
            if chunk.shape[0] > 2:
                samples.append(np.corrcoef(chunk[:, 0], chunk[:, 1])[0, 1])
                dates.append(df.index[start + chunk.shape[0] - 1])
        local_windows.append(
            {
                "feature_id": feature,
                "full_sample_correlation": corr,
                "local_window_days": 20,
                "window_count": len(samples),
                "local_corr_p05": np.nanpercentile(samples, 5) if samples else np.nan,
                "local_corr_median": np.nanpercentile(samples, 50) if samples else np.nan,
                "local_corr_p95": np.nanpercentile(samples, 95) if samples else np.nan,
                "first_window_end": min(dates).date().isoformat() if dates else "",
                "last_window_end": max(dates).date().isoformat() if dates else "",
                "method": "distribution_of_overlapping_20_day_local_window_correlations_not_bootstrap_ci",
            }
        )
    local_window_df = pd.DataFrame(local_windows)
    summary_rows = []
    if not block.empty:
        for _, row in block.iterrows():
            summary_rows.append(
                {
                    "module": "ex_mvrv_exposure",
                    "statistic": f"{row['asset']} {row['frequency']} {row['block']} delta_r2",
                    "value": row["drop_block_delta_r2"],
                    "robustness_note": "Compared daily/weekly models when accepted; reviewed multicollinearity, FDR, ridge, and local-window correlation distributions.",
                    "evidence_grade_hint": "B",
                }
            )
    robustness = pd.DataFrame(summary_rows)
    write_csv(p.tables / "local_window_correlation_distribution.csv", local_window_df)
    write_csv(p.tables / "robustness_summary.csv", robustness)
    return {"local_window_correlation_distribution": local_window_df, "robustness_summary": robustness}


def build_analysis_outputs(root: Path = PROJECT_ROOT) -> dict[str, pd.DataFrame]:
    p = paths(root)
    ensure_output_dirs(p)
    daily = pd.read_parquet(p.panels / "feature_store_daily.parquet")
    crypto_weekly = pd.read_parquet(p.panels / "feature_store_crypto_weekly.parquet")
    tradfi_daily = pd.read_parquet(p.panels / "feature_store_tradfi_daily.parquet")
    tradfi_weekly = pd.read_parquet(p.panels / "feature_store_tradfi_weekly.parquet")
    etf_daily = pd.read_parquet(p.panels / "feature_store_etf_trading_daily.parquet")
    etf_weekly = pd.read_parquet(p.panels / "feature_store_etf_trading_weekly.parquet")
    monthly = pd.read_parquet(p.panels / "market_structure_monthly.parquet")
    results: dict[str, pd.DataFrame] = {}
    results.update(mvrv_tables(daily, p))
    results.update(exposure_tables(daily, tradfi_daily, tradfi_weekly, crypto_weekly, etf_daily, etf_weekly, p))
    results.update(leverage_tables(daily, p))
    results.update(etf_tables(daily, etf_daily, p))
    results["valuation_contamination_audit"] = valuation_contamination_audit(daily, crypto_weekly, p)
    results.update(liquidity_tables(crypto_weekly, p))
    results.update(asset_identity_tables(monthly, p))
    results.update(selected_major_tables(root, p))
    results.update(pit_tables(monthly, p))
    results.update(event_tables(root, daily, p))
    results.update(robustness_tables(tradfi_daily, crypto_weekly, p))
    ledger, glance = evidence_and_glance(p)
    results["evidence_ledger"] = ledger
    results["results_at_a_glance"] = glance
    write_csv(p.tables / "evidence_ledger.csv", ledger)
    write_md(p.tables / "results_at_a_glance.md", glance.to_markdown(index=False))
    write_csv(p.tables / "claim_inventory.csv", claim_inventory())
    write_model_cards(p)
    write_reports(root, p)
    return results


def asset_identity_tables(monthly: pd.DataFrame, p: BuildPaths) -> dict[str, pd.DataFrame]:
    frame = monthly.reset_index(drop=True).copy()
    latest_month = frame["month"].max()
    latest = frame[frame["month"] == latest_month].copy()
    taxonomy = latest[["asset_key", "token_id", "coingecko_id", "symbol", "asset_name", "asset_class_final"]].drop_duplicates()
    taxonomy = taxonomy.rename(columns={"asset_class_final": "taxonomy_class"})
    audit_rows: list[dict[str, Any]] = []
    for asset in SELECTED_ASSETS:
        symbol = str(asset["symbol"])
        canonical_key = str(asset["asset_key"]).lower()
        matches = frame[
            frame["asset_key"].astype(str).str.lower().eq(canonical_key)
            | frame["coingecko_id"].astype(str).str.lower().eq(canonical_key)
        ]
        expected_class = "BTC" if symbol == "BTC" else "ETH" if symbol == "ETH" else "selected majors ex BTC/ETH"
        bad_class = matches[~matches["asset_class_final"].eq(expected_class)]
        audit_rows.append(
            {
                "check_id": f"selected_major_{symbol.lower()}",
                "symbol": symbol,
                "intended_name": str(asset["name"]),
                "canonical_asset_key": str(asset["asset_key"]),
                "observed_rows": len(matches),
                "failing_rows": int(len(bad_class)),
                "status": "pass" if len(matches) > 0 and bad_class.empty else "coverage_gap" if len(matches) == 0 else "fail",
                "note": "Computed against source rows using canonical ID before symbol.",
            }
        )
    collision_specs: list[tuple[str, str, Callable[[pd.DataFrame], pd.Series], set[str], str]] = [
        (
            "toncoin_not_tokamak",
            "TON",
            lambda df: df["asset_name"].astype(str).str.contains("Tokamak", case=False, na=False)
            | df["coingecko_id"].astype(str).str.lower().str.contains("tokamak", na=False),
            {"selected majors ex BTC/ETH"},
            "Tokamak Network rows must not classify as Toncoin.",
        ),
        (
            "sol_not_wrapped_sol",
            "SOL",
            lambda df: df["asset_name"].astype(str).str.contains("Wrapped SOL", case=False, na=False)
            | df["coingecko_id"].astype(str).str.lower().str.contains("wrapped-sol", na=False),
            {"selected majors ex BTC/ETH"},
            "Wrapped SOL rows must remain productized/wrapped assets.",
        ),
        (
            "xrp_not_binance_peg_xrp",
            "XRP",
            lambda df: df["asset_name"].astype(str).str.contains("Binance-Peg XRP", case=False, na=False)
            | df["coingecko_id"].astype(str).str.lower().str.contains("binance-peg-xrp", na=False),
            {"selected majors ex BTC/ETH"},
            "Binance-Peg XRP rows must not classify as base XRP.",
        ),
        (
            "doge_not_binance_peg_doge",
            "DOGE",
            lambda df: df["asset_name"].astype(str).str.contains("Binance-Peg DOGE", case=False, na=False)
            | df["coingecko_id"].astype(str).str.lower().str.contains("binance-peg-doge", na=False),
            {"selected majors ex BTC/ETH"},
            "Binance-Peg DOGE rows must not classify as base DOGE.",
        ),
        (
            "btc_eth_wrappers_separated",
            "WBTC/WETH",
            lambda df: df["coingecko_id"].astype(str).str.lower().isin(PRODUCTIZED_ASSET_IDS)
            | df["symbol"].astype(str).str.upper().isin({"WBTC", "WETH", "STETH", "WSTETH", "RETH", "WEETH", "WBETH", "CBETH", "CBBTC"}),
            {"BTC", "ETH"},
            "Wrapped/staked/productized BTC/ETH rows must not classify as base BTC or ETH.",
        ),
        (
            "lst_governance_separated",
            "LDO/RPL/EIGEN/ETHFI",
            lambda df: df["symbol"].astype(str).str.upper().isin({"LDO", "RPL", "EIGEN", "ETHFI"})
            | df["coingecko_id"].astype(str).str.lower().isin(GOVERNANCE_RISK_IDS),
            {"productized/wrapped assets"},
            "LDO/RPL/EIGEN/ETHFI remain governance/infrastructure risk, not staking derivatives.",
        ),
    ]
    for check_id, symbol, selector, forbidden_classes, note in collision_specs:
        matches = frame[selector(frame)]
        failing = matches[matches["asset_class_final"].isin(forbidden_classes)]
        audit_rows.append(
            {
                "check_id": check_id,
                "symbol": symbol,
                "intended_name": "",
                "canonical_asset_key": "",
                "observed_rows": int(len(matches)),
                "failing_rows": int(len(failing)),
                "status": "pass" if failing.empty else "fail",
                "note": f"Computed from source rows. {note}",
            }
        )
    audit = pd.DataFrame(audit_rows)
    write_csv(p.tables / "asset_identity_audit.csv", audit)
    write_csv(p.tables / "asset_taxonomy.csv", taxonomy)
    return {"asset_identity_audit": audit, "asset_taxonomy": taxonomy}


def claim_inventory() -> pd.DataFrame:
    rows = [
        {
            "claim": "MVRV is the strongest independent factor.",
            "disposition": "reject",
            "replacement": "MVRV is a mechanically price-linked valuation-state diagnostic.",
            "reason": "Same-day MVRV mechanically embeds market capitalization and BTC price-state content.",
        },
        {
            "claim": "ETF flows caused BTC/ETH returns.",
            "disposition": "reject",
            "replacement": "ETF flows show market-plumbing associations with returns and volatility.",
            "reason": "Daily flows are simultaneous and reporting-timing sensitive.",
        },
        {
            "claim": "Current-top50 daily returns are historical altseason evidence.",
            "disposition": "demote",
            "replacement": (
                "Use PIT monthly composition/concentration/turnover for historical market-structure "
                "claims; treat current-top50 daily cohort as exploratory appendix material."
            ),
            "reason": "The cohort is survivorship-biased and not point-in-time.",
        },
        {
            "claim": "PIT monthly data supports composition and turnover analysis.",
            "disposition": "retain",
            "replacement": "Use PIT monthly data for composition, concentration, rank persistence, entries, and exits.",
            "reason": "Monthly snapshots are appropriate for structure, not daily performance.",
        },
        {
            "claim": "Crypto exposure to TradFi risk evolved over time.",
            "disposition": "rewrite",
            "replacement": "Rolling ex-MVRV exposure estimates describe time-varying co-movement with TradFi proxies.",
            "reason": "Exposure language is appropriate; predictive/causal language is not.",
        },
    ]
    return pd.DataFrame(rows)


def evidence_and_glance(p: BuildPaths) -> tuple[pd.DataFrame, pd.DataFrame]:
    claim_specs = [
        (
            "mvrv_mechanics_01",
            "mvrv_mechanics",
            "Same-day MVRV changes strongly overlap with BTC returns and are treated as measurement mechanics.",
            "BTC return",
            "d_log_mvrv",
            sample_range_from_table(p.tables / "mvrv_identity_points.csv", "date", "daily"),
            "daily",
            "same-interval identity audit and HAC same-day diagnostic",
            "mvrv_mechanical_link_audit.csv",
            "01_mvrv_mechanics.png",
            mvrv_headline_stat(p.tables / "mvrv_mechanical_link_audit.csv"),
            "Diagnostic only; same-day MVRV is excluded from primary exposure models.",
            "Identity residual scale, residual quantiles, and lagged state summaries.",
            "direct_target_component",
            "high",
            "high",
            "not_applicable_single_diagnostic",
            "B",
            "mechanically price-linked valuation-state measure",
            "strongest independent factor; predictive driver",
            "Source conventions and realized-cap updates affect residual.",
            "accepted_qualified",
        ),
        (
            "tradfi_exposure_01",
            "tradfi_exposure_evolution",
            "Contemporaneous TradFi exposure is evaluated on synchronized business-date and Friday panels.",
            "BTC/ETH returns",
            "equity, volatility, dollar, rate, and gold exposures",
            "effective sample reported per row",
            "daily; weekly",
            "same-support HAC OLS drop-block delta R-squared",
            "block_delta_r2.csv; rolling_tradfi_exposures.csv",
            "02_tradfi_exposure_shift.png",
            tradfi_period_headline_stat(p.tables / "block_delta_r2.csv"),
            "HAC/FDR diagnostics; rolling windows overlap.",
            "Business-date daily returns, Friday weekly returns, VIF, ridge, FDR, and local-window correlation distributions.",
            "low",
            "medium",
            "low",
            "FDR applied within model family.",
            "B",
            "period comparison of exposure strength",
            "ETF effect; forecast; caused",
            "Period splits are descriptive and not causal ETF identification.",
            "accepted_qualified",
        ),
        (
            "lagged_state_01",
            "lagged_state_associations",
            "Crypto-native liquidity, sentiment, funding, and scaled OI are reported as lagged-state associations.",
            "BTC/ETH returns",
            "stablecoin supply, valuation-sensitive TVL, Fear & Greed, funding, OI/market-cap, exchange flow",
            "effective sample reported per row",
            "daily; Sunday weekly",
            "same-support HAC OLS state model",
            "frequency_robustness.csv; block_delta_r2.csv",
            "",
            lagged_state_headline_stat(p.tables / "frequency_robustness.csv"),
            "HAC/FDR diagnostics; weekly models require nonzero accepted samples.",
            "Sunday-ended crypto weekly panel and daily lagged-state panel.",
            "medium",
            "medium",
            "medium",
            "FDR applied within model family.",
            "B",
            "lagged-state association",
            "exogenous shock; forecast",
            "USD TVL and USD/notional OI can embed price content.",
            "accepted_qualified",
        ),
        (
            "etf_plumbing_01",
            "etf_plumbing",
            "ETF flow intensity is separated into lag 0 and lag 1 associations on ETF trading dates.",
            "BTC/ETH returns and volatility",
            "ETF flow intensity, cumulative flow / lagged market cap",
            "ETF era only",
            "ETF trading daily; Friday weekly model rows",
            "correlation grid, absorption ratios, ETF-era augmented same-support OLS",
            "etf_flow_associations.csv; etf_absorption_metrics.csv; block_delta_r2.csv",
            "03_etf_market_plumbing.png",
            etf_flow_headline_stat(p.tables / "etf_flow_associations.csv"),
            "Short samples and reporting timing caveats.",
            "Lag 0 and lag 1 flow intensity are separate columns; no zero-imputation for holidays.",
            "low",
            "high",
            "low",
            "pre_specified_lag0_lag1_grid",
            "B",
            "market-plumbing association",
            "ETF flows caused returns",
            "ETF flow timing may be reported after market close.",
            "accepted_qualified",
        ),
        (
            "leverage_tail_01",
            "leverage_tail_stress",
            "Leverage and liquidation variables are treated as stress-state diagnostics with interpretable denominators.",
            "BTC lower-tail days",
            "funding, OI/market-cap, leverage ratio, liquidations / lagged OI and market cap",
            sample_range_from_table(p.tables / "liquidation_event_responses.csv", "event_date", "daily"),
            "daily",
            "state quintiles, lagged logit, top liquidation event windows",
            "leverage_tail_risk_summary.csv; tail_risk_models.csv; liquidation_event_responses.csv",
            "04_leverage_tail_stress.png",
            leverage_headline_stat(p.tables / "leverage_tail_risk_summary.csv"),
            "Class-balance diagnostics; event responses separated from same-day signatures.",
            "Liquidation ratios in percent of lagged OI or basis points of lagged market cap.",
            "low",
            "medium",
            "medium_if_usd_notional",
            "limited_pre_specified_state_model",
            "B",
            "U-shaped tail-stress pattern",
            "liquidations caused the move",
            "Exchange coverage and liquidation reporting conventions.",
            "accepted_qualified",
        ),
        (
            "liquidity_state_01",
            "stablecoin_defi_state",
            "Stablecoin supply is a cleaner liquidity-state proxy; raw USD TVL is valuation-sensitive.",
            "BTC/ETH returns and BTC volatility",
            "stablecoin supply growth, valuation-sensitive DeFi TVL growth",
            sample_range_from_table(p.tables / "stablecoin_liquidity_features.csv", "date", "weekly"),
            "Sunday weekly",
            "weekly regime summaries and contamination audit correlations",
            "stablecoin_defi_liquidity_summary.csv; liquidity_associations.csv; valuation_contamination_audit.csv",
            "",
            liquidity_headline_stat(p.tables / "valuation_contamination_audit.csv"),
            "Descriptive correlations only.",
            "Sunday-ended weekly transformations and explicit TVL price-content audit.",
            "high_usd_price_content",
            "medium",
            "high",
            "not_promoted_as_shock",
            "B",
            "valuation-sensitive DeFi balance-sheet proxy",
            "pure capital inflow; liquidity shock",
            "No price-adjusted TVL source is available in the local data.",
            "accepted_qualified",
        ),
        (
            "pit_structure_01",
            "pit_structure",
            "Monthly PIT snapshots support composition, concentration, and turnover evidence.",
            "market composition and concentration",
            "PIT top-100 slices from top-200 snapshots",
            sample_range_from_table(p.tables / "pit_market_structure_summary.csv", "snapshot_date", "monthly"),
            "monthly",
            "market-cap shares, HHI, top-share concentration, entries/exits",
            "pit_market_structure_summary.csv; pit_composition.csv; pit_turnover.csv",
            "05_point_in_time_market_structure.png",
            pit_headline_stat(p.tables / "pit_market_structure_summary.csv"),
            "Descriptive monthly snapshots.",
            "Shares sum within month; taxonomy and canonical IDs audited.",
            "none",
            "low",
            "none",
            "not_applicable_descriptive",
            "A",
            "market-structure context",
            "daily PIT performance",
            "No daily PIT constituent OHLCV for historical performance.",
            "accepted_headline",
        ),
        (
            "selected_major_risk_01",
            "selected_major_risk",
            "Selected-major risk comparisons are coverage-aware and use canonical local IDs.",
            "volatility, drawdown, beta",
            "selected major current-source daily returns",
            sample_range_from_table(p.tables / "selected_major_risk_metrics.csv", "first_date", "daily"),
            "daily",
            "coverage-window and comparable-window risk summaries",
            "selected_major_risk_metrics.csv; selected_major_comparable_window_metrics.csv",
            "06_selected_major_asset_risk.png",
            selected_major_headline_stat(p.tables / "selected_major_comparable_window_metrics.csv", p.tables / "selected_major_coverage.csv"),
            "Coverage windows differ; HYPE is short-history.",
            "Comparable-window metrics reported separately.",
            "none",
            "medium",
            "low",
            "not_promoted_as_full_cycle",
            "B",
            "coverage-aware risk comparison",
            "event response for selected majors",
            "Current-source cohort coverage begins mostly in 2023.",
            "accepted_qualified",
        ),
        (
            "event_atlas_01",
            "event_atlas",
            "Configured BTC/ETH event windows are empirical placebo-window tests, not bootstrap causal inference.",
            "BTC/ETH post-event returns",
            "registered event dates",
            sample_range_from_table(p.tables / "event_response_matrix.csv", "event_date", "daily"),
            "daily",
            "post +1 through +10 return and non-overlapping placebo windows",
            "event_response_matrix.csv; event_inference.csv",
            "gallery/appendix_event_response_matrix.png",
            event_headline_stat(p.tables / "event_inference.csv"),
            "Small event count; placebo windows exclude registered-event overlaps.",
            "Actual and placebo windows use the same block size and convention.",
            "none",
            "high",
            "none",
            "empirical_placebo_not_bootstrap",
            "C",
            "descriptive event-window response",
            "causal event effect; forecast rule",
            "Sparse events and overlapping regimes.",
            "exploratory_only",
        ),
        (
            "deferred_altseason_01",
            "deferred_pit_altseason",
            "True point-in-time historical altseason return analysis remains deferred.",
            "altseason performance",
            "historical PIT constituent daily OHLCV and market cap",
            "not available",
            "daily",
            "honest skip path",
            "claim_inventory.csv; selected_major_coverage.csv",
            "",
            "Deferred: monthly PIT snapshots do not include daily constituent return histories.",
            "No statistical inference attempted.",
            "Public checker and evidence ledger prevent current-cohort overclaiming.",
            "none",
            "high",
            "none",
            "not_promoted",
            "C",
            "deferred until data exists",
            "historical altseason backtest",
            "Requires daily point-in-time constituent OHLCV/mcap.",
            "data_limited_deferred",
        ),
    ]
    claim_rows = [
        dict(zip(TABLE_SCHEMA_COLUMNS["evidence_ledger"], spec, strict=True))
        for spec in claim_specs
    ]
    ledger = pd.DataFrame(claim_rows, columns=TABLE_SCHEMA_COLUMNS["evidence_ledger"])
    glance = pd.DataFrame(
        [
            {
                "question": "MVRV mechanics",
                "finding": "MVRV is retained as a mechanically price-linked valuation-state diagnostic.",
                "key_statistic": mvrv_headline_stat(p.tables / "mvrv_mechanical_link_audit.csv"),
                "sample_frequency": "2020-2026 daily",
                "evidence_grade": "B",
                "interpretation": "Use lagged state regimes; exclude same-day MVRV from primary BTC/ETH models.",
                "caveat": "Mechanical target overlap.",
                "source_table": "mvrv_mechanical_link_audit.csv",
            },
            {
                "question": "TradFi exposure evolution",
                "finding": "Contemporaneous exposure comparisons use synchronized business-date and Friday calendars.",
                "key_statistic": tradfi_period_headline_stat(p.tables / "block_delta_r2.csv"),
                "sample_frequency": "business-date daily; Friday weekly",
                "evidence_grade": "B",
                "interpretation": "Period comparison of co-movement, not an ETF-effect estimate.",
                "caveat": "Collinearity and overlapping rolling windows.",
                "source_table": "block_delta_r2.csv",
            },
            {
                "question": "ETF plumbing",
                "finding": "ETF flow intensity is split into lag 0 and lag 1 on ETF trading dates.",
                "key_statistic": etf_flow_headline_stat(p.tables / "etf_flow_associations.csv"),
                "sample_frequency": "ETF trading daily",
                "evidence_grade": "B",
                "interpretation": "Market-plumbing association only.",
                "caveat": "Short sample and reporting timing.",
                "source_table": "etf_flow_associations.csv",
            },
            {
                "question": "Leverage and tail stress",
                "finding": "Tail-day rates are reported for pre-specified Q1/Q3/Q5 leverage states.",
                "key_statistic": leverage_headline_stat(p.tables / "leverage_tail_risk_summary.csv"),
                "sample_frequency": "daily",
                "evidence_grade": "B",
                "interpretation": "U-shaped pattern, not only the highest-leverage quintile.",
                "caveat": "No liquidation initiation-cause claim.",
                "source_table": "leverage_tail_risk_summary.csv",
            },
            {
                "question": "Stablecoin/DeFi state",
                "finding": "Raw USD TVL is valuation-sensitive; stablecoin supply is the cleaner local liquidity proxy.",
                "key_statistic": liquidity_headline_stat(p.tables / "valuation_contamination_audit.csv"),
                "sample_frequency": "Sunday weekly",
                "evidence_grade": "B",
                "interpretation": "Treat TVL as DeFi balance-sheet state, not pure inflow.",
                "caveat": "No price-adjusted TVL source is available locally.",
                "source_table": "valuation_contamination_audit.csv",
            },
            {
                "question": "PIT market structure",
                "finding": "PIT monthly snapshots support composition, concentration, and turnover evidence.",
                "key_statistic": pit_headline_stat(p.tables / "pit_market_structure_summary.csv"),
                "sample_frequency": "monthly",
                "evidence_grade": "A",
                "interpretation": "Use for market structure only.",
                "caveat": "No daily PIT performance.",
                "source_table": "pit_market_structure_summary.csv",
            },
            {
                "question": "Selected-major risk",
                "finding": "Selected-major risk is coverage-aware and reports comparable-window metrics.",
                "key_statistic": selected_major_headline_stat(p.tables / "selected_major_comparable_window_metrics.csv", p.tables / "selected_major_coverage.csv"),
                "sample_frequency": "daily current-source coverage",
                "evidence_grade": "B",
                "interpretation": "Compare risk only with coverage caveats.",
                "caveat": "HYPE is short-history; TON is canonical-source only.",
                "source_table": "selected_major_comparable_window_metrics.csv",
            },
            {
                "question": "Event atlas",
                "finding": "Configured BTC/ETH events use equal-length empirical placebo windows.",
                "key_statistic": event_headline_stat(p.tables / "event_inference.csv"),
                "sample_frequency": "daily",
                "evidence_grade": "C",
                "interpretation": "Descriptive event-window context.",
                "caveat": "Not bootstrap causal inference.",
                "source_table": "event_inference.csv",
            },
            {
                "question": "Deferred PIT altseason",
                "finding": "True PIT historical altseason return analysis is deferred.",
                "key_statistic": "No daily PIT constituent OHLCV/mcap history is available.",
                "sample_frequency": "not available",
                "evidence_grade": "C",
                "interpretation": "Monthly PIT supports structure, not daily performance.",
                "caveat": "Current-cohort daily outputs are survivorship-biased.",
                "source_table": "claim_inventory.csv",
            },
        ]
    )
    return ledger, glance


def table_stat(path: Path, metric: str) -> str:
    if not path.exists():
        return "not generated"
    frame = pd.read_csv(path)
    if "metric" in frame.columns and "value" in frame.columns:
        hit = frame[frame["metric"] == metric]
        if not hit.empty:
            value = hit["value"].iloc[0]
            return f"{value:.4f}" if isinstance(value, float | np.floating) else str(value)
    return "see table"


def sample_range_from_table(path: Path, date_col: str, frequency: str) -> str:
    if not path.exists():
        return "not generated"
    frame = pd.read_csv(path)
    if date_col not in frame:
        return frequency
    dates = pd.to_datetime(frame[date_col], errors="coerce").dropna()
    if dates.empty:
        return frequency
    return f"{dates.min().date().isoformat()} to {dates.max().date().isoformat()} {frequency}"


def mvrv_headline_stat(path: Path) -> str:
    if not path.exists():
        return "not generated"
    frame = pd.read_csv(path)
    metrics = frame.set_index("metric")["value"]
    corr = float(metrics.get("corr_btc_return_d_log_mvrv", np.nan))
    r2 = float(metrics.get("same_day_mvrv_r2_diagnostic", np.nan))
    residual_scale = float(metrics.get("identity_residual_abs_median_to_median_abs_btc_return", np.nan))
    return f"corr(BTC return, d-log MVRV)={corr:.4f}; R2={r2:.4f}; median abs residual / median abs BTC return={residual_scale:.2e}"


def block_headline_stat(path: Path, model_family: str = "long_sample_contemporaneous_exposure") -> str:
    return tradfi_period_headline_stat(path, model_family)


def tradfi_period_headline_stat(path: Path, model_family: str = "long_sample_contemporaneous_exposure") -> str:
    if not path.exists():
        return "not generated"
    frame = pd.read_csv(path)
    frame = frame[
        frame["model_family"].eq(model_family)
        & frame["frequency"].eq("daily")
        & frame["block"].eq("equity_beta")
        & frame["regime"].isin(["pre_btc_etf", "btc_etf_era"])
    ]
    if frame.empty:
        return "no accepted model sample"
    parts = []
    for asset in ["BTC", "ETH"]:
        pre = frame[(frame["asset"].eq(asset)) & frame["regime"].eq("pre_btc_etf")]
        era = frame[(frame["asset"].eq(asset)) & frame["regime"].eq("btc_etf_era")]
        if pre.empty or era.empty:
            continue
        pre_row = pre.iloc[0]
        era_row = era.iloc[0]
        parts.append(
            f"{asset} equity block pre-BTC-ETF delta R2={pre_row['drop_block_delta_r2']:.4f} "
            f"(n={int(pre_row['n'])}) vs BTC-ETF-era delta R2={era_row['drop_block_delta_r2']:.4f} "
            f"(n={int(era_row['n'])})"
        )
    return "; ".join(parts) + "; period comparison, not ETF effect" if parts else "no accepted pre-specified equity comparison"


def lagged_state_headline_stat(path: Path) -> str:
    if not path.exists():
        return "not generated"
    frame = pd.read_csv(path)
    subset = frame[
        frame["model_family"].eq("long_sample_lagged_state_association")
        & frame["frequency"].isin(["daily", "weekly"])
        & frame["status"].eq("passed")
    ]
    if subset.empty:
        return "no accepted lagged-state model"
    daily = subset[subset["frequency"].eq("daily")]
    rows = daily if not daily.empty else subset
    parts = []
    for asset in ["BTC", "ETH"]:
        hit = rows[rows["asset"].eq(asset)]
        if hit.empty:
            continue
        row = hit.iloc[0]
        parts.append(f"{asset} {row['frequency']} lagged-state full R2={row['full_r2']:.4f}, n={int(row['n'])}")
    return "; ".join(parts)


def etf_flow_headline_stat(path: Path) -> str:
    if not path.exists():
        return "not generated"
    frame = pd.read_csv(path)
    parts = []
    for asset in ["BTC", "ETH"]:
        hit = frame[frame["asset"].eq(asset)].sort_values("flow_lag_days")
        if hit.empty:
            continue
        lag0 = hit[hit["flow_lag_days"].eq(0)]
        lag1 = hit[hit["flow_lag_days"].eq(1)]
        if lag0.empty or lag1.empty:
            continue
        parts.append(
            f"{asset} lag0 return corr={lag0['return_corr'].iloc[0]:.3f} "
            f"(n={int(lag0['n_return'].iloc[0])}) vs lag1={lag1['return_corr'].iloc[0]:.3f} "
            f"(n={int(lag1['n_return'].iloc[0])})"
        )
    return "; ".join(parts) if parts else "no ETF flow association rows"


def leverage_headline_stat(path: Path) -> str:
    if not path.exists():
        return "not generated"
    frame = pd.read_csv(path)
    if frame.empty:
        return "no leverage state rows"
    parts = []
    for state in ["Q1 low", "Q3", "Q5 high"]:
        hit = frame[frame["leverage_state"].astype(str).eq(state)]
        if not hit.empty:
            row = hit.iloc[0]
            parts.append(f"{state} tail-day rate={row['bottom5_rate']:.2%} (n={int(row['n'])})")
    return "; ".join(parts) + "; read as U-shaped state pattern" if parts else "no Q1/Q3/Q5 leverage states"


def liquidity_headline_stat(path: Path) -> str:
    if not path.exists():
        return "not generated"
    frame = pd.read_csv(path)
    subset = frame[frame["feature_id"].eq("valuation_sensitive_defi_tvl_growth")]
    parts = []
    for asset in ["BTC", "ETH"]:
        hit = subset[subset["asset"].eq(asset)]
        if not hit.empty:
            row = hit.iloc[0]
            parts.append(f"{asset} same-week raw USD TVL corr={row['correlation_with_return']:.3f} (n={int(row['n'])})")
    return "; ".join(parts) + "; TVL labeled valuation-sensitive" if parts else "no TVL valuation audit rows"


def pit_headline_stat(path: Path) -> str:
    if not path.exists():
        return "not generated"
    frame = pd.read_csv(path)
    if frame.empty:
        return "no PIT rows"
    sort_col = "snapshot_date" if "snapshot_date" in frame else "month"
    row = frame.sort_values(sort_col).iloc[-1]
    partial = " partial snapshot" if bool(row.get("is_partial_month", False)) else ""
    snapshot = row.get("snapshot_date", row.get("month", ""))
    month = row.get("month", "")
    return f"{snapshot}{partial} (month={month}) top10 share={row['top10_share']:.2%}, HHI={row['hhi']:.3f}"


def selected_major_headline_stat(comparable_path: Path, coverage_path: Path) -> str:
    if not comparable_path.exists() or not coverage_path.exists():
        return "not generated"
    comparable = pd.read_csv(comparable_path)
    coverage = pd.read_csv(coverage_path)
    if comparable.empty:
        return "no comparable-window rows"
    common_start = comparable["common_start"].iloc[0]
    common_end = comparable["common_end"].iloc[0]
    hype = coverage[coverage["symbol"].eq("HYPE")]
    hype_n = int(hype["observations"].iloc[0]) if not hype.empty else 0
    return f"{len(comparable)} assets comparable from {common_start} to {common_end}; HYPE max-coverage n={hype_n}"


def event_headline_stat(path: Path) -> str:
    if not path.exists():
        return "not generated"
    frame = pd.read_csv(path)
    if frame.empty:
        return "no event rows"
    block_size = int(frame["block_size"].dropna().iloc[0]) if frame["block_size"].notna().any() else 0
    placebo = int(frame["placebo_window_count"].median()) if frame["placebo_window_count"].notna().any() else 0
    assets = ",".join(sorted(frame["asset"].dropna().unique()))
    return f"{assets} event windows use block size={block_size}; median eligible placebo windows={placebo}; convention +1 through +10"


def write_model_cards(p: BuildPaths) -> None:
    cards = {
        "mvrv_mechanics.md": f"""# MVRV Mechanics Model Card

Purpose: audit whether same-day MVRV changes mechanically overlap BTC returns and summarize lagged MVRV state outcomes.

Outcome and features: BTC log return, `d_log_mvrv`, `d_log_market_cap`, `d_log_realized_cap`, and `identity_residual` over the same daily interval.

Principal finding: {mvrv_headline_stat(p.tables / "mvrv_mechanical_link_audit.csv")}.

Estimator and uncertainty: HAC same-day diagnostic plus identity residual quantiles. This is a measurement audit, not a predictive model.

Prohibited claims: MVRV is the strongest independent factor; same-day MVRV predicts BTC returns.
""",
        "tradfi_exposure.md": f"""# TradFi Exposure Model Card

Purpose: measure contemporaneous BTC/ETH co-movement with equities, volatility, dollar, rates, and gold.

Calendar: daily models use common TradFi business-date closes; weekly models use Friday-to-Friday returns.

Estimator: same-support HAC OLS with drop-block delta R-squared, conventional partial R-squared in a separate table, FDR, VIF, and ridge diagnostics.

Principal finding: {tradfi_period_headline_stat(p.tables / "block_delta_r2.csv")}.

Prohibited claims: ETF effect; forecast; causal macro driver.
""",
        "lagged_state_associations.md": f"""# Lagged-State Association Model Card

Purpose: summarize lagged crypto-native state associations without calling them exposure betas.

Features: stablecoin supply growth, valuation-sensitive USD TVL growth, Fear & Greed state/change, funding z-score, OI/market-cap growth, and BTC exchange-flow state where available.

Calendar: daily state models use the crypto daily panel; weekly state models use Sunday-ended crypto weeks.

Principal finding: {lagged_state_headline_stat(p.tables / "frequency_robustness.csv")}.

Prohibited claims: exogenous liquidity shock; price forecast.
""",
        "etf_market_plumbing.md": f"""# ETF Market Plumbing Model Card

Purpose: describe ETF-era market plumbing through flow intensity, lag timing, and absorption ratios.

Calendar and timing: ETF trading-day panel computes BTC/ETH returns from the prior ETF trading date to the current ETF trading date. Lag 0 is current ETF trading-date flow intensity; lag 1 is prior ETF trading-date flow intensity.

Principal finding: {etf_flow_headline_stat(p.tables / "etf_flow_associations.csv")}.

Limitations: short sample, reporting timing, and simultaneity.

Prohibited claims: ETF flows caused BTC or ETH returns.
""",
        "leverage_tail_risk.md": f"""# Leverage And Tail Risk Model Card

Purpose: evaluate leverage/funding/OI state and liquidation signatures as stress diagnostics.

Features and units: lagged OI/market-cap growth, funding z-score, leverage percentile, liquidation USD / lagged OI in percent, and liquidation USD / lagged market cap in basis points.

Principal finding: {leverage_headline_stat(p.tables / "leverage_tail_risk_summary.csv")}.

Estimator: descriptive quintiles, lagged logit diagnostics, and top liquidation event response table.

Prohibited claims: liquidations initiated price moves.
""",
        "stablecoin_defi_state.md": f"""# Stablecoin And DeFi State Model Card

Purpose: summarize weekly stablecoin/DeFi state while auditing raw USD TVL price content.

Calendar: Sunday-ended crypto weekly panel.

Principal finding: {liquidity_headline_stat(p.tables / "valuation_contamination_audit.csv")}.

Interpretation: stablecoin supply is the cleaner local liquidity-state proxy; raw USD TVL is a valuation-sensitive DeFi balance-sheet proxy.

Prohibited claims: raw TVL growth is pure capital inflow; proxy changes are exogenous liquidity shocks.
""",
        "selected_major_risk.md": f"""# Selected-Major Risk Model Card

Purpose: compare selected-major volatility, drawdown, beta, and coverage using canonical IDs.

Procedure: maximum-coverage metrics are reported separately from comparable-window metrics.

Principal finding: {selected_major_headline_stat(p.tables / "selected_major_comparable_window_metrics.csv", p.tables / "selected_major_coverage.csv")}.

Limitations: current daily constituent coverage begins mostly in 2023; HYPE is short-history; TON is sourced only from the canonical local series.

Prohibited claims: full-cycle comparison; selected-major event-response analysis.
""",
        "pit_market_structure.md": f"""# PIT Market Structure Model Card

Purpose: describe monthly PIT top-200 composition, concentration, and turnover using canonical ID taxonomy.

Principal finding: {pit_headline_stat(p.tables / "pit_market_structure_summary.csv")}.

Procedure: top-100 shares, top-5/top-10 share, HHI, entries, exits, and rank persistence.

Limitations: monthly snapshots do not provide daily PIT constituent returns.

Prohibited claims: daily historical altseason backtest.
""",
        "event_atlas.md": f"""# Event Atlas Model Card

Purpose: report BTC/ETH event-window outcomes with equal-length empirical placebo windows.

Convention: post 10-day return means +1 through +10, excluding event day.

Principal finding: {event_headline_stat(p.tables / "event_inference.csv")}.

Procedure: placebo windows exclude registered-event overlaps and use the same block size as actual event windows.

Prohibited claims: bootstrap confidence interval; causal event effect; forecast rule.
""",
    }
    for filename, text in cards.items():
        write_md(p.model_cards / filename, text)


def write_reports(root: Path, p: BuildPaths) -> None:
    write_md(root / "docs" / "decisions" / "research_charter.md", research_charter_text())
    write_md(root / "docs" / "architecture" / "system.md", architecture_text())
    write_md(root / "docs" / "data" / "data_governance.md", data_governance_text())
    write_md(root / "docs" / "methodology" / "transformations_and_timing.md", transformations_text())
    write_md(root / "docs" / "methodology" / "attribution_methods.md", attribution_methods_text())
    write_md(root / "docs" / "methodology" / "interpretation_guardrails.md", interpretation_guardrails_text())
    write_md(p.report / "executive_summary.md", executive_summary_text(p))
    write_md(p.report / "methodology.md", methodology_report_text())
    write_md(p.report / "results_and_interpretation.md", results_and_interpretation_text(p))
    write_md(p.report / "limitations.md", limitations_text())
    write_md(p.report / "reproducibility_report.md", reproducibility_report_text())


def executive_summary_text(p: BuildPaths) -> str:
    return f"""# Executive Summary

Crypto Market Dynamics is a descriptive research-code project covering BTC/ETH valuation mechanics, synchronized TradFi exposure, ETF market plumbing, leverage/tail stress, stablecoin/DeFi state, point-in-time market structure, selected-major risk, and event windows from local 2020-2026 data.

The strongest measurement warning remains MVRV: {mvrv_headline_stat(p.tables / "mvrv_mechanical_link_audit.csv")}. Same-day MVRV therefore stays out of the primary BTC/ETH exposure models and appears only as a mechanics audit and lagged state context.

TradFi exposure is now calendar-synchronized. {tradfi_period_headline_stat(p.tables / "block_delta_r2.csv")}. This is a period comparison of co-movement on common business-date closes, not an ETF-effect estimate.

ETF, leverage, and liquidity results are descriptive and timing-sensitive. {etf_flow_headline_stat(p.tables / "etf_flow_associations.csv")}. {leverage_headline_stat(p.tables / "leverage_tail_risk_summary.csv")}. {liquidity_headline_stat(p.tables / "valuation_contamination_audit.csv")}.

The latest PIT structure headline is {pit_headline_stat(p.tables / "pit_market_structure_summary.csv")}. Selected-major risk is coverage-aware: {selected_major_headline_stat(p.tables / "selected_major_comparable_window_metrics.csv", p.tables / "selected_major_coverage.csv")}. Event outputs remain empirical placebo-window tests: {event_headline_stat(p.tables / "event_inference.csv")}.

Release caveat: `DATA_LICENSE.md` and `provider_data_disposition.csv` document provider-data risk but do not grant redistribution rights. The repository should remain private until uncertain/restricted raw exports are cleared or removed from the public repository and history.
"""


def results_and_interpretation_text(p: BuildPaths) -> str:
    return f"""# Results And Interpretation

## MVRV Mechanics

{mvrv_headline_stat(p.tables / "mvrv_mechanical_link_audit.csv")}. Interpret MVRV as a mechanically price-linked valuation-state measure. The identity residual is reported with source-convention caveats rather than called small by assumption.

## TradFi Exposure Evolution

{tradfi_period_headline_stat(p.tables / "block_delta_r2.csv")}. Daily exposure models use consecutive common TradFi business-date closes. Weekly TradFi models use Friday-to-Friday returns. Rolling beta and correlation outputs exclude ETF and sparse state features.

## Lagged-State Associations

{lagged_state_headline_stat(p.tables / "frequency_robustness.csv")}. These are lagged-state associations, not exposure betas or forecasts. Raw USD TVL and OI are audited for price content before being used in public language.

## ETF Market Plumbing

{etf_flow_headline_stat(p.tables / "etf_flow_associations.csv")}. Lag 0 is the current ETF trading-date flow intensity; lag 1 is the prior ETF trading-date flow intensity. Flow relationships are association grids and absorption ratios, not causal return estimates.

## Leverage And Tail Stress

{leverage_headline_stat(p.tables / "leverage_tail_risk_summary.csv")}. Liquidations are expressed as percent of prior-day open interest or basis points of prior-day market cap, and post-event returns exclude the same-day liquidation signature.

## Stablecoin And DeFi State

{liquidity_headline_stat(p.tables / "valuation_contamination_audit.csv")}. Stablecoin supply growth is the cleaner local liquidity-state proxy. Raw USD TVL growth is labeled a valuation-sensitive DeFi balance-sheet proxy because deposited-token price appreciation can mechanically raise USD TVL.

## PIT Structure And Selected Majors

{pit_headline_stat(p.tables / "pit_market_structure_summary.csv")}. PIT data is monthly composition/concentration/turnover evidence only. {selected_major_headline_stat(p.tables / "selected_major_comparable_window_metrics.csv", p.tables / "selected_major_coverage.csv")}. Selected-major event responses are not claimed.

## Event Atlas And Deferred Altseason

{event_headline_stat(p.tables / "event_inference.csv")}. Event cells remain missing when unavailable. True PIT historical altseason performance is deferred until daily PIT constituent OHLCV and market-cap histories exist.
"""


def research_charter_text() -> str:
    return """# Research Charter

## Objective

Crypto Market Dynamics studies whether crypto market behavior evolved from 2020-2026 across native valuation state, macro/risk integration, ETF access, leverage, stablecoin/DeFi state, selected major assets, point-in-time market structure, and BTC/ETH event windows.

## Questions

1. How mechanically linked are MVRV and related holder-profit metrics to BTC price/returns?
2. After removing mechanically linked valuation-state measures, how did BTC/ETH exposures to equities, volatility, the dollar, yields, gold, ETF flows, and crypto liquidity evolve?
3. Are leverage, funding, OI, liquidations, and taker flow more informative for volatility/tail stress than for average returns?
4. How did ETF access relate to market plumbing, AUM concentration, basis/premium relationships, and risk-market integration?
5. How do stablecoin and DeFi state variables relate to BTC/ETH returns and BTC volatility?
6. How do selected major assets differ in volatility, drawdown, and beta after accounting for coverage?
7. How did point-in-time market composition, concentration, and turnover evolve around halving and ETF eras?
8. Which findings are robust, qualified, exploratory, rejected, or data-limited?

## Primary outcomes

- Ex-MVRV return exposure.
- Realized volatility.
- Extreme-down-day/tail state.
- Rolling beta/correlation.
- Market concentration/turnover.

## Secondary outcomes

- Drawdown.
- Event windows.
- Current-cohort exploratory breadth.

## Excluded claims

The project does not forecast prices, present trading strategies, claim causal ETF effects, or treat same-day MVRV as an independent factor.

## Evidence grades

Grade A is robust descriptive evidence; Grade B is qualified descriptive evidence; Grade C is exploratory; rejected findings are kept in the evidence ledger. True point-in-time daily altseason performance is deferred until historical constituent daily data exists.
"""


def methodology_report_text() -> str:
    return transformations_text() + """

## Estimation

Full, reduced-block, and feature-drop models are fit on one explicitly constructed complete-case frame per asset, frequency, regime, and model family. The tables report `n_full`, `n_reduced`, `same_support`, sample dates, feature lists, and row-index hashes. The build fails if nested-model R-squared monotonicity or conventional partial-R-squared bounds are violated.

## Evidence Language

Contemporaneous TradFi coefficients are exposure/co-movement estimates. Crypto-native lagged variables are lagged-state associations. ETF flow intensity is a market-plumbing association. Raw USD TVL is a valuation-sensitive DeFi balance-sheet proxy, and OI growth is interpreted through OI/market-cap scaling when treated as USD/notional-valued.
"""


def architecture_text() -> str:
    return """# Maintained Architecture

The maintained public build path is:

- `src/cqresearch/pipelines/final_research.py` for orchestration.
- `scripts/build_data_inventory.py` for source inventory.
- `scripts/build_feature_store.py` for deterministic panels.
- `scripts/build_analysis_outputs.py` for tables, reports, and model cards.
- `scripts/build_public_figures.py` for six README figures, one gallery appendix figure, and the QA contact sheet.
- `scripts/check_public_surface.py` for README/output guardrails.
- `scripts/run_all.py` for the complete offline build.

Legacy portfolio and versioned release workflows are not part of the maintained public surface.
"""


def data_governance_text() -> str:
    return """# Data Governance

Raw and curated provider exports are local-only under `data_local/raw/` and are ignored by Git. Generated feature stores live under `data_local/processed/`; public-safe semantic tables, reports, metadata, and figures live under `outputs/`.

Asset joins use canonical IDs where available. Selected major assets are defined in `config/assets.yml`; Toncoin is explicitly separated from Tokamak Network, and wrapped/productized assets are separated from governance/infrastructure risk assets.

No source should be silently substituted for a weaker dataset. If coverage is insufficient, the pipeline writes a qualified or skipped output rather than fabricating data.
"""


def transformations_text() -> str:
    return """# Transformations And Timing

- Prices use log returns.
- Rates and index levels use first differences where appropriate.
- Daily TradFi models use common business-date closes: BTC/ETH returns are recomputed between consecutive common TradFi business dates, then aligned with QQQ, SPY, IWM, DXY, gold, VIX, real-yield, and nominal-yield moves on those same business dates.
- Weekly TradFi models use Friday-to-Friday BTC/ETH and TradFi returns/changes.
- Crypto-native weekly liquidity/state analysis uses Sunday-ended crypto weeks.
- ETF trading-day panels compute BTC/ETH returns from the prior ETF trading date to the current ETF trading date.
- ETF flows are scaled by prior-period market capitalization and modeled separately at lag 0 and lag 1 in ETF-era augmented specifications.
- Liquidations are expressed as liquidation USD divided by prior-period open interest in percent and prior-period market cap in basis points.
- MVRV same-day changes are diagnostic only; lagged MVRV levels, percentiles, z-scores, and regimes are used for state conditioning.
- Stablecoin and DeFi state features are primary at weekly frequency; weekly returns sum daily log returns, weekly changes sum daily level changes, flows sum over the week and scale by prior week-end denominators, and state variables use prior week-end state.
- Raw USD DeFi TVL growth is labeled `valuation_sensitive_defi_tvl_growth` unless price-adjusted. OI growth is audited and OI/market-cap growth is preferred when OI is treated as USD/notional-valued.
- Monthly PIT market-universe data is joined only for composition, concentration, and turnover analysis.
- Same-support model comparisons use identical non-missing row sets.
"""


def attribution_methods_text() -> str:
    return """# Attribution Methods

## Drop-Block Delta R-Squared

The canonical block table reports `R2_full - R2_reduced` as `drop_block_delta_r2`.
This is a same-support model-sensitivity diagnostic. It is not labeled
conventional partial R-squared.

## Conventional Partial R-Squared

For readers who need the conventional formula, the separate
`outputs/tables/conventional_partial_r2.csv` table reports
`(SSE_reduced - SSE_full) / SSE_reduced`.

## Interpretation

Attribution diagnostics can be unstable when feature blocks are correlated. Read
contemporaneous TradFi models as co-movement/integration evidence and lagged
state models as lagged-state associations, not causal contribution or forecast
importance.
"""


def interpretation_guardrails_text() -> str:
    return """# Interpretation Guardrails

- ETF-flow results are association, exposure, timing, and market-plumbing
  diagnostics. They do not prove ETF flows caused BTC or ETH returns.
- Lagged stablecoin supply is a liquidity-state proxy; raw USD TVL is a valuation-sensitive
  DeFi balance-sheet proxy, not identified capital inflow.
- MVRV is a mechanically price-linked valuation-state diagnostic; same-day MVRV
  changes are excluded from primary BTC/ETH exposure models.
- `block_delta_r2.csv` reports drop-block delta R-squared, not conventional
  partial R-squared.
- Monthly PIT data supports composition, concentration, and turnover. It does
  not identify daily historical altseason performance.
- Daily current-top50 cohort outputs are exploratory and survivorship-biased.
- Frozen local data improves reproducibility but is not a live market monitor.
"""


def limitations_text() -> str:
    return """# Limitations

- No causal identification strategy is claimed.
- ETF, liquidation, stablecoin, and DeFi variables are subject to simultaneity and reporting timing.
- MVRV and holder-profit metrics contain mechanical price-state content.
- Raw USD DeFi TVL embeds deposited-asset price effects; no local price-adjusted TVL source is available.
- CryptoQuant OI is treated as USD/notional-valued unless provider metadata prove otherwise, so OI/market-cap growth is preferred for public state language.
- Current-top50 daily cohort outputs are exploratory and survivorship-biased.
- True PIT historical altseason-return analysis is deferred until daily constituent OHLCV and market-cap data exist for every historical PIT constituent.
- Current selected-major daily constituent coverage begins 2022-12-31/2023 for most assets; HYPE is short-history.
- The project is not affiliated with CryptoQuant, Artemis, TradingView, DefiLlama, Farside, AlternativeMe, FRED, or other data providers.
"""


def final_release_audit_text() -> str:
    return """# Final Release Audit

## Verdict

Pass, pending reviewer approval and merge.

## Scope completed

- Maintained canonical build path: `scripts/run_all.py`.
- Semantic table and report surface under `outputs/`.
- Public figure surface limited to six README figures under `outputs/figures/public/`.
- MVRV same-day features removed from primary BTC/ETH exposure models.
- Contemporaneous TradFi exposure, lagged-state association, and ETF-era augmented model families are separated.
- ETF flows framed as market-plumbing associations, not causal return drivers.
- Monthly PIT market-structure data used for composition, concentration, and turnover only.
- Current-top50 daily cohort marked exploratory and survivorship-biased.
- Selected-major assets use canonical IDs and explicit coverage caveats.

## Required local gates

- `uv sync --all-extras`
- `uv run ruff check src/cqresearch scripts tests`
- `uv run mypy src/cqresearch`
- `uv run pytest`
- `uv run python scripts/run_all.py`
- `uv run python scripts/check_public_surface.py`

## Known non-goals

- No live API dependency is required for the canonical build, but provider exports are local-only and governed by source access.
- No price forecasting, trading strategy, or causal ETF-flow identification is claimed.
- Historical daily point-in-time altseason performance remains deferred until constituent-level daily OHLCV and market-cap history exists.
"""


def reproducibility_report_text() -> str:
    return """# Reproducibility Report

## Maintained commands

```powershell
uv sync --all-extras
uv run ruff check src/cqresearch scripts tests
uv run mypy src/cqresearch
uv run python scripts/run_all.py
uv run pytest
uv run python scripts/check_public_surface.py
```

## Data contract

The local reproducible build reads provider exports from `data_local/raw/` and writes generated feature stores to `data_local/processed/`. Both locations are ignored by Git. Public-safe semantic tables remain under `outputs/tables/`, and source inventories are written to `data_local/metadata/`.

## Determinism

Public CI validates code, committed derived outputs, and public-surface guardrails without requiring licensed local provider exports. On a machine with `data_local/raw/`, the canonical build is run before semantic-output tests so tests can exercise freshly regenerated artifacts. Determinism checks compare generated semantic outputs while excluding timestamp metadata.
"""


def public_readiness_text() -> str:
    return """# Public Readiness

## Public surface

- README embeds exactly six canonical figures.
- Public figures have PNG and SVG renderings.
- No old F-numbered figure gallery is part of the public surface.
- `.env.example` lists variable names only and contains no secret-like assignments.

## Evidence language

- Drop-block delta R-squared is not labeled conventional partial R-squared.
- MVRV is described as a valuation-state diagnostic with mechanical price-state content.
- ETF, liquidation, stablecoin, and DeFi variables are descriptive and timing-sensitive.
- Evidence grades and claim dispositions live in `outputs/tables/evidence_ledger.csv` and `outputs/tables/claim_inventory.csv`.
"""


def final_pr_body_text() -> str:
    return """## Summary

- Replace the old portfolio/v2 public surface with the canonical Crypto Market Dynamics offline build.
- Add semantic feature stores, tables, reports, model cards, docs, data governance, and exactly six public README figures.
- Reframe MVRV, ETF flows, leverage/liquidations, stablecoin/DeFi liquidity, PIT market structure, and selected major assets according to the final evidence standards.

## Verification

- `uv sync --all-extras`
- `uv run ruff check src/cqresearch scripts tests`
- `uv run mypy src/cqresearch`
- `uv run pytest`
- `uv run python scripts/run_all.py`
- `uv run python scripts/check_public_surface.py`

## Guardrails

- No instruction-bundle files are included.
- Raw provider exports remain local-only under ignored `data_local/raw/`.
- Public README embeds exactly six canonical figures.
- ETF-flow, liquidation, data-licensing, and current-top50 cohort claims remain caveated.
"""


def write_licenses(root: Path = PROJECT_ROOT) -> None:
    license_text = """MIT License

Copyright (c) 2026 Crypto Market Dynamics contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    write_md(root / "LICENSE", license_text)
    data_license = """# Data License And Source Notes

The repository code is licensed separately under `LICENSE`.

Tracked data files come from a mix of public, provider-exported, and locally curated sources. `DATA_LICENSE.md` documents known caveats but does not resolve provider redistribution rights.

This project is not affiliated with, endorsed by, or published on behalf of CryptoQuant, Artemis, TradingView, DefiLlama, Farside, AlternativeMe, FRED, or any other data provider.

- FRED macro series are public Federal Reserve Economic Data series with attribution.
- DefiLlama, AlternativeMe, and Farside-derived files are public web/API sources; cite the providers and verify current terms before redistribution.
- CryptoQuant, Artemis, and TradingView exports may carry provider-specific or licensed redistribution restrictions. The repository uses them as curated research inputs and documents reproducibility caveats.
- `data_cache/` is gitignored and is for local raw API/cache payloads only.

No API keys are required for the final offline build. Public users can reproduce generated outputs from the committed curated data, subject to the source-specific redistribution caveats above. See `outputs/report/provider_data_disposition.md` for the concrete public/re-distributable, uncertain/restricted, and derived-only recommended disposition by provider group.
"""
    write_md(root / "DATA_LICENSE.md", data_license)
    contributing = """# Contributing

Run the maintained verification suite before proposing changes:

```powershell
uv sync --all-extras
uv run python scripts/run_all.py
uv run python scripts/check_public_surface.py
uv run pytest
uv run mypy src/cqresearch
uv run ruff check src/cqresearch scripts tests
```

Do not commit secrets, raw cache payloads, or newly licensed raw data without explicit redistribution permission.
"""
    write_md(root / "CONTRIBUTING.md", contributing)


def build_public_figures(root: Path = PROJECT_ROOT) -> list[Path]:
    from cqresearch.viz.public_figures import build_public_figures as build_public_figure_layer

    return build_public_figure_layer(root)


def write_outputs_index(p: BuildPaths) -> None:
    tables = sorted(path.relative_to(p.outputs).as_posix() for path in p.tables.glob("*") if path.is_file())
    figs = sorted(path.relative_to(p.outputs).as_posix() for path in p.public_figures.glob("*.png"))
    reports = sorted(path.relative_to(p.outputs).as_posix() for path in p.report.glob("*.md"))
    cards = sorted(path.relative_to(p.outputs).as_posix() for path in p.model_cards.glob("*.md"))
    text = f"""# Outputs

This is the canonical public output surface for Crypto Market Dynamics.

## Public Figures

{bullet_list(figs)}

## Public Summary Tables

{bullet_list([item for item in tables if item in public_table_names()])}

## Supporting Tables

{bullet_list([item for item in tables if item not in public_table_names()])}

## Reports

{bullet_list(reports)}

## Model Cards

{bullet_list(cards)}

Current-top50 daily cohort outputs, where present, are exploratory and survivorship-biased. PIT market-structure evidence is monthly composition/concentration/turnover only.
"""
    write_md(p.outputs / "README.md", text)


def public_table_names() -> set[str]:
    names = {
        "tables/results_at_a_glance.md",
        "tables/data_source_coverage.csv",
        "tables/provider_data_disposition.csv",
        "tables/valuation_contamination_audit.csv",
        "tables/feature_registry.csv",
        "tables/mvrv_mechanical_link_audit.csv",
        "tables/btc_ex_mvrv_feature_strength.csv",
        "tables/eth_feature_strength.csv",
        "tables/rolling_tradfi_exposures.csv",
        "tables/rolling_exposure_summary.csv",
        "tables/leverage_tail_risk_summary.csv",
        "tables/etf_market_plumbing_summary.csv",
        "tables/stablecoin_defi_liquidity_summary.csv",
        "tables/selected_major_risk_metrics.csv",
        "tables/selected_major_comparable_window_metrics.csv",
        "tables/pit_market_structure_summary.csv",
        "tables/event_response_matrix.csv",
        "tables/local_window_correlation_distribution.csv",
        "tables/robustness_summary.csv",
        "tables/evidence_ledger.csv",
    }
    return names


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- `{item}`" for item in items)


def write_main_readme(root: Path, p: BuildPaths) -> None:
    glance = (p.tables / "results_at_a_glance.md").read_text(encoding="utf-8")
    text = f"""# Crypto Market Dynamics

## Factor, Liquidity, Leverage, and Market-Structure Research

Crypto Market Dynamics is a reproducible research-code project studying how crypto market behavior evolved from 2020-2026 across native valuation state, TradFi co-movement, ETF access, leverage, stablecoin/DeFi state, selected major assets, point-in-time market structure, and BTC/ETH event windows.

The project is descriptive. It is not a price-forecasting system, trading strategy, or causal-identification claim.

## Research Questions

1. How mechanically linked are MVRV and holder-profit metrics to BTC price/returns?
2. After removing mechanically linked valuation-state measures, how did BTC/ETH contemporaneous TradFi exposure and lagged-state associations compare across periods?
3. Are leverage and liquidation variables more informative for volatility/tail stress than average returns?
4. How did ETF access relate to market plumbing and risk integration?
5. How do stablecoin and DeFi state variables relate to BTC/ETH returns and BTC volatility?
6. How do selected major assets differ in volatility, drawdown, and beta after accounting for coverage?
7. How did PIT market composition, concentration, and turnover evolve?

## Results At A Glance

{glance}

## Data

Provider exports are local-only and ignored by Git under `data_local/raw/`. Generated feature stores are local-only under `data_local/processed/`. The public repository ships code, docs, derived semantic outputs, and reproducibility instructions; users with source access can recreate the local layout documented in [docs/data](docs/data).

This repository is not affiliated with CryptoQuant, Artemis, TradingView, DefiLlama, Farside, AlternativeMe, FRED, or other data providers. Data-use caveats are separated in [DATA_LICENSE.md](DATA_LICENSE.md), but that file does not resolve provider redistribution rights. Source coverage is summarized in [data_source_coverage.csv](outputs/tables/data_source_coverage.csv), provider release risk is classified in [provider_data_disposition.csv](outputs/tables/provider_data_disposition.csv), and TVL/OI price-content risk is audited in [valuation_contamination_audit.csv](outputs/tables/valuation_contamination_audit.csv).

## MVRV Mechanics And On-Chain State

![MVRV mechanics](outputs/figures/public/01_mvrv_mechanics.png)

MVRV is a valuation-state diagnostic with mechanical price-state content. Same-day `d_log_mvrv` is excluded from the primary BTC/ETH exposure models; lagged MVRV state appears as conditioning context. The figure separates the same-interval mechanics from lagged-state outcome summaries.

Source: [mvrv_mechanical_link_audit.csv](outputs/tables/mvrv_mechanical_link_audit.csv)

## TradFi Exposure Shift

![TradFi exposure shift](outputs/figures/public/02_tradfi_exposure_shift.png)

The exposure tables split economically distinct families: contemporaneous TradFi co-movement models, lagged-state association models, and ETF-era augmented market-plumbing models. Daily TradFi models use common business-date BTC/ETH returns; weekly TradFi models use Friday-to-Friday returns. Figure 2 uses the pre-specified pre-BTC-ETF versus BTC-ETF-era equity block comparison and should be read as a period comparison, not an ETF effect.

Source: [block_delta_r2.csv](outputs/tables/block_delta_r2.csv), [rolling_tradfi_exposures.csv](outputs/tables/rolling_tradfi_exposures.csv)

## ETF Market Plumbing

![ETF market plumbing](outputs/figures/public/03_etf_market_plumbing.png)

ETF flows are market-plumbing variables with reporting-timing caveats. ETF-era augmented models include flow intensity separately at lag 0 and lag 1. Flow-return grids and absorption ratios are descriptive associations, not causal valuation statements.

Source: [etf_market_plumbing_summary.csv](outputs/tables/etf_market_plumbing_summary.csv)

## Leverage And Liquidation Stress

![Leverage and liquidation stress](outputs/figures/public/04_leverage_tail_stress.png)

Leverage, funding, OI, and liquidation variables are evaluated as stress and volatility-state measures. The headline is the U-shaped Q1/Q3/Q5 tail-rate pattern, not a cherry-picked maximum quintile. Lagged leverage/funding/OI states are separated from same-day liquidation signatures and post-event responses. Liquidations are shown as percent of prior-day OI or basis points of prior-day market cap.

Source: [leverage_tail_risk_summary.csv](outputs/tables/leverage_tail_risk_summary.csv)

## Stablecoin And DeFi Liquidity

Stablecoin and DeFi metrics use the Sunday-ended crypto weekly panel. Stablecoin supply is the cleaner local liquidity-state proxy; raw USD TVL growth is labeled `valuation_sensitive_defi_tvl_growth` because USD TVL embeds deposited-asset price effects. The project does not call proxy changes exogenous liquidity shocks.

Source: [stablecoin_defi_liquidity_summary.csv](outputs/tables/stablecoin_defi_liquidity_summary.csv)

## Point-In-Time Market Structure

![Point-in-time market structure](outputs/figures/public/05_point_in_time_market_structure.png)

The monthly PIT top-200 source is used for composition, concentration, and turnover. The latest observation preserves the real partial snapshot date. The PIT source is not used for daily historical altseason performance.

Source: [pit_market_structure_summary.csv](outputs/tables/pit_market_structure_summary.csv)

## Selected Major Assets

![Selected major asset risk](outputs/figures/public/06_selected_major_asset_risk.png)

Selected major assets use canonical IDs and explicit coverage windows. Current daily constituent coverage begins 2022-12-31/2023 for most selected assets, HYPE is short-history, and Toncoin is sourced only from the canonical `coingecko:the-open-network` local series when present. Comparable-window metrics are reported separately.

Source: [selected_major_risk_metrics.csv](outputs/tables/selected_major_risk_metrics.csv)

## Cycle And Event Atlas

Event windows are descriptive empirical placebo-window tests. The post-10-day convention is `+1` through `+10`, placebo windows have the same block length, and registered-event overlaps are excluded. The small number of events is not enough for forecast rules or causal structural claims. The event matrix is an appendix/gallery output rather than a README figure.

Source: [event_response_matrix.csv](outputs/tables/event_response_matrix.csv)

## Methods And Evidence Standards

Public claims map to [evidence_ledger.csv](outputs/tables/evidence_ledger.csv) and claim dispositions are summarized in [claim_inventory.csv](outputs/tables/claim_inventory.csv). Evidence grades follow the project charter in [research_charter.md](docs/decisions/research_charter.md).

## Limitations

No causal claims are made. MVRV is a valuation-state diagnostic with mechanical price-state content. ETF and liquidation variables are timing-sensitive. Stablecoin/DeFi variables are proxies. Current-top50 daily cohort analysis is exploratory and survivorship-biased. True PIT historical altseason performance is deferred until constituent daily data exists. Provider data redistribution rights remain a public-release risk where marked uncertain/restricted.

## Reproduce

```powershell
uv sync --all-extras
uv run ruff check src/cqresearch scripts tests
uv run mypy src/cqresearch
uv run python scripts/run_all.py
uv run python scripts/build_public_figures.py
uv run pytest
uv run python scripts/check_public_surface.py
```

With source access, recreate:

```text
data_local/
  raw/
  interim/
  processed/
  curated/
  metadata/
```

## Repository Structure

- `data_local/` ignored local provider exports, intermediates, and feature stores.
- `config/` asset, event, feature, and figure registries.
- `src/cqresearch/` maintained data, feature, modeling, analysis, reporting, visualization, and pipeline code.
- `scripts/` thin CLI entry points.
- `outputs/` generated public tables, figures, reports, and model cards.
- `docs/` methodology, data, architecture, and decisions.
- `archive/` historical material excluded from public indexing.
"""
    write_md(root / "README.md", text)


def write_manifest(root: Path, p: BuildPaths) -> Path:
    manifest = {
        "project": "Crypto Market Dynamics",
        "generated_at_utc": utc_stamp(),
        "pipeline": "src/cqresearch/pipelines/final_research.py",
        "public_figures": [f"outputs/figures/public/{item[1]}" for item in PUBLIC_FIGURES],
        "tables": sorted(path.relative_to(root).as_posix() for path in p.tables.glob("*") if path.is_file()),
        "reports": sorted(path.relative_to(root).as_posix() for path in p.report.glob("*.md")),
        "model_cards": sorted(path.relative_to(root).as_posix() for path in p.model_cards.glob("*.md")),
        "guardrails": [
            "Same-day MVRV excluded from primary exposure models.",
            "ETF flow language is market-plumbing association only.",
            "Stablecoin/DeFi liquidity is weekly and proxy-based.",
            "PIT monthly universe used for composition/concentration/turnover only.",
            "Current-top50 daily cohort is exploratory and survivorship-biased.",
        ],
    }
    path = p.outputs / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def check_public_surface(root: Path = PROJECT_ROOT) -> pd.DataFrame:
    p = paths(root)
    rows: list[dict[str, str]] = []
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme)
    allowed = {f"outputs/figures/public/{filename}" for _, filename, _, _, _ in PUBLIC_FIGURES}
    public_pngs = sorted(path.name for path in p.public_figures.glob("*.png"))
    allowed_names = sorted(Path(path).name for path in allowed)
    rows.append({"check": "readme_figure_count", "status": "pass" if len(images) == 6 else "fail", "detail": str(len(images))})
    rows.append(
        {
            "check": "public_png_count",
            "status": "pass" if public_pngs == allowed_names else "fail",
            "detail": ";".join(sorted(set(public_pngs) ^ set(allowed_names))),
        }
    )
    rows.append({"check": "readme_public_figures_match_registry", "status": "pass" if set(images) == allowed else "fail", "detail": ";".join(sorted(set(images) ^ allowed))})
    rows.append({"check": "no_contact_sheet_in_readme", "status": "fail" if "public_contact_sheet" in readme.lower() else "pass", "detail": "README"})
    old_numbered = [image for image in images if re.search(r"/[FT]\d+[^/]*\.(?:png|svg)$", image)]
    rows.append({"check": "no_old_numbered_figures_in_readme", "status": "pass" if not old_numbered else "fail", "detail": ";".join(old_numbered)})
    banned_figure_terms = ["dashboard", "contact_sheet", "gap", "triage", "before", "legacy"]
    for term in banned_figure_terms:
        offenders = [name for name in public_pngs if term in name.lower()]
        rows.append({"check": f"public_figure_name_no_{term}", "status": "pass" if not offenders else "fail", "detail": ";".join(offenders)})
    for image in images:
        path = root / image
        exists = path.exists() and path.stat().st_size > 0
        rows.append({"check": "figure_exists", "status": "pass" if exists else "fail", "detail": image})
        if exists:
            size_kb = path.stat().st_size / 1024
            rows.append({"check": "figure_min_size_50kb", "status": "pass" if size_kb >= 50 else "fail", "detail": f"{image}={size_kb:.1f}KB"})
            try:
                pixels = mpimg.imread(path)
                width_px = int(pixels.shape[1])
            except Exception as exc:  # pragma: no cover - guardrail detail only
                width_px = 0
                rows.append({"check": "figure_readable_for_dimensions", "status": "fail", "detail": f"{image}: {exc}"})
            rows.append({"check": "figure_width_gt_1200px", "status": "pass" if width_px > 1200 else "fail", "detail": f"{image}={width_px}px"})
    banned_terms = ["portfolio_v2", "v2.1", "v2.2", "career", "recruiter", "LinkedIn", "manager prompt", "Shapley", "Bai-Perron"]
    for term in banned_terms:
        rows.append({"check": f"banned_term_{term}", "status": "fail" if term.lower() in readme.lower() else "pass", "detail": term})
    prohibited = [" caused ", " proves ", " predicts ", " price target "]
    for term in prohibited:
        rows.append({"check": f"prohibited_language_{term.strip()}", "status": "fail" if term in readme.lower() else "pass", "detail": term.strip()})
    rows.append({"check": "data_license_link", "status": "pass" if "DATA_LICENSE.md" in readme else "fail", "detail": "README"})
    rows.append({"check": "current_cohort_caveat", "status": "pass" if "survivorship-biased" in readme and "deferred" in readme else "fail", "detail": "current-top50"})
    for table in sorted(public_table_names()):
        table_path = p.outputs / table
        rows.append({"check": "canonical_table_nonempty", "status": "pass" if table_path.exists() and table_path.stat().st_size > 0 else "fail", "detail": table})
    secret_patterns = ["gho_", "sk-", "DEFILLAMA_API_KEY=", "CMC_API_KEY="]
    scan_text = readme
    for file in [root / ".env.example", root / "outputs" / "manifest.json"]:
        if file.exists():
            scan_text += "\n" + file.read_text(encoding="utf-8", errors="ignore")
    for pattern in secret_patterns:
        rows.append({"check": f"secret_pattern_{pattern}", "status": "fail" if pattern in scan_text else "pass", "detail": pattern})
    result = pd.DataFrame(rows)
    status = "PASS" if (result["status"] == "fail").sum() == 0 else "FAIL"
    write_md(p.report / "market_structure_public_surface_check.md", f"# Public Surface Check\n\nVerdict: {status}\n\n{result.to_markdown(index=False)}")
    if status == "FAIL":
        raise SystemExit(result[result["status"] == "fail"].to_string(index=False))
    return result


def run_all(root: Path = PROJECT_ROOT) -> None:
    p = paths(root)
    ensure_output_dirs(p)
    clean_legacy_outputs(p)
    write_config_files(root)
    write_licenses(root)
    build_data_inventory(root)
    build_feature_store(root)
    build_analysis_outputs(root)
    build_public_figures(root)
    write_outputs_index(p)
    write_main_readme(root, p)
    write_manifest(root, p)
    check_public_surface(root)
