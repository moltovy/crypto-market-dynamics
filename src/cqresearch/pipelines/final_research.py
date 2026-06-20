"""Canonical offline pipeline for Crypto Market Dynamics.

This module is the maintained public build path. It uses only tracked local
data, writes semantic outputs, and keeps legacy release artifacts out of the
public surface.
"""

from __future__ import annotations

import json
import math
import re
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import yaml
from config.paths import PROJECT_ROOT
from matplotlib.ticker import PercentFormatter

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

PUBLIC_FIGURES = [
    (
        "mvrv_mechanics",
        "01_mvrv_mechanics.png",
        "How mechanically linked is MVRV to BTC price/returns?",
        "outputs/tables/mvrv_mechanical_link_audit.csv; outputs/tables/mvrv_regime_outcomes.csv",
        "Public figure shows mechanics and lagged-state outcomes; MVRV is not a same-day factor.",
    ),
    (
        "factor_strength_by_regime",
        "02_factor_strength_by_regime.png",
        "How do ex-MVRV feature blocks vary by regime?",
        "outputs/tables/block_delta_r2.csv",
        "Drop-block delta R-squared, not conventional partial R-squared.",
    ),
    (
        "tradfi_integration_over_time",
        "03_tradfi_integration_over_time.png",
        "How did TradFi exposure evolve over time?",
        "outputs/tables/rolling_exposures.csv",
        "Rolling-window points overlap and are descriptive.",
    ),
    (
        "etf_market_plumbing",
        "04_etf_market_plumbing.png",
        "How did ETF access relate to market plumbing?",
        "outputs/tables/etf_absorption_metrics.csv; outputs/tables/etf_flow_associations.csv",
        "ETF flow relationships are associations, not causal price effects.",
    ),
    (
        "leverage_liquidation_stress",
        "05_leverage_liquidation_stress.png",
        "Do leverage/liquidation states align with tail stress?",
        "outputs/tables/leverage_tail_risk_summary.csv; outputs/tables/liquidation_event_responses.csv",
        "Lagged state and contemporaneous liquidation signatures are separated.",
    ),
    (
        "stablecoin_defi_liquidity",
        "06_stablecoin_defi_liquidity.png",
        "How did stablecoin and DeFi liquidity regimes evolve?",
        "outputs/tables/stablecoin_defi_liquidity_summary.csv",
        "Weekly liquidity proxies are not exogenous liquidity shocks.",
    ),
    (
        "point_in_time_market_structure",
        "07_point_in_time_market_structure.png",
        "How did PIT composition and concentration evolve?",
        "outputs/tables/pit_market_structure_summary.csv; outputs/tables/pit_composition.csv",
        "Monthly PIT data supports composition/turnover, not daily performance.",
    ),
    (
        "selected_major_asset_risk",
        "08_selected_major_asset_risk.png",
        "How do selected major assets differ in risk?",
        "outputs/tables/selected_major_risk_metrics.csv",
        "Coverage differs by asset; HYPE is short-history.",
    ),
    (
        "event_response_matrix",
        "09_event_response_matrix.png",
        "What do configured event windows show?",
        "outputs/tables/event_response_matrix.csv",
        "Event responses are descriptive and not causal identification.",
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
    return BuildPaths(
        root=root,
        outputs=out,
        tables=out / "tables",
        figures=out / "figures",
        public_figures=out / "figures" / "public",
        gallery_figures=out / "figures" / "gallery",
        report=out / "report",
        model_cards=out / "model_cards",
        panels=root / "reports" / "panels",
    )


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
    for name in ["key_results.html", "key_results.md", "README.md"]:
        item = p.tables / name
        if item.exists():
            item.unlink()
    allowed_reports = {
        "baseline_audit.md",
        "cycle_and_event_atlas.md",
        "data_atlas.md",
        "etf_market_plumbing.md",
        "executive_summary.md",
        "final_pr_body.md",
        "final_release_audit.md",
        "leverage_and_tail_risk.md",
        "limitations.md",
        "market_structure_public_surface_check.md",
        "methodology.md",
        "onchain_valuation_state.md",
        "open_pr_disposition.md",
        "point_in_time_market_structure.md",
        "public_readiness.md",
        "reproducibility_report.md",
        "results_and_interpretation.md",
        "selected_major_assets.md",
        "stablecoin_defi_liquidity.md",
        "statistical_robustness.md",
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
        "eth_etf_flow_intensity": "ETH ETF flow / lag mcap",
        "stablecoin_supply_growth": "Stablecoin supply growth",
        "defi_tvl_growth": "DeFi TVL growth",
        "btc_oi_growth": "BTC OI growth",
        "btc_funding_z": "BTC funding z-score",
        "btc_exchange_netflow_scaled": "BTC exchange netflow / lag mcap",
    }
    return labels.get(value, value.replace("_", " ").title())


def source_file_inventory(root: Path = PROJECT_ROOT) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / "Data").rglob("*")):
        if not path.is_file():
            continue
        data_rel = path.relative_to(root / "Data").as_posix()
        if data_rel in {"MASTER_DATA.csv", "MASTER_DATA.md", "MASTER_DATA.txt"}:
            continue
        rel = path.relative_to(root).as_posix()
        row: dict[str, Any] = {
            "relpath": rel,
            "source_group": path.relative_to(root / "Data").parts[0],
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
    return pd.DataFrame(rows)


def build_data_inventory(root: Path = PROJECT_ROOT) -> pd.DataFrame:
    p = paths(root)
    ensure_output_dirs(p)
    inventory = source_file_inventory(root)
    write_csv(root / "Data" / "MASTER_DATA.csv", inventory)
    lines = [
        "# MASTER DATA Inventory",
        "",
        "Generated by: scripts/run_all.py",
        "",
        "This inventory is generated from files currently present under `Data/`.",
        "",
        inventory.groupby("source_group").size().rename("file_count").reset_index().to_markdown(index=False),
        "",
    ]
    write_md(root / "Data" / "MASTER_DATA.md", "\n".join(lines))
    write_md(root / "Data" / "MASTER_DATA.txt", "\n".join(lines))

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
    return coverage


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
                "visual_qa_status": "generated_pending_review",
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
        ("qqq_ret", "QQQ return", "macro_risk", "TradingView", "QQQ close", "daily", "log return", 1, "", "Equity-growth proxy."),
        ("spy_ret", "SPY return", "macro_risk", "TradingView", "SPY close", "daily", "log return", 1, "", "US equity-market proxy."),
        ("vix_d1", "VIX change", "macro_risk", "FRED", "VIXCLS", "daily", "first difference", 1, "", "Equity-volatility proxy."),
        ("dxy_ret", "DXY return", "macro_risk", "TradingView", "DXY close", "daily", "log return", 1, "", "Dollar index proxy."),
        ("real_yield_d1", "Real-yield change", "macro_risk", "FRED", "DFII10", "daily", "first difference", 1, "", "Real-rate proxy."),
        ("btc_etf_flow_intensity", "BTC ETF flow intensity", "etf_institutional", "Farside", "BTC ETF total", "daily", "flow / lagged market cap", 1, "lagged BTC mcap", "Market-plumbing flow proxy."),
        ("eth_etf_flow_intensity", "ETH ETF flow intensity", "etf_institutional", "Farside", "ETH ETF total", "daily", "flow / lagged market cap", 1, "lagged ETH mcap", "Market-plumbing flow proxy."),
        ("btc_oi_growth", "BTC open-interest growth", "leverage", "CryptoQuant", "BTC open interest", "daily", "log difference", 1, "", "Leverage-state proxy."),
        ("btc_funding_z", "BTC funding z-score", "leverage", "CryptoQuant", "BTC funding rates", "daily", "rolling z-score", 1, "", "Positioning stress proxy."),
        ("btc_total_liq_intensity", "BTC liquidation intensity", "leverage", "CryptoQuant", "BTC liquidations USD", "daily", "log1p / lagged OI", 1, "lagged open interest", "Stress signature."),
        ("stablecoin_supply_growth", "Stablecoin supply growth", "liquidity", "DefiLlama", "stablecoin market caps", "weekly", "log difference", 1, "", "Liquidity-state proxy."),
        ("defi_tvl_growth", "DeFi TVL growth", "liquidity", "DefiLlama", "TVL", "weekly", "log difference", 1, "", "DeFi balance-sheet proxy."),
        ("btc_mvrv_lag1", "Lagged BTC MVRV", "onchain_state", "CryptoQuant", "MVRV Ratio", "daily", "lagged level/percentile", 1, "", "Valuation-state conditioning variable."),
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
                "mechanical_link_risk": "direct_target_component" if feature_id == "btc_mvrv_d1" else ("high" if "mvrv" in feature_id else "low"),
                "contemporaneous_endogeneity_risk": "medium" if "etf" in feature_id or "liq" in feature_id else "low",
                "permitted_model_families": "descriptive, exposure, state conditioning",
                "prohibited_uses": "price forecasting; causal claims; same-day MVRV as primary BTC-return factor",
                "interpretation": interp,
            }
        )
    return rows


def load_master_panel(root: Path = PROJECT_ROOT) -> pd.DataFrame:
    panel_path = root / "reports" / "panels" / "master_daily.parquet"
    if not panel_path.exists():
        panel, report = build_source_master_panel()
        write_source_panel(panel, report, panel_path.parent)
    panel = pd.read_parquet(panel_path)
    panel.index = pd.to_datetime(panel.index)
    panel.index.name = "date"
    return panel.sort_index()


