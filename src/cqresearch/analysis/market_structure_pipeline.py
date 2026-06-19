"""Market-structure extension builders.

The extension is intentionally additive: raw pulls live in gitignored
``data_cache/`` while normalized public summaries live under
``Data/MarketStructure`` and ``outputs``.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from cqresearch.analysis.asset_classification import (
    classification_summary,
    classify_symbol_frame,
    load_classification_overrides,
)
from cqresearch.analysis.market_universe import (
    build_binance_liquidity_ranks,
    market_cap_top100_gap_report,
)
from cqresearch.data.market_structure_cache import CacheLayout, read_json, utc_now_iso
from cqresearch.data.market_structure_endpoints import all_endpoint_specs, endpoint_audit_rows
from cqresearch.data.market_structure_normalizers import (
    normalize_alternative_me_fear_greed,
    normalize_binance_24h_tickers,
    normalize_binance_exchange_info,
    normalize_binance_funding_rates,
    normalize_binance_klines,
    normalize_cmc_fear_greed,
    normalize_defillama_chains,
    normalize_defillama_overview,
    normalize_defillama_stablecoins,
)
from cqresearch.viz.design_system import COLORS, HERO_SIZE
from cqresearch.viz.theme import apply_institutional_mpl_theme

ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class MarketStructureBuildResult:
    """Paths written by the market-structure builders."""

    curated_files: list[Path]
    output_files: list[Path]
    skipped: list[str]


def rel(path: Path, root: Path = ROOT) -> str:
    """Return a POSIX relative path for reports/manifests."""

    return path.relative_to(root).as_posix()


def ensure_dirs(project_root: Path) -> dict[str, Path]:
    data_root = project_root / "Data" / "MarketStructure"
    dirs = {
        "data": data_root,
        "defillama": data_root / "DefiLlama",
        "binance": data_root / "Binance",
        "cmc": data_root / "CoinMarketCap",
        "registry": data_root / "SourceRegistry",
        "outputs": project_root / "outputs",
        "tables": project_root / "outputs" / "tables",
        "figures": project_root / "outputs" / "figures",
        "report": project_root / "outputs" / "report",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def write_csv(path: Path, frame: pd.DataFrame) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    return path


def write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def csv_sha12(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def csv_inventory_row(path: Path, source: str, topic: str, project_root: Path) -> dict[str, Any]:
    frame = pd.read_csv(path)
    start = end = ""
    frequency = "snapshot"
    missing_days = ""
    if "date" in frame.columns:
        dates = pd.to_datetime(frame["date"], errors="coerce").dropna()
        if not dates.empty:
            start = dates.min().date().isoformat()
            end = dates.max().date().isoformat()
            frequency = "daily"
            observed = dates.dt.normalize().nunique()
            span = (dates.max().normalize() - dates.min().normalize()).days + 1
            missing_days = max(0, span - observed)
    elif "month" in frame.columns:
        dates = pd.to_datetime(frame["month"], errors="coerce").dropna()
        if not dates.empty:
            start = dates.min().date().isoformat()
            end = dates.max().date().isoformat()
            frequency = "monthly"
    return {
        "source": source,
        "relpath": rel(path, project_root / "Data"),
        "topic": topic,
        "start_date": start,
        "end_date": end,
        "row_count": len(frame),
        "col_count": len(frame.columns),
        "frequency": frequency,
        "missing_days": missing_days,
        "size_bytes": path.stat().st_size,
        "sha256_12": csv_sha12(path),
        "columns": "|".join(map(str, frame.columns)),
    }


def write_readmes(project_root: Path) -> list[Path]:
    dirs = ensure_dirs(project_root)
    written = [
        write_text(
            dirs["data"] / "README.md",
            """# MarketStructure

Tracked, normalized market-structure summaries for the public repo. Large raw API payloads are intentionally kept out of git under `data_cache/`.

This subtree is additive to the frozen research database. Existing source files under `Data/AlternativeMe`, `Data/DefiLlama`, `Data/Tradingview`, and other historical folders remain unchanged.
""",
        ),
        write_text(
            dirs["defillama"] / "README.md",
            """# DefiLlama Market-Structure Curated Layer

Contains endpoint capability files and normalized public summaries derived from local DefiLlama cache when available. Pro-only datasets are skipped unless `DEFILLAMA_API_KEY` and plan access are present at runtime.
""",
        ),
        write_text(
            dirs["binance"] / "README.md",
            """# Binance Market-Structure Curated Layer

Contains public Binance exchange-info, kline, funding, and liquidity-rank summaries when local cache exists. Binance liquidity ranks are exchange-liquidity ranks based on quote volume, not historical market-cap ranks.
""",
        ),
        write_text(
            dirs["cmc"] / "README.md",
            """# CoinMarketCap Market-Structure Curated Layer