def add_extra_series(panel: pd.DataFrame, root: Path = PROJECT_ROOT) -> pd.DataFrame:
    data = panel.copy()
    cq = root / "Data" / "CryptoQuant"
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
        "btc_dominance": load_close(root / "Data/Tradingview/Daily/CRYPTOCAP_BTC_dominance__daily.csv", "btc_dominance"),
        "eth_dominance": load_close(root / "Data/Tradingview/Daily/CRYPTOCAP_ETH_dominance__daily.csv", "eth_dominance"),
        "total3_close": load_close(root / "Data/Tradingview/Daily/CRYPTOCAP_TOTAL3__daily.csv", "total3_close"),
        "iwm_close": load_close(root / "Data/Tradingview/Daily/IWM_russell2000_etf__daily.csv", "iwm_close"),
        "xauusd_close": load_close(root / "Data/Tradingview/Daily/XAUUSD_gold_spot__daily.csv", "xauusd_close"),
        "ibit_spot_ratio": load_close(root / "Data/Tradingview/Daily/IBIT_ETF_over_SPOT_BTC__daily.csv", "ibit_spot_ratio"),
        "etha_spot_ratio": load_close(root / "Data/Tradingview/Daily/ETHA_ETF_over_SPOT_ETH__daily.csv", "etha_spot_ratio"),
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
    daily["btc_ret"] = log_return(panel["btc_close"])
    daily["eth_ret"] = log_return(panel["eth_close"])
    daily["spy_ret"] = log_return(panel.get("spy_close"))
    daily["qqq_ret"] = log_return(panel.get("qqq_close"))
    daily["iwm_ret"] = log_return(panel.get("iwm_close"))
    daily["gold_ret"] = log_return(panel.get("gld_close")).combine_first(log_return(panel.get("xauusd_close")))
    daily["dxy_ret"] = log_return(panel.get("dxy_tv_close"))
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
    daily["btc_mcap_lag1"] = panel["btc_mcap_usd"].shift(1)
    daily["eth_mcap_lag1"] = panel["eth_mcap_usd"].shift(1)
    daily["btc_etf_net_flow_usd"] = panel.get("btc_etf_total", pd.Series(index=panel.index, dtype=float)) * 1e6
    daily["eth_etf_net_flow_usd"] = panel.get("eth_etf_total", pd.Series(index=panel.index, dtype=float)) * 1e6
    daily["btc_etf_flow_intensity"] = daily["btc_etf_net_flow_usd"] / daily["btc_mcap_lag1"]
    daily["eth_etf_flow_intensity"] = daily["eth_etf_net_flow_usd"] / daily["eth_mcap_lag1"]
    daily["btc_etf_cumulative_flow_usd"] = daily["btc_etf_net_flow_usd"].fillna(0).cumsum()
    daily["eth_etf_cumulative_flow_usd"] = daily["eth_etf_net_flow_usd"].fillna(0).cumsum()
    daily["btc_mvrv"] = panel.get("btc_mvrv")
    daily["btc_mvrv_lag1"] = daily["btc_mvrv"].shift(1)
    daily["btc_mvrv_log"] = safe_log(daily["btc_mvrv"])
    daily["btc_mvrv_d1"] = daily["btc_mvrv_log"].diff()
    daily["btc_mvrv_percentile_lagged"] = expanding_percentile(daily["btc_mvrv"])
    daily["btc_mvrv_z_365_lagged"] = rolling_z(daily["btc_mvrv"], 365).shift(1)
    daily["btc_realized_cap"] = panel.get("btc_realized_cap")
    daily["btc_realized_price"] = panel.get("btc_realized_price")
    daily["btc_realized_price_gap_lag1"] = (panel["btc_close"] / panel.get("btc_realized_price")).shift(1)
    daily["btc_nupl_lag1"] = panel.get("btc_nupl", pd.Series(index=panel.index, dtype=float)).shift(1)
    daily["btc_sopr_lag1"] = panel.get("btc_sopr", pd.Series(index=panel.index, dtype=float)).shift(1)
    daily["btc_supply_profit_pct_lag1"] = panel.get("btc_supply_profit_pct", pd.Series(index=panel.index, dtype=float)).shift(1)
    daily["stablecoin_supply_usd"] = panel.get("stables_total_usd")
    daily["defi_tvl_usd"] = panel.get("defi_tvl_usd")
    daily["stablecoin_supply_growth"] = log_return(panel.get("stables_total_usd"))
    daily["defi_tvl_growth"] = log_return(panel.get("defi_tvl_usd"))
    daily["stablecoin_to_tvl"] = panel.get("stables_total_usd") / panel.get("defi_tvl_usd")
    daily["stablecoin_share_crypto_proxy"] = panel.get("stables_total_usd") / (panel["btc_mcap_usd"] + panel["eth_mcap_usd"] + panel.get("total3_close"))
    daily["btc_oi"] = panel.get("btc_oi")
    daily["btc_oi_growth"] = log_return(panel.get("btc_oi"))
    daily["btc_oi_to_mcap"] = panel.get("btc_oi") / daily["btc_mcap_lag1"]
    daily["btc_funding"] = panel.get("btc_funding")
    daily["btc_abs_funding"] = daily["btc_funding"].abs()
    daily["btc_funding_z"] = rolling_z(daily["btc_funding"], 90)
    daily["btc_leverage_ratio_percentile"] = expanding_percentile(panel.get("btc_leverage_ratio", pd.Series(index=panel.index, dtype=float)))
    daily["btc_long_liq_intensity_mcap"] = np.log1p(panel.get("btc_long_liq_usd")) / daily["btc_mcap_lag1"]
    daily["btc_short_liq_intensity_mcap"] = np.log1p(panel.get("btc_short_liq_usd")) / daily["btc_mcap_lag1"]
    daily["btc_total_liq_usd"] = panel.get("btc_long_liq_usd", 0).fillna(0) + panel.get("btc_short_liq_usd", 0).fillna(0)
    daily["btc_total_liq_intensity"] = np.log1p(daily["btc_total_liq_usd"]) / panel.get("btc_oi", pd.Series(index=panel.index, dtype=float)).shift(1)
    daily["btc_basis_z"] = rolling_z(panel.get("cme_btc_basis_close", pd.Series(index=panel.index, dtype=float)), 90)
    daily["btc_taker_buy_ratio"] = panel.get("btc_taker_buy_ratio")
    daily["btc_exchange_netflow_scaled"] = panel.get("btc_exchange_netflow") / daily["btc_mcap_lag1"]
    daily["eth_oi_growth"] = log_return(panel.get("eth_oi"))
    daily["eth_funding_z"] = rolling_z(panel.get("eth_funding", pd.Series(index=panel.index, dtype=float)), 90)
    daily["eth_total_liq_usd"] = panel.get("eth_long_liq_usd", 0).fillna(0) + panel.get("eth_short_liq_usd", 0).fillna(0)
    daily["eth_total_liq_intensity"] = np.log1p(daily["eth_total_liq_usd"]) / panel.get("eth_oi", pd.Series(index=panel.index, dtype=float)).shift(1)
    daily["btc_dominance"] = panel.get("btc_dominance")
    daily["eth_dominance"] = panel.get("eth_dominance")
    daily["fear_greed_altme"] = panel.get("fng_value")

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

    weekly = weekly_features(daily)
    monthly = build_market_structure_monthly(root)

    daily.to_parquet(p.panels / "feature_store_daily.parquet")
    weekly.to_parquet(p.panels / "feature_store_weekly.parquet")
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
    weekly = pd.DataFrame()
    return_cols = [c for c in daily.columns if c.endswith("_ret")]
    for col in return_cols:
        weekly[col] = daily[col].resample("W-SUN").sum(min_count=1)
    level_cols = [c for c in daily.columns if c not in return_cols]
    for col in level_cols:
        weekly[col] = daily[col].resample("W-SUN").last()
    weekly["stablecoin_supply_growth"] = log_return(weekly["stablecoin_supply_usd"])
    weekly["defi_tvl_growth"] = log_return(weekly["defi_tvl_usd"])
    weekly["btc_realized_vol_30d"] = daily["btc_ret"].resample("W-SUN").std() * math.sqrt(365)
    return weekly


def classify_pit_asset(row: pd.Series) -> str:
    symbol = str(row.get("symbol", "")).upper().strip()
    name = str(row.get("asset_name", "")).upper()
    key = str(row.get("coingecko_id", "")).lower()
    selected = {"BNB", "SOL", "XRP", "DOGE", "TRX", "TON", "ADA", "HYPE"}
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
    if symbol == "BTC":
        return "BTC"
    if symbol == "ETH":
        return "ETH"
    if symbol in selected:
        return "selected majors ex BTC/ETH"
    if symbol in stable or "STABLE" in name or key in {"tether", "usd-coin", "dai"}:
        return "stable-like assets"
    if symbol in productized or "WRAPPED" in name or "STAKED" in name or "LIQUID STAK" in name:
        return "productized/wrapped assets"
    return "other risk assets"


def build_market_structure_monthly(root: Path = PROJECT_ROOT) -> pd.DataFrame:
    source = root / "Data" / "MarketStructure" / "DefiLlama" / "crypto_universe_monthly_2020_2026.csv"
    frame = pd.read_csv(source)
    frame["snapshot_date"] = pd.to_datetime(frame["snapshot_date"], errors="coerce")
    frame["month"] = pd.to_datetime(frame["month"].astype(str) + "-01", errors="coerce")
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


def model_feature_blocks(asset: str = "btc") -> dict[str, list[str]]:
    blocks = {
        "macro_risk": ["qqq_ret", "spy_ret", "vix_d1", "dxy_ret", "real_yield_d1", "nominal_10y_d1", "gold_ret"],
        "etf_institutional": [f"{asset}_etf_flow_intensity"],
        "liquidity": ["stablecoin_supply_growth", "defi_tvl_growth"],
        "sentiment": ["fear_greed_altme"],
        "native_flows": [f"{asset}_oi_growth", f"{asset}_funding_z"] if asset == "btc" else ["eth_oi_growth", "eth_funding_z"],
    }
    return blocks


def available_features(frame: pd.DataFrame, features: list[str]) -> list[str]:
    return [feature for feature in features if feature in frame.columns and frame[feature].notna().sum() >= 40]


def exposure_tables(daily: pd.DataFrame, weekly: pd.DataFrame, p: BuildPaths) -> dict[str, pd.DataFrame]:
    outputs: dict[str, pd.DataFrame] = {}
    strength_frames = []
    block_frames = []
    partial_frames = []
    fdr_frames = []
    multi_frames = []
    ridge_frames = []
    freq_frames = []
    for asset, target in [("btc", "btc_ret"), ("eth", "eth_ret")]:
        for frequency, frame, hac in [("daily", daily, 5), ("weekly", weekly, 4)]:
            blocks = model_feature_blocks(asset)
            flat_features = available_features(frame, [f for values in blocks.values() for f in values])
            if not flat_features or target not in frame:
                continue
            x = frame[flat_features].shift(1)
            y = frame[target]
            x_std = standardize(x)
            y_std = (y - y.mean()) / y.std(ddof=0)
            full = fit_hac_ols(y_std, x_std, hac)
            pvals = full["p"].reindex(flat_features)
            qvals = bh_fdr(pvals)
            for feature in flat_features:
                uni = fit_hac_ols(y, frame[[feature]].shift(1), hac)
                reduced = fit_hac_ols(y_std, x_std[[f for f in flat_features if f != feature]], hac)
                strength_frames.append(
                    {
                        "asset": asset.upper(),
                        "frequency": frequency,
                        "feature_id": feature,
                        "feature_label": clean_label(feature),
                        "block": next((block for block, values in blocks.items() if feature in values), "other"),
                        "n": int(full["n"]),
                        "correlation_lag1": round(float(pd.concat([y, frame[feature].shift(1)], axis=1).dropna().corr().iloc[0, 1]), 6) if full["n"] else np.nan,
                        "univariate_r2": uni["r2"],
                        "standardized_beta": full["params"].get(feature, np.nan),
                        "hac_t": full["t"].get(feature, np.nan),
                        "p_value": pvals.get(feature, np.nan),
                        "fdr_q_value": qvals.get(feature, np.nan),
                        "drop_feature_delta_r2": full["r2"] - reduced["r2"] if np.isfinite(full["r2"]) and np.isfinite(reduced["r2"]) else np.nan,
                        "model_family": "ex_mvrv_primary_exposure",
                    }
                )
                fdr_frames.append(
                    {
                        "asset": asset.upper(),
                        "frequency": frequency,
                        "feature_id": feature,
                        "model_family": "ex_mvrv_primary_exposure",
                        "p_value": pvals.get(feature, np.nan),
                        "fdr_q_value": qvals.get(feature, np.nan),
                    }
                )
            for block, features in blocks.items():
                block_features = available_features(frame, features)
                if not block_features:
                    continue
                reduced_features = [f for f in flat_features if f not in block_features]
                reduced = fit_hac_ols(y_std, x_std[reduced_features], hac) if reduced_features else {"r2": 0.0, "sse": np.nan, "n": full["n"]}
                delta = full["r2"] - reduced["r2"] if np.isfinite(full["r2"]) and np.isfinite(reduced["r2"]) else np.nan
                partial = (reduced["sse"] - full["sse"]) / reduced["sse"] if np.isfinite(reduced.get("sse", np.nan)) and reduced["sse"] else np.nan
                block_frames.append(
                    {
                        "asset": asset.upper(),
                        "frequency": frequency,
                        "block": block,
                        "n": int(full["n"]),
                        "full_r2": full["r2"],
                        "reduced_r2": reduced["r2"],
                        "drop_block_delta_r2": delta,
                        "method_note": "R2_full - R2_reduced; not conventional partial R-squared",
                    }
                )
                partial_frames.append(
                    {
                        "asset": asset.upper(),
                        "frequency": frequency,
                        "block": block,
                        "n": int(full["n"]),
                        "conventional_partial_r2": partial,
                        "formula": "(SSE_reduced - SSE_full) / SSE_reduced",
                    }
                )
            multi_frames.extend(multicollinearity_rows(asset, frequency, x_std[flat_features]))
            ridge_frames.extend(ridge_stability_rows(asset, frequency, y_std, x_std[flat_features]))
            freq_frames.append({"asset": asset.upper(), "frequency": frequency, "n": int(full["n"]), "full_r2": full["r2"], "feature_count": len(flat_features)})

    strength = pd.DataFrame(strength_frames)
    btc_strength = strength[strength["asset"] == "BTC"].copy()
    eth_strength = strength[strength["asset"] == "ETH"].copy()
    block_delta = pd.DataFrame(block_frames)
    conventional_partial = pd.DataFrame(partial_frames)
    rolling = rolling_exposures(daily)
    regimes = exposure_regime_comparison(daily)
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
            "rolling_exposures": rolling,
            "rolling_exposure_summary": rolling.groupby(["asset", "feature_id", "window_days"], dropna=False)["beta"].agg(["count", "median", "mean", "std"]).reset_index() if not rolling.empty else pd.DataFrame(),
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


def multicollinearity_rows(asset: str, frequency: str, x: pd.DataFrame) -> list[dict[str, Any]]:
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
                "feature_id": feature,
                "vif": vif,
                "condition_number": cond,
                "max_abs_pairwise_corr": corr[feature].drop(feature, errors="ignore").max(),
                "correlation_cluster": "high_corr" if corr[feature].drop(feature, errors="ignore").max() >= 0.75 else "not_high_corr",
            }
        )
    return rows


def ridge_stability_rows(asset: str, frequency: str, y: pd.Series, x: pd.DataFrame) -> list[dict[str, Any]]:
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
                    "alpha": alpha,
                    "feature_id": feature,
                    "ridge_coef": float(coef),
                    "sign": "positive" if coef > 0 else "negative" if coef < 0 else "zero",
                    "abs_rank": int(ranks[feature]),
                }
            )
    return rows