Contains CMC Fear & Greed normalized history only when `CMC_API_KEY` is available and cached. Without a key, the public output falls back to the tracked AlternativeMe Fear & Greed series and records the CMC gap.
""",
        ),
    ]
    return written


def source_registry(project_root: Path) -> pd.DataFrame:
    defillama_count = len(list((project_root / "Data" / "DefiLlama").rglob("*.csv")))
    ms_count = len(list((project_root / "Data" / "MarketStructure").rglob("*.csv")))
    return pd.DataFrame(
        [
            {
                "source": "DefiLlama",
                "role": "TVL, stablecoins, DeFi activity, RWA/DAT context",
                "tracked_files": defillama_count,
                "auth_required": "Pro endpoints only",
                "storage_policy": "raw cache in data_cache/defillama; curated summaries in Data/MarketStructure/DefiLlama",
                "status": "tracked_baseline_plus_optional_refresh",
            },
            {
                "source": "Binance",
                "role": "CEX spot/futures liquidity, quote volume, funding and premium regimes",
                "tracked_files": ms_count,
                "auth_required": "no",
                "storage_policy": "raw cache in data_cache/binance; curated summaries in Data/MarketStructure/Binance",
                "status": "optional_public_fetch_or_cache",
            },
            {
                "source": "CoinMarketCap",
                "role": "Fear & Greed historical sentiment comparison",
                "tracked_files": len(list((project_root / "Data" / "MarketStructure" / "CoinMarketCap").rglob("*.csv"))),
                "auth_required": "CMC_API_KEY",
                "storage_policy": "raw cache in data_cache/coinmarketcap; curated summaries in Data/MarketStructure/CoinMarketCap",
                "status": "optional_key_required",
            },
            {
                "source": "AlternativeMe",
                "role": "Tracked baseline Fear & Greed sentiment series",
                "tracked_files": 1,
                "auth_required": "no",
                "storage_policy": "existing frozen Data/AlternativeMe file used in public outputs",
                "status": "tracked_baseline",
            },
        ]
    )


def normalize_cache_to_curated(project_root: Path = ROOT, *, cache_only: bool = False) -> MarketStructureBuildResult:
    """Normalize local raw cache into tracked curated CSVs."""

    dirs = ensure_dirs(project_root)
    layout = CacheLayout.from_env(project_root)
    written = write_readmes(project_root)
    skipped: list[str] = []

    endpoint_rows = pd.DataFrame(endpoint_audit_rows(all_endpoint_specs()))
    written.append(write_csv(dirs["registry"] / "market_structure_endpoint_capabilities.csv", endpoint_rows))

    registry = source_registry(project_root)
    written.append(write_csv(dirs["registry"] / "market_structure_source_registry.csv", registry))

    defillama_existing = inventory_existing_defillama(project_root)
    written.append(write_csv(dirs["defillama"] / "defillama_existing_inventory.csv", defillama_existing))

    written.extend(normalize_defillama_cache(layout, dirs["defillama"], skipped))
    written.extend(normalize_binance_cache(layout, dirs["binance"], skipped))
    written.extend(normalize_cmc_cache(layout, dirs["cmc"], skipped))

    status_rows = [{"status": "cache_only", "detail": "No network calls were made."}] if cache_only else []
    status_rows.extend({"status": "skipped", "detail": item} for item in skipped)
    written.append(write_csv(dirs["registry"] / "market_structure_cache_status.csv", pd.DataFrame(status_rows)))

    update_master_inventory(project_root)
    return MarketStructureBuildResult(curated_files=written, output_files=[], skipped=skipped)


def inventory_existing_defillama(project_root: Path) -> pd.DataFrame:
    rows = []
    for path in sorted((project_root / "Data" / "DefiLlama").rglob("*.csv")):
        try:
            meta = csv_inventory_row(path, "DefiLlama", "Existing curated DefiLlama source file", project_root)
        except Exception:
            continue
        rows.append(meta)
    return pd.DataFrame(rows)


def _cached_payloads(layout: CacheLayout, source: str, dataset_prefix: str) -> list[tuple[Path, Any]]:
    raw_dir = layout.raw_dir(source)
    if not raw_dir.exists():
        return []
    payloads = []
    for path in sorted(raw_dir.glob(f"{dataset_prefix}*__*.json")):
        try:
            payloads.append((path, read_json(path)))
        except Exception:
            continue
    return payloads


def normalize_defillama_cache(layout: CacheLayout, out_dir: Path, skipped: list[str]) -> list[Path]:
    written: list[Path] = []
    chains = _cached_payloads(layout, "defillama", "chains_current")
    if chains:
        written.append(write_csv(out_dir / "defillama_chains_current.csv", normalize_defillama_chains(chains[-1][1])))
    else:
        skipped.append("DefiLlama chains_current cache unavailable.")

    stable = _cached_payloads(layout, "defillama", "stablecoins_current")
    if stable:
        written.append(write_csv(out_dir / "defillama_stablecoins_current.csv", normalize_defillama_stablecoins(stable[-1][1])))

    for dataset in ["dex_overview", "fees_overview", "open_interest_overview"]:
        payloads = _cached_payloads(layout, "defillama", dataset)
        if payloads:
            frame = normalize_defillama_overview(payloads[-1][1], dataset)
            written.append(write_csv(out_dir / f"defillama_{dataset}.csv", frame))
    return written


def normalize_binance_cache(layout: CacheLayout, out_dir: Path, skipped: list[str]) -> list[Path]:
    written: list[Path] = []
    exchange = _cached_payloads(layout, "binance", "spot_exchange_info")
    if exchange:
        symbols = normalize_binance_exchange_info(exchange[-1][1])
        written.append(write_csv(out_dir / "binance_spot_symbols.csv", symbols))
    else:
        skipped.append("Binance spot_exchange_info cache unavailable.")

    tickers = _cached_payloads(layout, "binance", "spot_24h_tickers")
    if tickers:
        written.append(write_csv(out_dir / "binance_spot_24h_tickers_snapshot.csv", normalize_binance_24h_tickers(tickers[-1][1])))

    kline_frames = []
    for path, payload in _cached_payloads(layout, "binance", "spot_daily_klines"):
        symbol = path.name.split("__", 1)[0].replace("spot_daily_klines_", "")
        frame = normalize_binance_klines(payload, symbol)
        if not frame.empty:
            kline_frames.append(frame)
    if kline_frames:
        klines = pd.concat(kline_frames, ignore_index=True)
        written.append(write_csv(out_dir / "binance_spot_klines__daily.csv", klines))
        ranks = build_binance_liquidity_ranks(klines)
        written.append(write_csv(out_dir / "binance_liquidity_top100__monthly.csv", ranks))
    else:
        skipped.append("Binance spot daily kline cache unavailable; liquidity top100 not generated.")

    funding_frames = []
    for path, payload in _cached_payloads(layout, "binance", "usd_m_funding_rate"):
        _ = path
        frame = normalize_binance_funding_rates(payload)
        if not frame.empty:
            funding_frames.append(frame)
    if funding_frames:
        written.append(write_csv(out_dir / "binance_usd_m_funding_rates.csv", pd.concat(funding_frames, ignore_index=True)))
    return written


def normalize_cmc_cache(layout: CacheLayout, out_dir: Path, skipped: list[str]) -> list[Path]:
    written: list[Path] = []
    payloads = _cached_payloads(layout, "coinmarketcap", "fear_greed_historical")
    if not payloads:
        skipped.append("CMC Fear & Greed cache unavailable; AlternativeMe remains the tracked sentiment baseline.")
        return written
    frames = [normalize_cmc_fear_greed(payload) for _, payload in payloads]
    out = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["date"]).sort_values("date")
    written.append(write_csv(out_dir / "cmc_fear_greed__daily.csv", out))
    return written


def update_master_inventory(project_root: Path) -> None:
    """Append/refresh MarketStructure rows in MASTER_DATA inventories."""

    master_csv = project_root / "Data" / "MASTER_DATA.csv"
    if not master_csv.exists():
        return
    base = pd.read_csv(master_csv)
    base = base[base["source"] != "MarketStructure"].copy()
    rows = []
    for path in sorted((project_root / "Data" / "MarketStructure").rglob("*.csv")):
        topic = path.stem.replace("_", " ").title()
        try:
            rows.append(csv_inventory_row(path, "MarketStructure", topic, project_root))
        except Exception:
            continue
    if rows:
        updated = pd.concat([base, pd.DataFrame(rows)], ignore_index=True)
        updated.to_csv(master_csv, index=False)
    master_md = project_root / "Data" / "MASTER_DATA.md"
    if master_md.exists() and rows:
        text = master_md.read_text(encoding="utf-8")
        marker = "\n## MarketStructure Extension\n"
        text = text.split(marker, 1)[0].rstrip()
        table_rows = "\n".join(
            f"| `{row['relpath']}` | {row['topic']} | {row['row_count']} | {row['frequency']} |"
            for row in rows
        )
        section = f"""{marker}