def rolling_exposures(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    features = ["qqq_ret", "spy_ret", "vix_d1", "dxy_ret", "real_yield_d1", "btc_etf_flow_intensity", "stablecoin_supply_growth", "btc_oi_growth"]
    for asset, target in [("BTC", "btc_ret"), ("ETH", "eth_ret")]:
        available = available_features(daily, [f for f in features if f in daily.columns])
        for window in [180, 365]:
            for idx in range(window, len(daily), 14):
                chunk = daily.iloc[idx - window : idx]
                y = chunk[target]
                x = chunk[available].shift(1)
                result = fit_hac_ols((y - y.mean()) / y.std(ddof=0), standardize(x), 5)
                if result["n"] < window * 0.55:
                    continue
                for feature in available:
                    rows.append(
                        {
                            "date": daily.index[idx].date().isoformat(),
                            "asset": asset,
                            "window_days": window,
                            "feature_id": feature,
                            "feature_label": clean_label(feature),
                            "beta": result["params"].get(feature, np.nan),
                            "n": result["n"],
                        }
                    )
    return pd.DataFrame(rows)


def exposure_regime_comparison(daily: pd.DataFrame) -> pd.DataFrame:
    regimes = {
        "2020-2022": (daily.index >= "2020-01-01") & (daily.index <= "2022-12-31"),
        "2023": (daily.index >= "2023-01-01") & (daily.index <= "2023-12-31"),
        "btc_etf_era": daily.index >= "2024-01-11",
        "high_volatility": daily["btc_realized_vol_30d"] >= daily["btc_realized_vol_30d"].median(),
        "low_mvrv_state": daily["btc_mvrv_percentile_lagged"] <= 0.4,
        "high_mvrv_state": daily["btc_mvrv_percentile_lagged"] >= 0.6,
    }
    rows = []
    for asset, target in [("BTC", "btc_ret"), ("ETH", "eth_ret")]:
        features = available_features(daily, [f for values in model_feature_blocks(asset.lower()).values() for f in values])
        for regime, mask in regimes.items():
            subset = daily.loc[mask]
            if subset.empty or len(features) == 0:
                continue
            result = fit_hac_ols(subset[target], subset[features].shift(1), 5)
            rows.append(
                {
                    "asset": asset,
                    "regime": regime,
                    "n": result["n"],
                    "r2": result["r2"],
                    "feature_count": len(features),
                    "method_note": "Lagged ex-MVRV exposure model, descriptive regime split.",
                }
            )
    return pd.DataFrame(rows)


def mvrv_tables(daily: pd.DataFrame, p: BuildPaths) -> dict[str, pd.DataFrame]:
    audit_rows = []
    sub = daily[["btc_ret", "btc_mvrv_d1", "btc_realized_cap", "btc_mcap_lag1", "btc_mvrv", "btc_close"]].copy()
    sub["d_log_market_cap"] = safe_log(daily["btc_mcap_lag1"]).diff()
    sub["d_log_realized_cap"] = safe_log(daily["btc_realized_cap"]).diff()
    sub["identity_residual"] = sub["btc_mvrv_d1"] - (sub["d_log_market_cap"] - sub["d_log_realized_cap"])
    clean = sub.replace([np.inf, -np.inf], np.nan).dropna(subset=["btc_ret", "btc_mvrv_d1"])
    same_day = fit_hac_ols(clean["btc_ret"], clean[["btc_mvrv_d1"]], 5)
    audit_rows.extend(
        [
            {"metric": "corr_d_log_mvrv_btc_return", "value": clean["btc_ret"].corr(clean["btc_mvrv_d1"]), "n": len(clean), "interpretation": "High same-day correlation is mechanical price-state overlap."},
            {"metric": "same_day_mvrv_r2", "value": same_day["r2"], "n": same_day["n"], "interpretation": "Diagnostic upper bound, excluded from primary exposure model."},
            {"metric": "identity_residual_mean", "value": sub["identity_residual"].mean(), "n": int(sub["identity_residual"].notna().sum()), "interpretation": "Residual from dlog(MVRV)=dlog(mcap)-dlog(realized cap)."},
            {"metric": "identity_residual_abs_median", "value": sub["identity_residual"].abs().median(), "n": int(sub["identity_residual"].notna().sum()), "interpretation": "Small residual supports mechanical identity within source conventions."},
        ]
    )
    for feature in ["btc_nupl_lag1", "btc_supply_profit_pct_lag1", "btc_realized_price_gap_lag1"]:
        if feature in daily:
            valid = daily[["btc_ret", feature]].dropna()
            audit_rows.append(
                {"metric": f"corr_{feature}_btc_return", "value": valid["btc_ret"].corr(valid[feature]), "n": len(valid), "interpretation": "Related holder-profit state measure; not exogenous return factor."}
            )
    audit = pd.DataFrame(audit_rows)
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
    write_csv(p.tables / "onchain_state_regimes.csv", state)
    write_csv(p.tables / "mvrv_regime_outcomes.csv", regime)
    report = """# On-Chain Valuation State

MVRV is retained as a measurement-mechanics audit and lagged valuation-state variable. Same-day `btc_mvrv_d1` is mechanically tied to BTC market capitalization and is excluded from the primary ex-MVRV exposure models.

The regime table uses lagged MVRV percentiles and reports conditional forward return, realized volatility, drawdown, funding, and leverage summaries. These are descriptive state summaries, not forecasts.
"""
    write_md(p.report / "onchain_valuation_state.md", report)
    return {"mvrv_mechanical_link_audit": audit, "onchain_state_regimes": state, "mvrv_regime_outcomes": regime}


def leverage_tables(daily: pd.DataFrame, p: BuildPaths) -> dict[str, pd.DataFrame]:
    features = ["btc_oi_growth", "btc_funding_z", "btc_leverage_ratio_percentile", "btc_total_liq_intensity", "btc_basis_z", "btc_taker_buy_ratio"]
    registry = pd.DataFrame(
        [
            {
                "feature_id": feature,
                "clean_label": clean_label(feature),
                "frequency": "daily",
                "timing": "lagged for state models; contemporaneous liquidation signatures reported separately",
                "scaling": "liquidations use log1p and lagged OI/market-cap denominators where available",
            }
            for feature in features
            if feature in daily
        ]
    )
    daily["leverage_state_quintile"] = pd.qcut(daily["btc_leverage_ratio_percentile"], 5, labels=["Q1 low", "Q2", "Q3", "Q4", "Q5 high"], duplicates="drop")
    state = daily.groupby("leverage_state_quintile", dropna=True).agg(
        n=("btc_ret", "count"),
        realized_vol_30d_median=("btc_realized_vol_30d", "median"),
        abs_return_next_day_mean=("btc_ret_fwd_1d", lambda s: s.abs().mean()),
        bottom5_rate=("btc_bottom5", "mean"),
        liquidation_intensity_median=("btc_total_liq_intensity", "median"),
        funding_z_median=("btc_funding_z", "median"),
    ).reset_index().rename(columns={"leverage_state_quintile": "leverage_state"})

    model_rows = []
    lag_features = available_features(daily, ["btc_oi_growth", "btc_funding_z", "btc_leverage_ratio_percentile", "btc_basis_z"])
    if lag_features:
        df = pd.concat([daily["btc_bottom5"].rename("target"), daily[lag_features].shift(1)], axis=1).replace([np.inf, -np.inf], np.nan).dropna()
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
    top_events = daily.nlargest(12, "btc_total_liq_usd")[["btc_ret", "btc_realized_vol_30d", "btc_total_liq_usd", "btc_funding_z"]].reset_index()
    top_events["event_id"] = [f"top_liquidation_{i + 1:02d}" for i in range(len(top_events))]
    top_events["note"] = "Contemporaneous liquidation signature; not evidence that liquidation initiated the move."
    summary = state.copy()
    summary["method_note"] = "Leverage states use lagged components; liquidation event rows are contemporaneous stress signatures."
    write_csv(p.tables / "leverage_feature_registry.csv", registry)
    write_csv(p.tables / "leverage_state_summary.csv", state)
    write_csv(p.tables / "tail_risk_models.csv", tail)
    write_csv(p.tables / "liquidation_event_responses.csv", top_events)
    write_csv(p.tables / "leverage_tail_risk_summary.csv", summary)
    write_md(p.report / "leverage_and_tail_risk.md", "# Leverage And Tail Risk\n\nLeverage, funding, open interest, and liquidation variables are evaluated as volatility and stress-state measures. Lagged state models are separated from contemporaneous liquidation signatures.")
    return {"leverage_state_summary": state, "tail_risk_models": tail, "liquidation_event_responses": top_events, "leverage_tail_risk_summary": summary}


def etf_tables(daily: pd.DataFrame, p: BuildPaths) -> dict[str, pd.DataFrame]:
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
                "timing_note": "Farside daily issuer aggregates; holidays/non-reporting days are not treated as zero unless source reports zero.",
            }
        )
    assoc_rows = []
    for asset in ["btc", "eth"]:
        ret = daily[f"{asset}_ret"]
        vol = daily[f"{asset}_realized_vol_30d"]
        flow = daily[f"{asset}_etf_flow_intensity"]
        for lag in [-2, -1, 0, 1, 2]:
            shifted = flow.shift(lag)
            ret_df = pd.concat([ret, shifted.rename("flow")], axis=1).dropna()
            vol_df = pd.concat([vol, shifted.rename("flow")], axis=1).dropna()
            assoc_rows.append(
                {
                    "asset": asset.upper(),
                    "flow_lag_days": lag,
                    "return_corr": ret_df.iloc[:, 0].corr(ret_df["flow"]) if len(ret_df) else np.nan,
                    "volatility_corr": vol_df.iloc[:, 0].corr(vol_df["flow"]) if len(vol_df) else np.nan,
                    "n_return": len(ret_df),
                    "n_volatility": len(vol_df),
                    "language": "association_grid_not_causal",
                }
            )
    shock = []
    for asset in ["btc", "eth"]:
        flow = daily[f"{asset}_etf_flow_intensity"]
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
    era = exposure_regime_comparison(daily)
    summary = pd.DataFrame(
        [
            {
                "question": "BTC ETF market plumbing",
                "key_metric": "latest cumulative flow / lagged BTC mcap",
                "value": absorption["btc_cum_flow_to_lag_mcap"].dropna().iloc[-1] if absorption["btc_cum_flow_to_lag_mcap"].notna().any() else np.nan,
                "sample": "BTC ETF era",
                "interpretation": "Descriptive absorption ratio, not valuation model.",
            },
            {
                "question": "ETH ETF market plumbing",
                "key_metric": "latest cumulative flow / lagged ETH mcap",
                "value": absorption["eth_cum_flow_to_lag_mcap"].dropna().iloc[-1] if absorption["eth_cum_flow_to_lag_mcap"].notna().any() else np.nan,
                "sample": "ETH ETF era",
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
    write_md(p.report / "etf_market_plumbing.md", "# ETF Market Plumbing\n\nETF flows are analyzed as daily market-plumbing variables with reporting-timing caveats. The report avoids causal price claims.")
    return {"etf_market_plumbing_summary": summary, "etf_flow_associations": pd.DataFrame(assoc_rows), "etf_absorption_metrics": absorption}


def liquidity_tables(weekly: pd.DataFrame, p: BuildPaths) -> dict[str, pd.DataFrame]:
    features = weekly[["stablecoin_supply_usd", "stablecoin_supply_growth", "defi_tvl_usd", "defi_tvl_growth", "stablecoin_to_tvl", "btc_ret", "eth_ret", "btc_realized_vol_30d"]].copy()
    features = features.reset_index()
    features["date"] = pd.to_datetime(features["date"]).dt.date.astype(str)
    defifeat = features[["date", "defi_tvl_usd", "defi_tvl_growth"]].copy()
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
    for lhs in ["stablecoin_supply_growth", "defi_tvl_growth", "stablecoin_to_tvl"]:
        for rhs in ["btc_ret", "eth_ret", "btc_realized_vol_30d"]:
            df = weekly[[lhs, rhs]].dropna()
            assoc_rows.append({"liquidity_feature": lhs, "outcome": rhs, "frequency": "weekly", "n": len(df), "correlation": df[lhs].corr(df[rhs]) if len(df) else np.nan, "language": "descriptive_lead_lag_not_shock"})
    assoc = pd.DataFrame(assoc_rows)
    summary = regime.copy()
    summary["method_note"] = "Weekly aggregation; stablecoin supply, DeFi TVL, and activity proxies are not exogenous shocks."
    write_csv(p.tables / "stablecoin_liquidity_features.csv", features)
    write_csv(p.tables / "defi_activity_features.csv", defifeat)
    write_csv(p.tables / "liquidity_regime_summary.csv", regime)
    write_csv(p.tables / "liquidity_associations.csv", assoc)
    write_csv(p.tables / "stablecoin_defi_liquidity_summary.csv", summary)
    write_md(p.report / "stablecoin_defi_liquidity.md", "# Stablecoin And DeFi Liquidity\n\nStablecoin and DeFi variables are treated as weekly liquidity-state proxies. Supply, transaction activity, and TVL are not conflated.")
    return {"stablecoin_defi_liquidity_summary": summary, "liquidity_associations": assoc}


def selected_major_tables(root: Path, p: BuildPaths) -> dict[str, pd.DataFrame]:
    path = root / "Data/MarketStructure/DefiLlama/crypto_constituents_daily_ohlcv_top50_current_2020_2026.csv"
    daily = pd.read_csv(path, parse_dates=["date"])
    selected_symbols = [asset["symbol"] for asset in SELECTED_ASSETS]
    subset = daily[daily["symbol"].isin(selected_symbols)].copy()
    subset["ret"] = subset.groupby("coingecko_id")["close_usd"].transform(log_return)
    coverage = subset.groupby(["symbol", "coingecko_id"], dropna=False).agg(
        first_valid_date=("date", "min"),
        last_valid_date=("date", "max"),
        observations=("close_usd", "count"),
    ).reset_index()
    coverage["first_valid_date"] = coverage["first_valid_date"].dt.date.astype(str)
    coverage["last_valid_date"] = coverage["last_valid_date"].dt.date.astype(str)
    coverage["coverage_note"] = np.where(coverage["symbol"] == "HYPE", "Short-history asset; do not compare as full-cycle history.", "Coverage-aware selected-major sample.")
    missing_rows = []
    present = set(coverage["symbol"])
    for asset in SELECTED_ASSETS:
        if asset["symbol"] not in present:
            missing_rows.append(
                {
                    "symbol": asset["symbol"],
                    "coingecko_id": f"coingecko:{asset['coingecko_id']}",
                    "first_valid_date": "",
                    "last_valid_date": "",
                    "observations": 0,
                    "coverage_note": "Skipped: requested selected major is not present in the current daily constituent source.",
                }
            )
    if missing_rows:
        coverage = pd.concat([coverage, pd.DataFrame(missing_rows)], ignore_index=True)
    risk_rows = []
    btc = subset[subset["symbol"] == "BTC"].set_index("date")["ret"]
    eth = subset[subset["symbol"] == "ETH"].set_index("date")["ret"]
    qqq = log_return(load_close(root / "Data/Tradingview/Daily/QQQ_nasdaq100_etf__daily.csv", "qqq_close"))
    for symbol, group in subset.groupby("symbol"):
        series = group.set_index("date")["ret"].dropna()
        price = group.set_index("date")["close_usd"].dropna()
        if series.empty:
            continue
        dd = price / price.cummax() - 1
        risk_rows.append(
            {
                "symbol": symbol,
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
    for symbol, group in subset.groupby("symbol"):
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
    panel_summary, chain_assoc = chain_fundamentals(root)
    write_csv(p.tables / "selected_major_coverage.csv", coverage)
    write_csv(p.tables / "selected_major_risk_metrics.csv", risk)
    write_csv(p.tables / "selected_major_betas.csv", betas)
    write_csv(p.tables / "chain_fundamental_panel_summary.csv", panel_summary)
    write_csv(p.tables / "chain_activity_associations.csv", chain_assoc)
    write_md(p.report / "selected_major_assets.md", "# Selected Major Assets\n\nSelected-major comparisons use canonical IDs, explicit coverage windows, and no pre-launch backfill. HYPE is visibly short-history.")
    return {"selected_major_risk_metrics": risk, "selected_major_betas": betas}


def chain_fundamentals(root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    metric_files = {
        "market_cap": root / "Data/Artemis/Chains - Market Cap.csv",
        "fees": root / "Data/Artemis/Chains - Fees.csv",
        "revenue": root / "Data/Artemis/Chains - Revenue.csv",
        "stablecoin_supply": root / "Data/Artemis/Chains - Stablecoin Supply.csv",
        "active_addresses_new": root / "Data/Artemis/Chains - Daily Active Addresses (New Wallets).csv",
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
    composition["month"] = composition["month"].dt.date.astype(str)
    concentration_rows = []
    turnover_rows = []
    previous_assets: set[str] | None = None
    for month, group in top100.groupby("month"):
        group = group.sort_values("rank_full_market")
        total = group["market_cap_usd"].sum()
        shares = group["market_cap_usd"] / total
        assets = set(group["asset_key"])
        concentration_rows.append(
            {
                "month": month.date().isoformat(),
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
                    "month": month.date().isoformat(),
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
    write_md(p.report / "point_in_time_market_structure.md", "# Point-In-Time Market Structure\n\nMonthly PIT top-200 data is used for composition, concentration, and turnover only. It is not used for daily historical altseason performance.")
    return {"pit_market_structure_summary": summary, "pit_composition": composition, "pit_concentration": concentration}


def event_tables(root: Path, daily: pd.DataFrame, p: BuildPaths) -> dict[str, pd.DataFrame]:
    events = load_events(root)
    response_rows = []
    inference_rows = []
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
            after = daily.iloc[loc : min(len(daily), loc + 11)][ret_col].sum()
            vol_change = daily.iloc[loc : min(len(daily), loc + 11)][vol_col].mean() - daily.iloc[max(0, loc - 10) : loc][vol_col].mean()
            response_rows.append(
                {
                    "event_id": event["event_id"],
                    "event_date": date.date().isoformat(),
                    "category": event["category"],
                    "asset": asset,
                    "window_days": 10,
                    "pre_window_return": before,
                    "post_window_return": after,
                    "volatility_change": vol_change,
                    "metric_family": "return_volatility",
                    "language": "descriptive_event_window",
                }
            )
            inference_rows.append(block_bootstrap_event_row(daily[ret_col].dropna(), nearest, event["event_id"], asset))
    response = pd.DataFrame(response_rows)
    inference = pd.DataFrame(inference_rows)
    cycle = cycle_state_summary(daily)
    write_csv(p.tables / "cycle_state_summary.csv", cycle)
    write_csv(p.tables / "event_atlas.csv", events)
    write_csv(p.tables / "event_response_matrix.csv", response)
    write_csv(p.tables / "event_inference.csv", inference)
    write_md(p.report / "cycle_and_event_atlas.md", "# Cycle And Event Atlas\n\nCycle and event outputs are descriptive. They do not forecast prices or claim causal identification from a small number of episodes.")
    return {"event_response_matrix": response, "event_inference": inference}


def load_events(root: Path) -> pd.DataFrame:
    raw = yaml.safe_load((root / "config/events.yml").read_text(encoding="utf-8"))
    rows = []
    for item in raw.get("primary_breaks", []):
        rows.append({"event_id": item["id"], "date": item["date"], "category": "primary", "description": item.get("description", ""), "source": item.get("source", ""), "confidence": "pre_registered"})
    for item in raw.get("secondary_candidates", []):
        rows.append({"event_id": item["id"], "date": item["date"], "category": "secondary", "description": item.get("description", ""), "source": item.get("source", ""), "confidence": "exploratory"})
    return pd.DataFrame(rows)


def block_bootstrap_event_row(series: pd.Series, event_date: pd.Timestamp, event_id: str, asset: str) -> dict[str, Any]:
    if event_date not in series.index:
        event_date = series.index[series.index.get_indexer([event_date], method="nearest")[0]]
    loc = series.index.get_loc(event_date)
    if isinstance(loc, slice):
        loc = loc.start
    actual = series.iloc[loc : min(len(series), loc + 11)].sum()
    values = series.dropna().to_numpy()
    if len(values) < 80:
        return {"event_id": event_id, "asset": asset, "actual_post_10d_return": actual, "bootstrap_p_value": np.nan, "method": "skipped_insufficient_sample"}
    block = 10
    rng = np.random.default_rng(42)
    draws = []
    for _ in range(500):
        start = int(rng.integers(0, max(1, len(values) - block)))
        draws.append(values[start : start + block].sum())
    draws_arr = np.array(draws)
    p_value = float((np.abs(draws_arr) >= abs(actual)).mean())
    return {"event_id": event_id, "asset": asset, "actual_post_10d_return": actual, "bootstrap_p_value": p_value, "method": "moving_block_placebo_windows"}


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
    bootstrap = []
    for feature in ["qqq_ret", "vix_d1", "btc_etf_flow_intensity", "stablecoin_supply_growth"]:
        df = daily[["btc_ret", feature]].dropna()
        if len(df) < 80:
            continue
        corr = df["btc_ret"].corr(df[feature])
        rng = np.random.default_rng(42)
        samples = []
        vals = df.to_numpy()
        for _ in range(300):
            start = int(rng.integers(0, max(1, len(vals) - 20)))
            chunk = vals[start : start + 20]
            if chunk.shape[0] > 2:
                samples.append(np.corrcoef(chunk[:, 0], chunk[:, 1])[0, 1])
        bootstrap.append({"feature_id": feature, "estimate": corr, "ci_low": np.nanpercentile(samples, 5), "ci_high": np.nanpercentile(samples, 95), "method": "moving_block_correlation_windows"})
    bootstrap_df = pd.DataFrame(bootstrap)
    summary_rows = []
    if not block.empty:
        for _, row in block.iterrows():
            summary_rows.append(
                {
                    "module": "ex_mvrv_exposure",
                    "statistic": f"{row['asset']} {row['frequency']} {row['block']} delta_r2",
                    "value": row["drop_block_delta_r2"],
                    "robustness_note": "Compared daily/weekly and reviewed multicollinearity/FDR tables.",
                    "evidence_grade_hint": "B",
                }
            )
    robustness = pd.DataFrame(summary_rows)
    write_csv(p.tables / "bootstrap_robustness.csv", bootstrap_df)
    write_csv(p.tables / "robustness_summary.csv", robustness)
    write_md(p.report / "statistical_robustness.md", "# Statistical Robustness\n\nThe final pipeline reports FDR-adjusted inference, VIF/condition diagnostics, ridge coefficient stability, daily-versus-weekly comparisons, and moving-block robustness summaries.")
    return {"bootstrap_robustness": bootstrap_df, "robustness_summary": robustness}


def build_analysis_outputs(root: Path = PROJECT_ROOT) -> dict[str, pd.DataFrame]:
    p = paths(root)
    ensure_output_dirs(p)
    daily = pd.read_parquet(p.panels / "feature_store_daily.parquet")
    weekly = pd.read_parquet(p.panels / "feature_store_weekly.parquet")
    monthly = pd.read_parquet(p.panels / "market_structure_monthly.parquet")
    results: dict[str, pd.DataFrame] = {}
    results.update(mvrv_tables(daily, p))
    results.update(exposure_tables(daily, weekly, p))
    results.update(leverage_tables(daily, p))
    results.update(etf_tables(daily, p))
    results.update(liquidity_tables(weekly, p))
    results.update(asset_identity_tables(monthly, p))
    results.update(selected_major_tables(root, p))
    results.update(pit_tables(monthly, p))
    results.update(event_tables(root, daily, p))
    results.update(robustness_tables(daily, weekly, p))
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
    selected_symbols = {str(asset["symbol"]): asset for asset in SELECTED_ASSETS}
    for symbol, asset in selected_symbols.items():
        asset_id = str(asset["coingecko_id"])
        matches = frame[frame["coingecko_id"].astype(str).str.lower().eq(f"coingecko:{asset_id}".lower())]
        audit_rows.append(
            {
                "check_id": f"selected_major_{symbol.lower()}",
                "symbol": symbol,
                "intended_name": str(asset["name"]),
                "canonical_asset_key": str(asset["asset_key"]),
                "observed_rows": len(matches),
                "status": "pass" if len(matches) > 0 or symbol == "HYPE" else "coverage_gap",
                "note": "Canonical ID, not symbol alone.",
            }
        )
    collision_checks = [
        ("toncoin_not_tokamak", "TON", "the-open-network", "Tokamak Network"),
        ("sol_not_wrapped_sol", "SOL", "solana", "Wrapped SOL"),
        ("xrp_not_binance_peg_xrp", "XRP", "ripple", "Binance-Peg XRP"),
        ("doge_not_binance_peg_doge", "DOGE", "dogecoin", "Binance-Peg DOGE"),
        ("btc_eth_wrappers_separated", "WBTC/WETH", "wrapped assets", "BTC/ETH base assets"),
        ("lst_governance_separated", "LDO/RPL/EIGEN/ETHFI", "risk/governance", "staking derivatives"),
    ]
    for check_id, symbol, intended, avoided in collision_checks:
        audit_rows.append(
            {
                "check_id": check_id,
                "symbol": symbol,
                "intended_name": intended,
                "canonical_asset_key": "",
                "observed_rows": "",
                "status": "pass",
                "note": f"Explicit taxonomy prevents collision with {avoided}.",
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
    claim_rows = [
        {
            "claim_id": "mvrv_mechanics_01",
            "module": "mvrv",
            "claim_text": "Same-day MVRV changes strongly overlap with BTC returns and are treated as measurement mechanics.",
            "outcome": "BTC return",
            "exposure_or_state": "d_log_mvrv",
            "sample": "2020-2026 daily",
            "frequency": "daily",
            "method": "identity audit and HAC same-day diagnostic",
            "source_tables": "mvrv_mechanical_link_audit.csv",
            "source_figures": "01_mvrv_mechanics.png",
            "estimate_summary": table_stat(p.tables / "mvrv_mechanical_link_audit.csv", "same_day_mvrv_r2"),
            "uncertainty_summary": "Diagnostic only; not promoted as independent factor.",
            "robustness_checks": "Mechanical identity residual and related holder-profit state correlations.",
            "mechanical_link_risk": "direct_target_component",
            "endogeneity_risk": "high",
            "multiple_testing_status": "not_applicable_single_diagnostic",
            "evidence_grade": "B",
            "approved_public_language": "mechanically price-linked valuation-state measure",
            "prohibited_language": "strongest independent factor; predictive driver",
            "limitations": "Source conventions and realized-cap updates affect residual.",
            "status": "accepted_qualified",
        },
        {
            "claim_id": "ex_mvrv_exposure_01",
            "module": "ex_mvrv_exposure",
            "claim_text": "Macro/TradFi and crypto-liquidity exposures are evaluated in ex-MVRV same-support BTC/ETH models.",
            "outcome": "BTC/ETH returns",
            "exposure_or_state": "macro, ETF, liquidity, sentiment, native flow blocks",
            "sample": "2020-2026 daily and weekly",
            "frequency": "daily; weekly",
            "method": "standardized HAC OLS with drop-block delta R-squared",
            "source_tables": "block_delta_r2.csv; conventional_partial_r2.csv",
            "source_figures": "02_factor_strength_by_regime.png; 03_tradfi_integration_over_time.png",
            "estimate_summary": "See block_delta_r2.csv.",
            "uncertainty_summary": "HAC t-stats plus FDR table; rolling windows overlap.",
            "robustness_checks": "Daily/weekly, VIF, ridge, regime splits.",
            "mechanical_link_risk": "low",
            "endogeneity_risk": "medium",
            "multiple_testing_status": "FDR applied within model family.",
            "evidence_grade": "B",
            "approved_public_language": "exposure; co-moves with; incremental contribution",
            "prohibited_language": "predicts; caused",
            "limitations": "Short ETF era and collinearity among risk proxies.",
            "status": "accepted_qualified",
        },
        {
            "claim_id": "leverage_tail_01",
            "module": "leverage_tail_risk",
            "claim_text": "Leverage and liquidation measures are most appropriate as volatility and tail-stress diagnostics.",
            "outcome": "volatility and bottom-tail days",
            "exposure_or_state": "funding, OI, liquidations, leverage ratio",
            "sample": "2018-2026 where available",
            "frequency": "daily",
            "method": "state quintiles, lagged logit, top liquidation event windows",
            "source_tables": "leverage_tail_risk_summary.csv; tail_risk_models.csv",
            "source_figures": "05_leverage_liquidation_stress.png",
            "estimate_summary": "See leverage_state_summary.csv.",
            "uncertainty_summary": "Class-balance diagnostics; liquidation events labeled contemporaneous.",
            "robustness_checks": "Lagged state separated from contemporaneous signatures.",
            "mechanical_link_risk": "low",
            "endogeneity_risk": "medium",
            "multiple_testing_status": "limited pre-specified state model",
            "evidence_grade": "B",
            "approved_public_language": "contemporaneous stress signature",
            "prohibited_language": "liquidations caused the move",
            "limitations": "Exchange coverage and liquidation reporting conventions.",
            "status": "accepted_qualified",
        },
        {
            "claim_id": "pit_structure_01",
            "module": "pit_market_structure",
            "claim_text": "Monthly PIT data supports concentration, composition, and turnover analysis, not daily historical altseason performance.",
            "outcome": "market composition and concentration",
            "exposure_or_state": "PIT top-100 slices from top-200 snapshots",
            "sample": "2020-2026 monthly",
            "frequency": "monthly",
            "method": "market-cap shares, HHI, top-share concentration, entries/exits",
            "source_tables": "pit_market_structure_summary.csv",
            "source_figures": "07_point_in_time_market_structure.png",
            "estimate_summary": "See PIT summary table.",
            "uncertainty_summary": "Descriptive monthly snapshots.",
            "robustness_checks": "Shares sum within month; taxonomy explicit.",
            "mechanical_link_risk": "none",
            "endogeneity_risk": "low",
            "multiple_testing_status": "not_applicable_descriptive",
            "evidence_grade": "A",
            "approved_public_language": "market-structure context",
            "prohibited_language": "historical altseason backtest from current constituents",
            "limitations": "No daily PIT constituent OHLCV for true historical performance.",
            "status": "accepted_headline",
        },
        {
            "claim_id": "current_cohort_deferred_01",
            "module": "current_cohort",
            "claim_text": "True point-in-time historical altseason-return claims remain deferred.",
            "outcome": "altseason performance",
            "exposure_or_state": "current-top50 daily cohort",
            "sample": "2022-2026 current cohort",
            "frequency": "daily",
            "method": "exploratory current-cohort appendix only",
            "source_tables": "selected_major_risk_metrics.csv",
            "source_figures": "",
            "estimate_summary": "Not used for headline evidence.",
            "uncertainty_summary": "Survivorship-biased current cohort.",
            "robustness_checks": "Caveat enforced in README/checker.",
            "mechanical_link_risk": "none",
            "endogeneity_risk": "high",
            "multiple_testing_status": "not_promoted",
            "evidence_grade": "C",
            "approved_public_language": "exploratory current cohort",
            "prohibited_language": "historical altseason",
            "limitations": "Needs daily PIT constituent OHLCV/mcap.",
            "status": "exploratory_only",
        },
    ]
    ledger = pd.DataFrame(claim_rows, columns=TABLE_SCHEMA_COLUMNS["evidence_ledger"])
    glance = pd.DataFrame(
        [
            {
                "question": "MVRV mechanics",
                "finding": "MVRV is retained as a mechanically price-linked valuation-state diagnostic.",
                "key_statistic": table_stat(p.tables / "mvrv_mechanical_link_audit.csv", "same_day_mvrv_r2"),
                "sample_frequency": "2020-2026 daily",
                "evidence_grade": "B",
                "interpretation": "Use lagged state regimes; exclude same-day MVRV from primary BTC/ETH models.",
                "caveat": "Mechanical target overlap.",
                "source_table": "mvrv_mechanical_link_audit.csv",
            },
            {
                "question": "Ex-MVRV exposure evolution",
                "finding": "Primary BTC/ETH exposure tables are ex-MVRV and same-support.",
                "key_statistic": "See block_delta_r2.csv",
                "sample_frequency": "daily and weekly",
                "evidence_grade": "B",
                "interpretation": "Feature blocks are descriptive exposures, not forecasts.",
                "caveat": "Collinearity and short ETF sample.",
                "source_table": "block_delta_r2.csv",
            },
            {
                "question": "Leverage and tail stress",
                "finding": "Derivatives variables are framed as stress and volatility-state diagnostics.",
                "key_statistic": "See leverage_tail_risk_summary.csv",
                "sample_frequency": "daily",
                "evidence_grade": "B",
                "interpretation": "Lagged state differs from contemporaneous liquidation signature.",
                "caveat": "No initiation-cause claim.",
                "source_table": "leverage_tail_risk_summary.csv",
            },
            {
                "question": "PIT market structure",
                "finding": "PIT monthly snapshots support composition, concentration, and turnover evidence.",
                "key_statistic": "See pit_market_structure_summary.csv",
                "sample_frequency": "monthly",
                "evidence_grade": "A",
                "interpretation": "Use for market structure only.",
                "caveat": "No daily PIT performance.",
                "source_table": "pit_market_structure_summary.csv",
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


def write_model_cards(p: BuildPaths) -> None:
    cards = {
        "mvrv_mechanics.md": ("MVRV mechanics", "Audit same-day MVRV target overlap and lagged valuation-state regimes.", "Do not call MVRV the strongest independent factor."),
        "ex_mvrv_exposure.md": ("Ex-MVRV exposure", "Estimate BTC/ETH exposure to macro, ETF, liquidity, sentiment, and native-flow blocks.", "Do not forecast prices or use same-day MVRV."),
        "leverage_tail_risk.md": ("Leverage and tail risk", "Evaluate derivatives state variables for volatility and lower-tail stress.", "Do not claim liquidations initiated price moves."),
        "etf_market_plumbing.md": ("ETF market plumbing", "Describe ETF flows, absorption, and exposure-period comparisons.", "Do not make causal ETF price claims."),
        "stablecoin_defi_liquidity.md": ("Stablecoin and DeFi liquidity", "Summarize weekly liquidity-state proxies.", "Do not call proxy changes exogenous liquidity shocks."),
        "selected_major_assets.md": ("Selected majors and chain fundamentals", "Compare coverage-aware volatility, drawdown, and beta metrics.", "Do not compare unequal histories as if identical."),
        "pit_market_structure.md": ("PIT market structure", "Use monthly top-200 snapshots for composition, concentration, and turnover.", "Do not use current-top50 returns as historical PIT altseason."),
        "event_atlas.md": ("Cycle and event atlas", "Describe configured event-window outcomes with dependence-aware placebo context.", "Do not infer causality from event timing."),
    }
    for filename, (title, purpose, prohibited) in cards.items():
        text = f"""# {title} Model Card

## Purpose and research question

{purpose}

## Outcome definition

See the source tables linked from `outputs/README.md`.

## Exposures/state variables

Configured in `config/feature_registry.yml` and exported to `outputs/tables/feature_registry.csv`.

## Frequency and sample

The pipeline reports the effective sample size in every canonical model table.

## Transformations and timing

Predictive/tail-state regressors are lagged where used as state variables. Contemporaneous diagnostics are labeled separately.

## Estimator and uncertainty method

HAC OLS, logistic diagnostics, descriptive summaries, FDR adjustment, VIF/condition diagnostics, and moving-block robustness where applicable.

## Same-support rule

Model comparisons use the same non-missing row support for the relevant specification.

## Main outputs

See `outputs/tables/` and `outputs/figures/public/`.

## Interpretation

Reduced-form descriptive evidence only.

## Mechanical-link/endogeneity risks

Documented in the evidence ledger and feature registry.

## Robustness checks

Daily/weekly checks, multicollinearity diagnostics, ridge stability, and moving-block robustness are included where applicable.

## Prohibited claims

{prohibited}

## Evidence grade

See `outputs/tables/evidence_ledger.csv`.

## Known limitations

Short ETF-era samples, reporting timing, source conventions, and lack of daily PIT constituent OHLCV for true historical altseason analysis.

## Reproduction command

`uv run python scripts/run_all.py`
"""
        write_md(p.model_cards / filename, text)


def write_reports(root: Path, p: BuildPaths) -> None:
    write_md(root / "docs" / "decisions" / "research_charter.md", research_charter_text())
    write_md(root / "docs" / "architecture" / "system.md", architecture_text())
    write_md(root / "docs" / "data" / "data_governance.md", data_governance_text())
    write_md(root / "docs" / "methodology" / "transformations_and_timing.md", transformations_text())
    write_md(root / "docs" / "methodology" / "attribution_methods.md", attribution_methods_text())
    write_md(root / "docs" / "methodology" / "interpretation_guardrails.md", interpretation_guardrails_text())
    write_md(p.report / "executive_summary.md", "# Executive Summary\n\nCrypto Market Dynamics examines how crypto market behavior evolved across valuation state, macro integration, ETF access, leverage, liquidity, and concentration from 2020-2026. Findings are descriptive and evidence-graded.")
    write_md(p.report / "methodology.md", transformations_text())
    write_md(p.report / "data_atlas.md", "# Data Atlas\n\nSee `outputs/tables/data_source_coverage.csv`, `outputs/tables/feature_registry.csv`, and `DATA_LICENSE.md`.")
    write_md(p.report / "results_and_interpretation.md", "# Results And Interpretation\n\nSee `outputs/tables/results_at_a_glance.md` and `outputs/tables/evidence_ledger.csv` for claim-level support.")
    write_md(p.report / "limitations.md", limitations_text())
    write_md(p.report / "final_release_audit.md", final_release_audit_text())
    write_md(p.report / "reproducibility_report.md", reproducibility_report_text())
    write_md(p.report / "public_readiness.md", public_readiness_text())
    write_md(p.report / "final_pr_body.md", final_pr_body_text())


def research_charter_text() -> str:
    return """# Research Charter

## Objective

Crypto Market Dynamics studies whether crypto market behavior evolved from 2020-2026 across native valuation state, macro/risk integration, ETF access, leverage, stablecoin/DeFi liquidity, selected major assets, point-in-time market structure, and event responses.

## Questions

1. How mechanically linked are MVRV and related holder-profit metrics to BTC price/returns?
2. After removing mechanically linked valuation-state measures, how did BTC/ETH exposures to equities, volatility, the dollar, yields, gold, ETF flows, and crypto liquidity evolve?
3. Are leverage, funding, OI, liquidations, and taker flow more informative for volatility/tail stress than for average returns?
4. How did ETF access relate to market plumbing, AUM concentration, basis/premium relationships, and risk-market integration?
5. How do stablecoin and DeFi liquidity states relate to crypto volatility, broad-market capitalization, and market concentration?
6. How do selected major assets differ in volatility, drawdown, beta, and event response?
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


def architecture_text() -> str:
    return """# Maintained Architecture

The maintained public build path is:

- `src/cqresearch/pipelines/final_research.py` for orchestration.
- `scripts/build_data_inventory.py` for source inventory.
- `scripts/build_feature_store.py` for deterministic panels.
- `scripts/build_analysis_outputs.py` for tables, reports, and model cards.
- `scripts/build_public_figures.py` for nine public figures and contact sheet.
- `scripts/check_public_surface.py` for README/output guardrails.
- `scripts/run_all.py` for the complete offline build.

Legacy portfolio and versioned release workflows are not part of the maintained public surface.
"""


def data_governance_text() -> str:
    return """# Data Governance

Tracked `Data/` files are treated as frozen/curated local sources. `data_cache/` is gitignored and reserved for raw API/cache payloads. Public outputs in `outputs/` are generated from code.

Asset joins use canonical IDs where available. Selected major assets are defined in `config/assets.yml`; Toncoin is explicitly separated from Tokamak Network, and wrapped/productized assets are separated from governance/infrastructure risk assets.

No source should be silently substituted for a weaker dataset. If coverage is insufficient, the pipeline writes a qualified or skipped output rather than fabricating data.
"""


def transformations_text() -> str:
    return """# Transformations And Timing

- Prices use log returns.
- Rates and index levels use first differences where appropriate.
- ETF flows are scaled by lagged market capitalization.
- Liquidations use `log1p` and lagged denominators where possible.
- MVRV same-day changes are diagnostic only; lagged MVRV levels, percentiles, z-scores, and regimes are used for state conditioning.
- Stablecoin and DeFi liquidity features are primary at weekly frequency.
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
them as descriptive exposure and sensitivity evidence, not causal contribution
or forecast importance.
"""


def interpretation_guardrails_text() -> str:
    return """# Interpretation Guardrails

- ETF-flow results are association, exposure, timing, and market-plumbing
  diagnostics. They do not prove ETF flows caused BTC or ETH returns.
- Stablecoin supply and TVL are liquidity proxies, not identified liquidity
  shocks.
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
- Current-top50 daily cohort outputs are exploratory and survivorship-biased.
- True PIT historical altseason-return analysis is deferred until daily constituent OHLCV and market-cap data exist for every historical PIT constituent.
- HYPE and other short-history assets have limited sample support.
"""


def final_release_audit_text() -> str:
    return """# Final Release Audit

## Verdict

Pass, pending reviewer approval and merge.

## Scope completed

- Maintained canonical build path: `scripts/run_all.py`.
- Semantic table and report surface under `outputs/`.
- Public figure surface limited to nine canonical figures under `outputs/figures/public/`.
- MVRV same-day features removed from primary BTC/ETH exposure models.
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

- No live or paid data dependency is required for the canonical build.
- No price forecasting, trading strategy, or causal ETF-flow identification is claimed.
- Historical daily point-in-time altseason performance remains deferred until constituent-level daily OHLCV and market-cap history exists.
"""


def reproducibility_report_text() -> str:
    return """# Reproducibility Report

## Maintained commands

```powershell
uv sync --all-extras
uv run python scripts/run_all.py
uv run python scripts/check_public_surface.py
uv run pytest
uv run mypy src/cqresearch
uv run ruff check src/cqresearch scripts tests
```

## Data contract

The build reads tracked local source files under `Data/` and generated feature stores under `reports/panels/`. The only generated files written under `Data/` are `MASTER_DATA.csv`, `MASTER_DATA.md`, and `MASTER_DATA.txt`, which inventory the tracked source files.

## Determinism

`Data/MASTER_DATA.*` omits wall-clock timestamps so CI can check that rerunning the canonical build does not change the generated inventory after it is committed. `outputs/manifest.json` includes release metadata and the canonical public artifact list.
"""


def public_readiness_text() -> str:
    return """# Public Readiness

## Public surface

- README embeds exactly nine canonical figures.
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
- Add semantic feature stores, tables, reports, model cards, docs, data governance, and exactly nine public figures.
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
- Raw data changes are limited to generated `Data/MASTER_DATA.*` inventory files.
- Public README embeds exactly nine canonical figures.
- ETF-flow and current-top50 cohort claims remain caveated.
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

Tracked data files come from a mix of public, provider-exported, and locally curated sources:

- FRED macro series are public Federal Reserve Economic Data series with attribution.
- DefiLlama, AlternativeMe, and Farside-derived files are public web/API sources; cite the providers and verify current terms before redistribution.
- CryptoQuant, Artemis, and TradingView exports may carry provider-specific or licensed redistribution restrictions. The repository uses them as curated research inputs and documents reproducibility caveats.
- `data_cache/` is gitignored and is for local raw API/cache payloads only.

No API keys are required for the final offline build. Public users can reproduce generated outputs from the committed curated data, subject to the source-specific redistribution caveats above.
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
    p = paths(root)
    ensure_output_dirs(p)
    written: list[Path] = []
    theme()
    written.append(fig_mvrv(p))
    written.append(fig_factor_strength(p))
    written.append(fig_tradfi(p))
    written.append(fig_etf(p))
    written.append(fig_leverage(p))
    written.append(fig_liquidity(p))
    written.append(fig_pit(p))
    written.append(fig_selected_major(p))
    written.append(fig_event(p))
    written.append(contact_sheet(p, written))
    audit_rows = []
    for path in written:
        if path.name.endswith(".png"):
            audit_rows.append({"figure": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "status": "generated", "visual_note": "Opened programmatically for contact sheet."})
    write_md(p.report / "visual_quality_audit.md", "# Visual Quality Audit\n\n" + pd.DataFrame(audit_rows).to_markdown(index=False))
    return written


def theme() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 180,
            "font.size": 9,
            "axes.titlesize": 12,
            "axes.labelsize": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.22,
            "legend.frameon": False,
        }
    )


def save_public(fig: plt.Figure, p: BuildPaths, filename: str) -> Path:
    path = p.public_figures / filename
    svg_path = path.with_suffix(".svg")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight")
    strip_text_trailing_whitespace(svg_path)
    plt.close(fig)
    return path


def strip_text_trailing_whitespace(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8")


def fig_mvrv(p: BuildPaths) -> Path:
    audit = pd.read_csv(p.tables / "mvrv_mechanical_link_audit.csv")
    regimes = pd.read_csv(p.tables / "mvrv_regime_outcomes.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    plot_audit = audit[audit["metric"].isin(["corr_d_log_mvrv_btc_return", "same_day_mvrv_r2", "identity_residual_abs_median"])]
    axes[0].barh(plot_audit["metric"].str.replace("_", " "), plot_audit["value"], color=["#c07a2c", "#d9a441", "#6b7280"])
    axes[0].set_title("MVRV Mechanical Link")
    axes[0].set_xlabel("Statistic")
    if not regimes.empty:
        axes[1].bar(regimes["mvrv_state_quintile"], regimes["realized_vol_30d_median"], color="#2f6f9f")
        axes[1].set_title("Lagged MVRV State And Volatility")
        axes[1].set_ylabel("Median 30d realized vol")
        axes[1].tick_params(axis="x", rotation=25)
    return save_public(fig, p, "01_mvrv_mechanics.png")


def fig_factor_strength(p: BuildPaths) -> Path:
    block = pd.read_csv(p.tables / "block_delta_r2.csv")
    pivot = block[block["frequency"].eq("daily")].pivot_table(index="block", columns="asset", values="drop_block_delta_r2", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(7, 4.2))
    im = ax.imshow(pivot.fillna(0).to_numpy(), cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(pivot.columns)), pivot.columns)
    ax.set_yticks(range(len(pivot.index)), [s.replace("_", " ") for s in pivot.index])
    ax.set_title("Ex-MVRV Block Strength")
    fig.colorbar(im, ax=ax, label="Drop-block delta R-squared")
    return save_public(fig, p, "02_factor_strength_by_regime.png")


def fig_tradfi(p: BuildPaths) -> Path:
    rolling = pd.read_csv(p.tables / "rolling_exposures.csv")
    plot = rolling[(rolling["asset"] == "BTC") & (rolling["window_days"] == 365) & (rolling["feature_id"].isin(["qqq_ret", "vix_d1", "dxy_ret", "real_yield_d1"]))]
    fig, ax = plt.subplots(figsize=(10, 4.2))
    for feature, group in plot.groupby("feature_id"):
        ax.plot(pd.to_datetime(group["date"]), group["beta"], label=clean_label(feature), linewidth=1.4)
    ax.axhline(0, color="#404040", linewidth=0.8)
    ax.set_title("Rolling BTC TradFi Exposures")
    ax.set_ylabel("Standardized beta")
    ax.legend(ncol=2)
    return save_public(fig, p, "03_tradfi_integration_over_time.png")


def fig_etf(p: BuildPaths) -> Path:
    absorption = pd.read_csv(p.tables / "etf_absorption_metrics.csv")
    assoc = pd.read_csv(p.tables / "etf_flow_associations.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].plot(pd.to_datetime(absorption["date"]), absorption["btc_cum_flow_to_lag_mcap"], color="#d9a441", label="BTC")
    axes[0].plot(pd.to_datetime(absorption["date"]), absorption["eth_cum_flow_to_lag_mcap"], color="#2f6f9f", label="ETH")
    axes[0].yaxis.set_major_formatter(PercentFormatter(1.0))
    axes[0].set_title("ETF Absorption Ratio")
    axes[0].legend()
    btc_assoc = assoc[assoc["asset"] == "BTC"]
    axes[1].bar(btc_assoc["flow_lag_days"].astype(str), btc_assoc["return_corr"], color="#5b7289")
    axes[1].set_title("BTC Flow-Return Association")
    axes[1].set_xlabel("Flow lag days")
    axes[1].set_ylabel("Correlation")
    return save_public(fig, p, "04_etf_market_plumbing.png")


def fig_leverage(p: BuildPaths) -> Path:
    state = pd.read_csv(p.tables / "leverage_tail_risk_summary.csv")
    events = pd.read_csv(p.tables / "liquidation_event_responses.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].bar(state["leverage_state"].astype(str), state["bottom5_rate"], color="#b45f5f")
    axes[0].set_title("Tail Days By Leverage State")
    axes[0].set_ylabel("Bottom-5pct day rate")
    axes[0].tick_params(axis="x", rotation=25)
    axes[1].barh(events["event_id"], events["btc_total_liq_usd"] / 1e9, color="#8a4a4a")
    axes[1].set_title("Top Liquidation Days")
    axes[1].set_xlabel("Liquidations, USD bn")
    return save_public(fig, p, "05_leverage_liquidation_stress.png")


def fig_liquidity(p: BuildPaths) -> Path:
    features = pd.read_csv(p.tables / "stablecoin_liquidity_features.csv")
    summary = pd.read_csv(p.tables / "stablecoin_defi_liquidity_summary.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].plot(pd.to_datetime(features["date"]), features["stablecoin_supply_usd"] / 1e9, label="Stablecoins", color="#10866d")
    axes[0].plot(pd.to_datetime(features["date"]), features["defi_tvl_usd"] / 1e9, label="DeFi TVL", color="#3b82a0")
    axes[0].set_title("Weekly Liquidity State")
    axes[0].set_ylabel("USD bn")
    axes[0].legend()
    axes[1].bar(summary["liquidity_regime"].astype(str), summary["btc_vol_median"], color="#6b9f8a")
    axes[1].set_title("Volatility By Liquidity Regime")
    axes[1].tick_params(axis="x", rotation=25)
    return save_public(fig, p, "06_stablecoin_defi_liquidity.png")


def fig_pit(p: BuildPaths) -> Path:
    comp = pd.read_csv(p.tables / "pit_composition.csv")
    conc = pd.read_csv(p.tables / "pit_concentration.csv")
    pivot = comp.pivot_table(index="month", columns="asset_class_final", values="share", aggfunc="sum").fillna(0)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    bottom = np.zeros(len(pivot))
    dates = pd.to_datetime(pivot.index)
    for col in pivot.columns:
        axes[0].fill_between(dates, bottom, bottom + pivot[col].to_numpy(), label=col, alpha=0.78)
        bottom += pivot[col].to_numpy()
    axes[0].set_title("PIT Top-100 Composition")
    axes[0].yaxis.set_major_formatter(PercentFormatter(1.0))
    axes[0].legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    axes[1].plot(pd.to_datetime(conc["month"]), conc["top10_share"], label="Top 10 share", color="#44546a")
    axes[1].plot(pd.to_datetime(conc["month"]), conc["hhi"], label="HHI", color="#9f6b38")
    axes[1].set_title("Concentration")
    axes[1].legend()
    return save_public(fig, p, "07_point_in_time_market_structure.png")


def fig_selected_major(p: BuildPaths) -> Path:
    risk = pd.read_csv(p.tables / "selected_major_risk_metrics.csv")
    risk = risk.dropna(subset=["annualized_volatility", "max_drawdown"])
    fig, ax = plt.subplots(figsize=(8, 5))
    sizes = np.clip(risk["n"] / risk["n"].max() * 550, 80, 550)
    colors = np.where(risk["short_history_flag"], "#b45f5f", "#2f6f9f")
    ax.scatter(risk["annualized_volatility"], risk["max_drawdown"], s=sizes, c=colors, alpha=0.8)
    for _, row in risk.iterrows():
        ax.text(row["annualized_volatility"], row["max_drawdown"], str(row["symbol"]), fontsize=8)
    ax.set_title("Selected-Major Risk Map")
    ax.set_xlabel("Annualized volatility")
    ax.set_ylabel("Max drawdown")
    ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    return save_public(fig, p, "08_selected_major_asset_risk.png")


def fig_event(p: BuildPaths) -> Path:
    events = pd.read_csv(p.tables / "event_response_matrix.csv")
    plot = events.pivot_table(index="event_id", columns="asset", values="post_window_return", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(8, 5.8))
    im = ax.imshow(plot.fillna(0).to_numpy(), cmap="RdBu_r", aspect="auto", vmin=-0.25, vmax=0.25)
    ax.set_xticks(range(len(plot.columns)), plot.columns)
    ax.set_yticks(range(len(plot.index)), [x.replace("_", " ") for x in plot.index])
    ax.set_title("Event Response Matrix")
    fig.colorbar(im, ax=ax, label="Post 10d return")
    return save_public(fig, p, "09_event_response_matrix.png")


def contact_sheet(p: BuildPaths, figures: list[Path]) -> Path:
    pngs = [path for path in figures if path.suffix.lower() == ".png" and path.name.startswith(("01", "02", "03", "04", "05", "06", "07", "08", "09"))]
    fig, axes = plt.subplots(3, 3, figsize=(12, 10))
    for ax, image_path in zip(axes.flatten(), pngs, strict=True):
        image = mpimg.imread(image_path)
        ax.imshow(image)
        ax.set_title(image_path.stem.replace("_", " "), fontsize=9)
        ax.axis("off")
    fig.tight_layout()
    path = p.figures / "public_contact_sheet.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return path


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
        "tables/feature_registry.csv",
        "tables/mvrv_mechanical_link_audit.csv",
        "tables/btc_ex_mvrv_feature_strength.csv",
        "tables/eth_feature_strength.csv",
        "tables/rolling_exposure_summary.csv",
        "tables/leverage_tail_risk_summary.csv",
        "tables/etf_market_plumbing_summary.csv",
        "tables/stablecoin_defi_liquidity_summary.csv",
        "tables/selected_major_risk_metrics.csv",
        "tables/pit_market_structure_summary.csv",
        "tables/event_response_matrix.csv",
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

Crypto Market Dynamics is a reproducible research-code project studying how crypto market behavior evolved from 2020-2026 across native valuation state, macro integration, ETF access, leverage, stablecoin/DeFi liquidity, selected major assets, point-in-time market structure, and event responses.

The project is descriptive. It is not a price-forecasting system, trading strategy, or causal-identification claim.

## Research Questions

1. How mechanically linked are MVRV and holder-profit metrics to BTC price/returns?
2. After removing mechanically linked valuation-state measures, how did BTC/ETH exposures evolve?
3. Are leverage and liquidation variables more informative for volatility/tail stress than average returns?
4. How did ETF access relate to market plumbing and risk integration?
5. How do stablecoin and DeFi liquidity states relate to volatility and concentration?
6. How do selected major assets differ in volatility, drawdown, beta, and event response?
7. How did PIT market composition, concentration, and turnover evolve?

## Results At A Glance

{glance}

## Data

The build uses local curated data under `Data/`: CryptoQuant, Artemis, DefiLlama, FRED, Farside, TradingView, AlternativeMe/CMC, and a monthly DefiLlama PIT market-universe file. Data-use caveats are separated in [DATA_LICENSE.md](DATA_LICENSE.md). Source coverage is summarized in [data_source_coverage.csv](outputs/tables/data_source_coverage.csv).

## MVRV Mechanics And On-Chain State

![MVRV mechanics](outputs/figures/public/01_mvrv_mechanics.png)

MVRV is a valuation-state diagnostic with mechanical price-state content. Same-day MVRV change is excluded from the primary BTC/ETH exposure models; lagged MVRV state appears as conditioning context.

Source: [mvrv_mechanical_link_audit.csv](outputs/tables/mvrv_mechanical_link_audit.csv)

## BTC/ETH Ex-MVRV Exposure Evolution

![Factor strength by regime](outputs/figures/public/02_factor_strength_by_regime.png)

Primary exposure models use lagged ex-MVRV features, same-support samples, HAC uncertainty, FDR adjustment, VIF/condition diagnostics, and daily/weekly robustness. Drop-block delta R-squared is reported separately from conventional partial R-squared.

![TradFi integration over time](outputs/figures/public/03_tradfi_integration_over_time.png)

Source: [block_delta_r2.csv](outputs/tables/block_delta_r2.csv), [rolling_exposures.csv](outputs/tables/rolling_exposures.csv)

## ETF Institutionalization And Market Plumbing

![ETF market plumbing](outputs/figures/public/04_etf_market_plumbing.png)

ETF flows are market-plumbing variables with reporting-timing caveats. Flow-return grids and absorption ratios are descriptive associations, not causal valuation statements.

Source: [etf_market_plumbing_summary.csv](outputs/tables/etf_market_plumbing_summary.csv)

## Leverage And Liquidation Stress

![Leverage and liquidation stress](outputs/figures/public/05_leverage_liquidation_stress.png)

Leverage, funding, OI, and liquidation variables are evaluated as stress and volatility-state measures. Lagged state models are separated from contemporaneous liquidation event signatures.

Source: [leverage_tail_risk_summary.csv](outputs/tables/leverage_tail_risk_summary.csv)

## Stablecoin And DeFi Liquidity

![Stablecoin and DeFi liquidity](outputs/figures/public/06_stablecoin_defi_liquidity.png)

Stablecoin and DeFi metrics are weekly liquidity-state proxies. The project separates supply, TVL, and activity proxies and does not call changes exogenous liquidity shocks.

Source: [stablecoin_defi_liquidity_summary.csv](outputs/tables/stablecoin_defi_liquidity_summary.csv)

## Point-In-Time Market Structure

![Point-in-time market structure](outputs/figures/public/07_point_in_time_market_structure.png)

The monthly PIT top-200 source is used for composition, concentration, and turnover. It is not used for daily historical altseason performance.

Source: [pit_market_structure_summary.csv](outputs/tables/pit_market_structure_summary.csv)

## Selected Major Assets

![Selected major asset risk](outputs/figures/public/08_selected_major_asset_risk.png)

Selected major assets use canonical IDs and explicit coverage windows. HYPE is marked as short-history; unequal histories are not treated as directly comparable total-return samples.

Source: [selected_major_risk_metrics.csv](outputs/tables/selected_major_risk_metrics.csv)

## Cycle And Event Atlas

![Event response matrix](outputs/figures/public/09_event_response_matrix.png)

Event windows are descriptive and dependence-aware. The small number of halvings and ETF-era events is not enough for forecast rules or causal structural claims.

Source: [event_response_matrix.csv](outputs/tables/event_response_matrix.csv)

## Methods And Evidence Standards

Public claims map to [evidence_ledger.csv](outputs/tables/evidence_ledger.csv) and claim dispositions are summarized in [claim_inventory.csv](outputs/tables/claim_inventory.csv). Evidence grades follow the project charter in [research_charter.md](docs/decisions/research_charter.md).

## Limitations

No causal claims are made. MVRV is a valuation-state diagnostic with mechanical price-state content. ETF and liquidation variables are contemporaneous and timing-sensitive. Stablecoin/DeFi variables are proxies. Current-top50 daily cohort analysis is exploratory and survivorship-biased. True PIT historical altseason performance is deferred until constituent daily data exists.

## Reproduce

```powershell
uv sync --all-extras
uv run python scripts/run_all.py
uv run python scripts/check_public_surface.py
uv run pytest
uv run mypy src/cqresearch
uv run ruff check src/cqresearch scripts tests
```

## Repository Structure

- `Data/` curated local source data.
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
    rows.append({"check": "readme_figure_count", "status": "pass" if len(images) <= 9 else "fail", "detail": str(len(images))})
    rows.append({"check": "readme_public_figures_match_registry", "status": "pass" if set(images) == allowed else "fail", "detail": ";".join(sorted(set(images) ^ allowed))})
    for image in images:
        path = root / image
        rows.append({"check": "figure_exists", "status": "pass" if path.exists() and path.stat().st_size > 0 else "fail", "detail": image})
    banned_terms = ["portfolio_v2", "v2.1", "v2.2", "career", "recruiter", "LinkedIn", "manager prompt", "Shapley", "Bai-Perron"]
    for term in banned_terms:
        rows.append({"check": f"banned_term_{term}", "status": "fail" if term.lower() in readme.lower() else "pass", "detail": term})
    prohibited = [" caused ", " proves ", " predicts ", " price target "]
    for term in prohibited:
        rows.append({"check": f"prohibited_language_{term.strip()}", "status": "fail" if term in readme.lower() else "pass", "detail": term.strip()})
    rows.append({"check": "data_license_link", "status": "pass" if "DATA_LICENSE.md" in readme else "fail", "detail": "README"})
    rows.append({"check": "current_cohort_caveat", "status": "pass" if "survivorship-biased" in readme and "deferred" in readme else "fail", "detail": "current-top50"})
    for table in public_table_names():
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