Tracked normalized market-structure summaries. Raw API payloads stay in gitignored `data_cache/`; these files are release-ready CSVs under `Data/MarketStructure/`.

| Relative path | Topic | Rows | Freq |
| --- | --- | ---: | --- |
{table_rows}
"""
        master_md.write_text(text + "\n" + section, encoding="utf-8")


def load_sentiment(project_root: Path) -> pd.DataFrame:
    frames = []
    alt_path = project_root / "Data" / "AlternativeMe" / "fear_greed_index__daily.csv"
    if alt_path.exists():
        frames.append(normalize_alternative_me_fear_greed(pd.read_csv(alt_path)))
    cmc_path = project_root / "Data" / "MarketStructure" / "CoinMarketCap" / "cmc_fear_greed__daily.csv"
    if cmc_path.exists():
        frames.append(pd.read_csv(cmc_path))
    if not frames:
        return pd.DataFrame(columns=["source", "date", "fng_value", "fng_classification"])
    return pd.concat(frames, ignore_index=True).sort_values(["source", "date"])


def stablecoin_tvl_regimes(project_root: Path) -> pd.DataFrame:
    metrics_path = project_root / "Data" / "DefiLlama" / "ChainMetrics" / "all_dex_metrics__daily.csv"
    tvl_path = project_root / "Data" / "DefiLlama" / "TVL" / "Daily" / "tvl_all_chains_daily.csv"
    if not metrics_path.exists() and not tvl_path.exists():
        return pd.DataFrame(columns=["date", "defi_tvl_usd", "stablecoins_mcap_usd", "dex_volume_usd", "stablecoin_tvl_ratio", "regime"])

    if metrics_path.exists():
        metrics = pd.read_csv(metrics_path, parse_dates=["date"])
        frame = pd.DataFrame({"date": metrics["date"]})
        frame["stablecoins_mcap_usd"] = pd.to_numeric(metrics.get("Stablecoins Mcap"), errors="coerce")
        frame["dex_volume_usd"] = pd.to_numeric(metrics.get("DEXs Volume"), errors="coerce")
        frame["defi_tvl_usd"] = pd.to_numeric(metrics.get("TVL"), errors="coerce")
    else:
        frame = pd.DataFrame()
    if tvl_path.exists():
        tvl = pd.read_csv(tvl_path, parse_dates=["date"])
        tvl["defi_tvl_usd_alt"] = pd.to_numeric(tvl.get("TVL"), errors="coerce")
        frame = frame.merge(tvl[["date", "defi_tvl_usd_alt"]], on="date", how="outer") if not frame.empty else tvl[["date", "defi_tvl_usd_alt"]]
        frame["defi_tvl_usd"] = frame.get("defi_tvl_usd").combine_first(frame["defi_tvl_usd_alt"]) if "defi_tvl_usd" in frame else frame["defi_tvl_usd_alt"]
    frame = frame.drop(columns=[col for col in ["defi_tvl_usd_alt"] if col in frame])
    frame["stablecoin_tvl_ratio"] = frame["stablecoins_mcap_usd"] / frame["defi_tvl_usd"]
    monthly = frame.set_index("date").resample("ME").last().reset_index()
    median = monthly["stablecoin_tvl_ratio"].median(skipna=True)
    monthly["regime"] = monthly["stablecoin_tvl_ratio"].map(lambda value: "high_stablecoin_to_tvl" if pd.notna(value) and value >= median else "low_stablecoin_to_tvl")
    monthly["date"] = monthly["date"].dt.date
    return monthly


def cex_dex_activity(project_root: Path) -> pd.DataFrame:
    dex_path = project_root / "Data" / "DefiLlama" / "ChainMetrics" / "all_dex_metrics__daily.csv"
    cex_path = project_root / "Data" / "DefiLlama" / "CEX" / "cex_net_inflows_by_exchange__daily.csv"
    frames: list[pd.DataFrame] = []
    if dex_path.exists():
        dex = pd.read_csv(dex_path, parse_dates=["date"])
        frames.append(pd.DataFrame({"date": dex["date"], "metric": "dex_volume_usd", "value": pd.to_numeric(dex.get("DEXs Volume"), errors="coerce")}))
    if cex_path.exists():
        cex = pd.read_csv(cex_path, parse_dates=["date"])
        value_cols = [col for col in cex.columns if col != "date"]
        values = cex[value_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1, min_count=1)
        frames.append(pd.DataFrame({"date": cex["date"], "metric": "cex_net_inflows_usd", "value": values}))
    if not frames:
        return pd.DataFrame(columns=["date", "metric", "value"])
    out = pd.concat(frames, ignore_index=True)
    out = out.set_index("date").groupby("metric").resample("ME")["value"].sum(min_count=1).reset_index()
    out["date"] = out["date"].dt.date
    return out


def rwa_dat_growth(project_root: Path) -> pd.DataFrame:
    rwa_path = project_root / "Data" / "DefiLlama" / "RWA" / "rwa_onchain_mcap_all__daily.csv"
    dat_path = project_root / "Data" / "DefiLlama" / "DATs" / "dat-institutions.csv"
    rows = []
    if rwa_path.exists():
        rwa = pd.read_csv(rwa_path, parse_dates=["date"])
        value_cols = [col for col in rwa.columns if col != "date"]
        values = rwa[value_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1, min_count=1)
        rows.append(pd.DataFrame({"date": rwa["date"], "metric": "rwa_onchain_mcap_usd", "value": values}))
    if dat_path.exists():
        dat = pd.read_csv(dat_path)
        rows.append(
            pd.DataFrame(
                {
                    "date": [pd.Timestamp("2026-04-17")],
                    "metric": ["dat_institution_count"],
                    "value": [len(dat)],
                }
            )
        )
    if not rows:
        return pd.DataFrame(columns=["date", "metric", "value"])
    out = pd.concat(rows, ignore_index=True)
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.date
    return out


def btc_cycle_overlay(project_root: Path) -> pd.DataFrame:
    path = project_root / "Data" / "Tradingview" / "Daily" / "CRYPTOCAP_BTC_dominance__daily.csv"
    if not path.exists():
        return pd.DataFrame(columns=["date", "btc_dominance_close"])
    frame = pd.read_csv(path, parse_dates=["date"])
    out = frame[["date", "close"]].rename(columns={"close": "btc_dominance_close"})
    out["btc_dominance_close"] = pd.to_numeric(out["btc_dominance_close"], errors="coerce")
    out["date"] = out["date"].dt.date
    return out.dropna()


def feature_panel_summary(
    sentiment: pd.DataFrame,
    stablecoin_tvl: pd.DataFrame,
    activity: pd.DataFrame,
    ranks: pd.DataFrame,
) -> pd.DataFrame:
    rows = [
        {"feature_family": "sentiment", "rows": len(sentiment), "status": "available" if len(sentiment) else "missing"},
        {"feature_family": "stablecoin_tvl_regime", "rows": len(stablecoin_tvl), "status": "available" if len(stablecoin_tvl) else "missing"},
        {"feature_family": "cex_dex_activity", "rows": len(activity), "status": "available" if len(activity) else "missing"},
        {"feature_family": "binance_liquidity_top100", "rows": len(ranks), "status": "available" if len(ranks) else "skipped_no_kline_cache"},
        {"feature_family": "market_cap_top100", "rows": 0, "status": "skipped_no_point_in_time_source"},
    ]
    return pd.DataFrame(rows)


def build_outputs(project_root: Path = ROOT) -> MarketStructureBuildResult:
    """Build market-structure public tables, figures, reports, and manifest patch."""

    dirs = ensure_dirs(project_root)
    output_files: list[Path] = []
    skipped: list[str] = []

    endpoint_rows = pd.DataFrame(endpoint_audit_rows(all_endpoint_specs()))
    output_files.append(write_csv(dirs["tables"] / "T28_market_structure_source_capabilities.csv", endpoint_rows))

    overrides = load_classification_overrides(project_root / "config" / "asset_classification_overrides.yml")
    symbol_path = project_root / "Data" / "MarketStructure" / "Binance" / "binance_spot_symbols.csv"
    if symbol_path.exists():
        symbols = pd.read_csv(symbol_path)
    else:
        symbols = pd.DataFrame(
            {
                "symbol": ["BTCUSDT", "ETHUSDT", "USDCUSDT", "PAXGUSDT", "DOGEUSDT"],
                "base_asset": ["BTC", "ETH", "USDC", "PAXG", "DOGE"],
                "quote_asset": ["USDT", "USDT", "USDT", "USDT", "USDT"],
                "status": ["seed_reference"] * 5,
            }
        )
    classified = classify_symbol_frame(symbols, overrides)
    output_files.append(write_csv(dirs["tables"] / "T29_asset_classification.csv", classified))
    output_files.append(write_csv(dirs["tables"] / "T29_asset_classification_summary.csv", classification_summary(classified)))

    ranks_path = project_root / "Data" / "MarketStructure" / "Binance" / "binance_liquidity_top100__monthly.csv"
    if ranks_path.exists():
        ranks = pd.read_csv(ranks_path)
    else:
        ranks = pd.DataFrame(
            [
                {
                    "month": "",
                    "symbol": "",
                    "base_asset": "",
                    "quote_asset": "",
                    "rolling_quote_volume_usd": "",
                    "liquidity_rank": "",
                    "universe_label": "Binance exchange-liquidity top100",
                    "status": "skipped_no_kline_cache",
                }
            ]
        )
        skipped.append("Binance liquidity top100 skipped because no spot kline cache exists.")
    output_files.append(write_csv(dirs["tables"] / "T30_binance_liquidity_top100.csv", ranks))

    sentiment = load_sentiment(project_root)
    if not (project_root / "Data" / "MarketStructure" / "CoinMarketCap" / "cmc_fear_greed__daily.csv").exists():
        skipped.append("CMC Fear & Greed skipped because CMC_API_KEY/cache is unavailable; AlternativeMe baseline used.")
    output_files.append(write_csv(dirs["tables"] / "T31_sentiment_comparison.csv", sentiment))
    stablecoin_tvl = stablecoin_tvl_regimes(project_root)
    output_files.append(write_csv(dirs["tables"] / "T32_stablecoin_tvl_regimes.csv", stablecoin_tvl))
    activity = cex_dex_activity(project_root)
    output_files.append(write_csv(dirs["tables"] / "T33_cex_dex_activity.csv", activity))
    cycle = btc_cycle_overlay(project_root)
    output_files.append(write_csv(dirs["tables"] / "T34_btc_cycle_overlay.csv", cycle))
    rwa_dat = rwa_dat_growth(project_root)
    output_files.append(write_csv(dirs["tables"] / "T35_rwa_dat_growth.csv", rwa_dat))
    gap = market_cap_top100_gap_report(False)
    skipped.append("Historical market-cap top100 skipped because no point-in-time source is available.")
    output_files.append(write_csv(dirs["tables"] / "T36_market_cap_top100_gap.csv", gap))
    feature_panel = feature_panel_summary(sentiment, stablecoin_tvl, activity, ranks)
    output_files.append(write_csv(dirs["tables"] / "T37_market_structure_feature_panel.csv", feature_panel))

    output_files.extend(write_reports(project_root, feature_panel, endpoint_rows, skipped))
    output_files.extend(render_market_structure_figures(project_root))
    output_files.append(update_outputs_readme(project_root))
    output_files.append(patch_outputs_manifest(project_root, output_files, skipped))
    return MarketStructureBuildResult(curated_files=[], output_files=output_files, skipped=skipped)


def write_reports(
    project_root: Path,
    feature_panel: pd.DataFrame,
    endpoint_rows: pd.DataFrame,
    skipped: list[str],
) -> list[Path]:
    report_dir = project_root / "outputs" / "report"
    rows = int(feature_panel["rows"].sum()) if not feature_panel.empty else 0
    key_required = endpoint_rows[endpoint_rows["requires_key_env"].astype(str) != ""] if "requires_key_env" in endpoint_rows else pd.DataFrame()
    key_available = int(key_required["key_available"].sum()) if "key_available" in key_required else 0
    return [
        write_text(
            report_dir / "market_evolution_thesis.md",
            f"""# Market Evolution Thesis

The market-structure extension adds a public, reduced-form context layer around the factor lab: DeFi TVL, stablecoin supply, CEX/DEX activity, sentiment, BTC dominance/cycle markers, RWA/DAT growth, and optional Binance liquidity ranks.

The release is designed to work without paid/live data. It uses the frozen tracked dataset first and enriches from `data_cache/` only when optional DefiLlama, Binance, or CoinMarketCap cache is available. Generated feature rows across the public market-structure tables: {rows}.

Interpretation stays descriptive. Binance ranks are exchange-liquidity ranks, stablecoin/TVL variables are liquidity proxies, and ETF-flow language remains contemporaneous association rather than causal identification.
""",
        ),
        write_text(
            report_dir / "market_structure_methodology.md",
            """# Market-Structure Methodology

Raw optional payloads are stored in gitignored `data_cache/{defillama,binance,coinmarketcap}/raw`. Normalized release-ready CSVs are written under `Data/MarketStructure/`.

Point-in-time market-cap top100 universes require point-in-time market-cap source data. The pipeline refuses to backfill a historical top100 from a current list. Binance top100 outputs are labeled as exchange-liquidity ranks based on rolling quote volume.

CMC Fear & Greed uses the official `v3/fear-and-greed/historical` client when `CMC_API_KEY` is available. Without that key, the tracked AlternativeMe series remains the baseline sentiment source.
""",
        ),
        write_text(
            report_dir / "market_structure_data_inventory.md",
            """# Market-Structure Data Inventory

Primary public tables:

- `T28_market_structure_source_capabilities.csv`
- `T29_asset_classification.csv`
- `T30_binance_liquidity_top100.csv`
- `T31_sentiment_comparison.csv`
- `T32_stablecoin_tvl_regimes.csv`
- `T33_cex_dex_activity.csv`
- `T34_btc_cycle_overlay.csv`
- `T35_rwa_dat_growth.csv`
- `T36_market_cap_top100_gap.csv`
- `T37_market_structure_feature_panel.csv`

Curated source files live under `Data/MarketStructure/`. Existing frozen data under `Data/DefiLlama`, `Data/AlternativeMe`, and `Data/Tradingview` remains unchanged.
""",
        ),
        write_text(
            report_dir / "market_structure_limitations.md",
            """# Market-Structure Limitations

- DefiLlama Pro-only datasets are skipped when key or plan access is missing.
- Binance does not provide historical market-cap rankings, so the Binance universe is liquidity-ranked only.
- Current order-book and ticker endpoints are snapshots and are not used as historical depth.
- Stablecoin supply and TVL are proxies, not proven causal drivers.
- CMC Fear & Greed is unavailable unless `CMC_API_KEY` is configured.
""",
        ),
        write_text(
            report_dir / "market_structure_fetch_diagnostics.md",
            f"""# Market-Structure Fetch Diagnostics

Endpoint rows audited: {len(endpoint_rows)}

Optional key-gated endpoints available now: {key_available}/{len(key_required)}

Skipped outputs:
{chr(10).join(f"- {item}" for item in skipped) if skipped else "- None"}

No API keys are written to public outputs. Raw payloads, when fetched, remain in `data_cache/`.
""",
        ),
    ]


def _style_axis(ax: plt.Axes) -> None:
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=COLORS["grid"], alpha=0.35)
    ax.tick_params(colors=COLORS["text"], labelsize=8)


def save_fig(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def render_market_structure_figures(project_root: Path) -> list[Path]:
    tables = project_root / "outputs" / "tables"
    figures = project_root / "outputs" / "figures"
    apply_institutional_mpl_theme()
    written: list[Path] = []

    feature_panel = pd.read_csv(tables / "T37_market_structure_feature_panel.csv")
    fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    ax.barh(feature_panel["feature_family"], feature_panel["rows"], color=COLORS["institutional"])
    ax.set_title("Market-Structure Extension Coverage", color=COLORS["text"], fontweight="bold")
    ax.set_xlabel("Rows in public tables")
    _style_axis(ax)
    written.append(save_fig(fig, figures / "F30_market_structure_dashboard.png"))

    st = pd.read_csv(tables / "T32_stablecoin_tvl_regimes.csv", parse_dates=["date"])
    fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    if not st.empty:
        ax.plot(st["date"], st["defi_tvl_usd"], label="DeFi TVL", color=COLORS["eth"])
        ax.plot(st["date"], st["stablecoins_mcap_usd"], label="Stablecoin mcap", color=COLORS["stablecoin"])
        ax.set_yscale("log")
    ax.set_title("Stablecoins and TVL Regimes", color=COLORS["text"], fontweight="bold")
    ax.legend(frameon=False)
    _style_axis(ax)
    written.append(save_fig(fig, figures / "F31_stablecoin_tvl_regimes.png"))

    sent = pd.read_csv(tables / "T31_sentiment_comparison.csv", parse_dates=["date"])
    fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    for source, data in sent.groupby("source"):
        ax.plot(data["date"], data["fng_value"], label=source, linewidth=1.2)
    ax.set_ylim(0, 100)
    ax.set_title("Fear & Greed Sentiment Comparison", color=COLORS["text"], fontweight="bold")
    ax.legend(frameon=False)
    _style_axis(ax)
    written.append(save_fig(fig, figures / "F32_sentiment_comparison.png"))

    activity = pd.read_csv(tables / "T33_cex_dex_activity.csv", parse_dates=["date"])
    fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    for metric, data in activity.groupby("metric"):
        ax.plot(data["date"], data["value"].abs(), label=metric, linewidth=1.2)
    ax.set_yscale("log")
    ax.set_title("CEX and DEX Activity Context", color=COLORS["text"], fontweight="bold")
    ax.legend(frameon=False)
    _style_axis(ax)
    written.append(save_fig(fig, figures / "F33_cex_dex_activity.png"))

    ranks = pd.read_csv(tables / "T30_binance_liquidity_top100.csv")
    fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    if "rolling_quote_volume_usd" in ranks and pd.to_numeric(ranks["rolling_quote_volume_usd"], errors="coerce").notna().any():
        latest_month = ranks["month"].dropna().iloc[-1]
        latest = ranks[ranks["month"] == latest_month].head(20)
        ax.barh(latest["symbol"], pd.to_numeric(latest["rolling_quote_volume_usd"], errors="coerce"), color=COLORS["btc"])
    else:
        ax.text(0.5, 0.5, "No Binance kline cache\nliquidity ranks skipped", ha="center", va="center", color=COLORS["muted"], transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
    ax.set_title("Binance Exchange-Liquidity Universe", color=COLORS["text"], fontweight="bold")
    _style_axis(ax)
    written.append(save_fig(fig, figures / "F34_binance_liquidity_universe.png"))

    cycle = pd.read_csv(tables / "T34_btc_cycle_overlay.csv", parse_dates=["date"])
    fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    if not cycle.empty:
        ax.plot(cycle["date"], cycle["btc_dominance_close"], color=COLORS["btc"], linewidth=1.2)
        for date_str, label in [("2020-05-11", "2020 halving"), ("2024-01-11", "BTC ETF"), ("2024-04-20", "2024 halving"), ("2024-07-23", "ETH ETF")]:
            ax.axvline(pd.Timestamp(date_str), color=COLORS["neutral"], linewidth=0.8, alpha=0.5)
            ax.text(pd.Timestamp(date_str), ax.get_ylim()[1], label, rotation=90, va="top", fontsize=7, color=COLORS["muted"])
    ax.set_title("BTC Dominance With Cycle Markers", color=COLORS["text"], fontweight="bold")
    _style_axis(ax)
    written.append(save_fig(fig, figures / "F35_btc_dominance_cycle_overlay.png"))

    rwa = pd.read_csv(tables / "T35_rwa_dat_growth.csv", parse_dates=["date"])
    fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    for metric, data in rwa.groupby("metric"):
        ax.plot(data["date"], data["value"], label=metric, marker="o", linewidth=1.2)
    ax.set_title("RWA and DAT Growth Context", color=COLORS["text"], fontweight="bold")
    handles, _ = ax.get_legend_handles_labels()
    if handles:
        ax.legend(frameon=False)
    _style_axis(ax)
    written.append(save_fig(fig, figures / "F36_rwa_dat_growth.png"))

    gap = pd.read_csv(tables / "T36_market_cap_top100_gap.csv")
    fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    ax.axis("off")
    ax.text(0.02, 0.75, "Market-Cap Top100", color=COLORS["text"], fontsize=18, fontweight="bold", transform=ax.transAxes)
    ax.text(0.02, 0.55, str(gap.loc[0, "status"]).upper(), color=COLORS["risk"], fontsize=28, fontweight="bold", transform=ax.transAxes)
    ax.text(0.02, 0.36, str(gap.loc[0, "reason"]), color=COLORS["muted"], fontsize=11, wrap=True, transform=ax.transAxes)
    ax.text(0.02, 0.18, "Guardrail: no current-top100 historical backfill.", color=COLORS["muted"], fontsize=10, transform=ax.transAxes)
    written.append(save_fig(fig, figures / "F37_market_cap_top100_gap.png"))

    return written


def update_outputs_readme(project_root: Path) -> Path:
    """Add the market-structure extension map to outputs/README.md."""

    path = project_root / "outputs" / "README.md"
    text = path.read_text(encoding="utf-8") if path.exists() else "# Canonical Outputs\n"
    marker = "\n## Market-Structure Extension\n"
    text = text.split(marker, 1)[0].rstrip()
    section = f"""{marker}
The additive market-structure layer integrates tracked DefiLlama/AlternativeMe/TradingView context with optional DefiLlama, Binance, and CoinMarketCap cache. It does not require API keys for the public build.

Reports:

- `report/market_evolution_thesis.md`
- `report/market_structure_methodology.md`
- `report/market_structure_data_inventory.md`
- `report/market_structure_limitations.md`
- `report/market_structure_fetch_diagnostics.md`

Figures:

- `figures/F30_market_structure_dashboard.png`
- `figures/F31_stablecoin_tvl_regimes.png`
- `figures/F32_sentiment_comparison.png`
- `figures/F33_cex_dex_activity.png`
- `figures/F34_binance_liquidity_universe.png`
- `figures/F35_btc_dominance_cycle_overlay.png`
- `figures/F36_rwa_dat_growth.png`
- `figures/F37_market_cap_top100_gap.png`

Tables:

- `tables/T28_market_structure_source_capabilities.csv`
- `tables/T29_asset_classification.csv`
- `tables/T30_binance_liquidity_top100.csv`
- `tables/T31_sentiment_comparison.csv`
- `tables/T32_stablecoin_tvl_regimes.csv`
- `tables/T33_cex_dex_activity.csv`
- `tables/T34_btc_cycle_overlay.csv`
- `tables/T35_rwa_dat_growth.csv`
- `tables/T36_market_cap_top100_gap.csv`
- `tables/T37_market_structure_feature_panel.csv`

Guardrails:

- Binance top100 is exchange-liquidity based, not historical market-cap rank.
- CMC Fear & Greed is skipped unless `CMC_API_KEY` is available.
- Raw source responses stay in gitignored `data_cache/`.
"""
    return write_text(path, text + "\n" + section)


def patch_outputs_manifest(project_root: Path, output_files: list[Path], skipped: list[str]) -> Path:
    manifest_path = project_root / "outputs" / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {}
    manifest["market_structure"] = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source_table_bundle_date": "2026-06-18",
        "figure_bundle_start": "F30",
        "table_bundle_start": "T28",
        "commands": [
            "uv run python scripts/audit_market_structure_endpoints.py --dry-run",
            "uv run python scripts/fetch_market_structure_raw.py --dry-run",
            "uv run python scripts/fetch_market_structure_raw.py --cache-only",
            "uv run python scripts/normalize_market_structure_cache.py --cache-only",
            "uv run python scripts/build_market_structure_outputs.py",
        ],
        "outputs": [rel(path, project_root) for path in output_files if path.exists()],
        "skipped": skipped,
        "guardrails": [
            "Binance top100 is exchange-liquidity based, not market-cap based.",
            "CMC Fear & Greed is skipped without CMC_API_KEY.",
            "Raw API payloads stay in data_cache/ and are not committed.",
            "No API keys are written to outputs or manifests.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def public_surface_findings(project_root: Path) -> pd.DataFrame:
    """Scan public files for market-structure guardrail violations."""

    patterns = {
        "secret_assignment": ["DEFILLAMA_API_KEY=", "CMC_API_KEY=", "X-CMC_PRO_API_KEY="],
        "binance_market_cap_top100": ["Binance market-cap top100", "Binance market cap top100"],
        "current_top100_backfill": ["current top100 backfill", "current-top100 backfill"],
    }
    rows = []
    roots = [project_root / "README.md", project_root / "outputs", project_root / "docs", project_root / "Data" / "MarketStructure"]
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
        elif root.exists():
            files.extend(path for path in root.rglob("*") if path.suffix.lower() in {".md", ".json", ".csv", ".txt"})
    files = [path for path in files if path.name != "market_structure_public_surface_check.md"]
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for rule, terms in patterns.items():
            for term in terms:
                if term in text:
                    allowed = path.name == ".env.example" or "guardrail" in text.lower()
                    rows.append({"file": rel(path, project_root), "rule": rule, "term": term, "status": "allowed_context" if allowed else "violation"})
    if not rows:
        rows.append({"file": "", "rule": "all", "term": "", "status": "pass"})
    rows.extend(readme_public_surface_rows(project_root))
    return pd.DataFrame(rows)


def readme_public_surface_rows(project_root: Path) -> list[dict[str, str]]:
    """Run the legacy README public-surface checks."""

    readme_path = project_root / "README.md"
    if not readme_path.exists():
        return [{"file": "README.md", "rule": "readme_exists", "term": "", "status": "violation"}]
    readme = readme_path.read_text(encoding="utf-8")
    rows: list[dict[str, str]] = []
    for term in ["portfolio_v2", "v2.1", "v2.2", "v2.0", "career", "recruiter", "LinkedIn", "interview"]:
        if term.lower() in readme.lower():
            rows.append({"file": "README.md", "rule": "banned_readme_term", "term": term, "status": "violation"})
    if "results at a glance" not in readme.lower():
        rows.append({"file": "README.md", "rule": "required_section", "term": "Results at a Glance", "status": "violation"})
    if "t11_results_at_a_glance.md" not in readme.lower():
        rows.append({"file": "README.md", "rule": "required_table_link", "term": "T11_results_at_a_glance.md", "status": "violation"})
    old_figs = [
        "F02_btc_model_sensitivity.png",
        "F01_data_inventory.png",
        "F02_btc_model_sensitivity",
        "F01_data_inventory",
    ]
    for raw_path in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme):
        if "archive/" in raw_path or "reports/portfolio_" in raw_path:
            rows.append({"file": "README.md", "rule": "banned_image_path", "term": raw_path, "status": "violation"})
        for old_fig in old_figs:
            if old_fig in raw_path:
                rows.append({"file": "README.md", "rule": "old_figure_name", "term": old_fig, "status": "violation"})
        if not (project_root / raw_path).exists():
            rows.append({"file": "README.md", "rule": "missing_image_path", "term": raw_path, "status": "violation"})
    return rows


def write_public_surface_report(project_root: Path = ROOT) -> Path:
    findings = public_surface_findings(project_root)
    path = project_root / "outputs" / "report" / "market_structure_public_surface_check.md"
    violations = findings[findings["status"] == "violation"]
    text = f"""# Market-Structure Public Surface Check

Generated at: {utc_now_iso()}

Verdict: {"PASS" if violations.empty else "FAIL"}

Findings:

{findings.to_markdown(index=False)}
"""
    return write_text(path, text)
