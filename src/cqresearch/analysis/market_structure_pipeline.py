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
from matplotlib.ticker import PercentFormatter

from cqresearch.analysis.asset_classification import (
    classification_summary,
    classify_symbol_frame,
    load_classification_overrides,
)
from cqresearch.analysis.constituent_rotation import (
    build_constituent_rotation_tables,
    constituent_rotation_summary,
    load_daily_constituents,
)
from cqresearch.analysis.market_universe import (
    MONTHLY_UNIVERSE_CURATED,
    build_binance_liquidity_ranks,
    build_market_structure_daily_context,
    classify_market_universe,
    clean_risk_top100,
    cycle_phase_market_structure,
    market_cap_top100_gap_report,
    market_evolution_summary,
    market_structure_composition,
    market_structure_composition_shift,
    market_structure_modeling_summary,
    market_structure_monthly_features,
    market_structure_return_regimes,
    market_structure_turnover_by_phase,
    rank_turnover,
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
plt.switch_backend("Agg")


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
        "sentiment": data_root / "Sentiment",
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

The optional `crypto_universe_monthly_2020_2026.csv` file is a local point-in-time monthly top200 market-cap universe. It is ingested from `data_cache/defillama/` only after validation and supports composition, concentration, clean-risk universe, rank-turnover, and cycle-phase structure diagnostics.

The optional `top50_current_ex_stable_daily_ohlcv_2020_2026.csv` file is a current-constituent daily OHLCV sample. It supports exploratory breadth, rotation, beta, dispersion, and event-response diagnostics, but it is not a point-in-time top100/top200 panel.
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

Contains CMC Fear & Greed normalized history when a local cache exists. Live refreshes require `CMC_API_KEY`; public output falls back to the tracked AlternativeMe series only when no CMC cache is present.
""",
        ),
        write_text(
            dirs["sentiment"] / "README.md",
            """# Sentiment Curated Layer

Contains the transparent Fear & Greed blend and source-overlap diagnostics. The blended file uses AlternativeMe before 2023-06-29 and CoinMarketCap from 2023-06-29 onward, with a `source` column preserved on every row.
""",
        ),
    ]
    return written


def source_registry(project_root: Path) -> pd.DataFrame:
    defillama_count = len(list((project_root / "Data" / "DefiLlama").rglob("*.csv")))
    binance_count = len(
        list((project_root / "Data" / "MarketStructure" / "Binance").rglob("*.csv"))
    )
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
                "tracked_files": binance_count,
                "auth_required": "no",
                "storage_policy": "raw cache in data_cache/binance; curated summaries in Data/MarketStructure/Binance",
                "status": "optional_public_fetch_or_cache",
            },
            {
                "source": "CoinMarketCap",
                "role": "Fear & Greed historical sentiment comparison",
                "tracked_files": len(
                    list(
                        (project_root / "Data" / "MarketStructure" / "CoinMarketCap").rglob("*.csv")
                    )
                ),
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


def normalize_cache_to_curated(
    project_root: Path = ROOT, *, cache_only: bool = False
) -> MarketStructureBuildResult:
    """Normalize local raw cache into tracked curated CSVs."""

    dirs = ensure_dirs(project_root)
    layout = CacheLayout.from_env(project_root)
    written = write_readmes(project_root)
    skipped: list[str] = []

    endpoint_rows = pd.DataFrame(endpoint_audit_rows(all_endpoint_specs()))
    written.append(
        write_csv(dirs["registry"] / "market_structure_endpoint_capabilities.csv", endpoint_rows)
    )

    registry = source_registry(project_root)
    written.append(write_csv(dirs["registry"] / "market_structure_source_registry.csv", registry))

    defillama_existing = inventory_existing_defillama(project_root)
    written.append(
        write_csv(dirs["defillama"] / "defillama_existing_inventory.csv", defillama_existing)
    )

    written.extend(normalize_defillama_cache(layout, dirs["defillama"], skipped))
    written.extend(normalize_binance_cache(layout, dirs["binance"], skipped))
    written.extend(normalize_cmc_cache(layout, dirs["cmc"], skipped))
    written.extend(write_sentiment_blend_files(project_root, dirs["sentiment"], skipped))

    status_rows = (
        [{"status": "cache_only", "detail": "No network calls were made."}] if cache_only else []
    )
    status_rows.extend({"status": "skipped", "detail": item} for item in skipped)
    written.append(
        write_csv(dirs["registry"] / "market_structure_cache_status.csv", pd.DataFrame(status_rows))
    )

    update_master_inventory(project_root)
    return MarketStructureBuildResult(curated_files=written, output_files=[], skipped=skipped)


def inventory_existing_defillama(project_root: Path) -> pd.DataFrame:
    rows = []
    for path in sorted((project_root / "Data" / "DefiLlama").rglob("*.csv")):
        try:
            meta = csv_inventory_row(
                path, "DefiLlama", "Existing curated DefiLlama source file", project_root
            )
        except Exception:
            continue
        rows.append(meta)
    return pd.DataFrame(rows)


def _cached_payloads(
    layout: CacheLayout, source: str, dataset_prefix: str
) -> list[tuple[Path, Any]]:
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
        written.append(
            write_csv(
                out_dir / "defillama_chains_current.csv", normalize_defillama_chains(chains[-1][1])
            )
        )
    else:
        skipped.append("DefiLlama chains_current cache unavailable.")

    stable = _cached_payloads(layout, "defillama", "stablecoins_current")
    if stable:
        written.append(
            write_csv(
                out_dir / "defillama_stablecoins_current.csv",
                normalize_defillama_stablecoins(stable[-1][1]),
            )
        )

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
        written.append(
            write_csv(
                out_dir / "binance_spot_24h_tickers_snapshot.csv",
                normalize_binance_24h_tickers(tickers[-1][1]),
            )
        )

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
        skipped.append(
            "Binance spot daily kline cache unavailable; liquidity top100 not generated."
        )

    funding_frames = []
    for path, payload in _cached_payloads(layout, "binance", "usd_m_funding_rate"):
        _ = path
        frame = normalize_binance_funding_rates(payload)
        if not frame.empty:
            funding_frames.append(frame)
    if funding_frames:
        written.append(
            write_csv(
                out_dir / "binance_usd_m_funding_rates.csv",
                pd.concat(funding_frames, ignore_index=True),
            )
        )
    return written


def normalize_cmc_cache(layout: CacheLayout, out_dir: Path, skipped: list[str]) -> list[Path]:
    written: list[Path] = []
    payloads = _cached_payloads(layout, "coinmarketcap", "fear_greed_historical")
    if not payloads:
        skipped.append(
            "CMC Fear & Greed cache unavailable; AlternativeMe remains the tracked sentiment baseline."
        )
        return written
    frames = [normalize_cmc_fear_greed(payload) for _, payload in payloads]
    out = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["date"]).sort_values("date")
    written.append(write_csv(out_dir / "cmc_fear_greed__daily.csv", out))
    return written


def load_alt_and_cmc_fear_greed(project_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load AlternativeMe and curated CMC Fear & Greed frames."""

    alt_path = project_root / "Data" / "AlternativeMe" / "fear_greed_index__daily.csv"
    cmc_path = (
        project_root / "Data" / "MarketStructure" / "CoinMarketCap" / "cmc_fear_greed__daily.csv"
    )
    alt = pd.DataFrame(columns=["date", "alt_value", "alt_classification"])
    cmc = pd.DataFrame(columns=["date", "cmc_value", "cmc_classification"])
    if alt_path.exists():
        alt = pd.read_csv(alt_path, parse_dates=["date"]).rename(
            columns={"fng_value": "alt_value", "fng_classification": "alt_classification"}
        )
    if cmc_path.exists():
        cmc = pd.read_csv(cmc_path, parse_dates=["date"]).rename(
            columns={"fng_value": "cmc_value", "fng_classification": "cmc_classification"}
        )
    return alt[["date", "alt_value", "alt_classification"]], cmc[
        ["date", "cmc_value", "cmc_classification"]
    ]


def sentiment_overlap_diagnostics(project_root: Path) -> pd.DataFrame:
    """Return daily overlap diagnostics between AlternativeMe and CMC."""

    alt, cmc = load_alt_and_cmc_fear_greed(project_root)
    if alt.empty or cmc.empty:
        return pd.DataFrame(
            columns=[
                "date",
                "alt_value",
                "cmc_value",
                "diff_cmc_minus_alt",
                "abs_diff",
                "alt_classification",
                "cmc_classification",
                "same_classification",
            ]
        )
    merged = alt.merge(cmc, on="date", how="inner")
    merged["diff_cmc_minus_alt"] = merged["cmc_value"] - merged["alt_value"]
    merged["abs_diff"] = merged["diff_cmc_minus_alt"].abs()
    merged["same_classification"] = (
        merged["alt_classification"].astype(str).str.lower().str.strip()
        == merged["cmc_classification"].astype(str).str.lower().str.strip()
    )
    merged["date"] = merged["date"].dt.date
    return merged[
        [
            "date",
            "alt_value",
            "cmc_value",
            "diff_cmc_minus_alt",
            "abs_diff",
            "alt_classification",
            "cmc_classification",
            "same_classification",
        ]
    ].sort_values("date")


def sentiment_overlap_summary(
    project_root: Path, *, splice_date: str = "2023-06-29"
) -> pd.DataFrame:
    """Summarize AlternativeMe vs CMC overlap and splice risk."""

    overlap = sentiment_overlap_diagnostics(project_root)
    alt, cmc = load_alt_and_cmc_fear_greed(project_root)
    rows: list[dict[str, object]] = []
    if overlap.empty:
        return pd.DataFrame(
            [
                {
                    "metric": "overlap_rows",
                    "value": 0,
                    "note": "CMC or AlternativeMe data unavailable.",
                }
            ]
        )

    def add(metric: str, value: object, note: str = "") -> None:
        rows.append({"metric": metric, "value": value, "note": note})

    add("overlap_rows", len(overlap))
    add("overlap_start", str(overlap["date"].min()))
    add("overlap_end", str(overlap["date"].max()))
    add(
        "pearson_correlation",
        round(float(overlap[["alt_value", "cmc_value"]].corr().iloc[0, 1]), 4),
    )
    add("mean_diff_cmc_minus_alt", round(float(overlap["diff_cmc_minus_alt"].mean()), 4))
    add("median_diff_cmc_minus_alt", round(float(overlap["diff_cmc_minus_alt"].median()), 4))
    add("mean_abs_diff", round(float(overlap["abs_diff"].mean()), 4))
    add("median_abs_diff", round(float(overlap["abs_diff"].median()), 4))
    add("p90_abs_diff", round(float(overlap["abs_diff"].quantile(0.90)), 4))
    add("max_abs_diff", round(float(overlap["abs_diff"].max()), 4))
    add("share_abs_diff_le_5", round(float((overlap["abs_diff"] <= 5).mean()), 4))
    add("share_abs_diff_le_10", round(float((overlap["abs_diff"] <= 10).mean()), 4))
    add("classification_match_rate", round(float(overlap["same_classification"].mean()), 4))

    splice = pd.Timestamp(splice_date)
    if not alt.empty and not cmc.empty:
        prev_alt = alt.loc[alt["date"] == splice - pd.Timedelta(days=1), "alt_value"]
        first_cmc = cmc.loc[cmc["date"] == splice, "cmc_value"]
        same_day_alt = alt.loc[alt["date"] == splice, "alt_value"]
        if not prev_alt.empty and not first_cmc.empty:
            add(
                "splice_jump_alt_prev_day_to_cmc_start",
                round(float(first_cmc.iloc[0] - prev_alt.iloc[0]), 4),
                f"AlternativeMe {(splice - pd.Timedelta(days=1)).date()} to CMC {splice.date()}",
            )
        if not same_day_alt.empty and not first_cmc.empty:
            add(
                "same_day_cmc_minus_alt_on_splice_date",
                round(float(first_cmc.iloc[0] - same_day_alt.iloc[0]), 4),
            )
        alt_last_date = alt["date"].max()
        cmc_next = cmc.loc[cmc["date"] == alt_last_date + pd.Timedelta(days=1), "cmc_value"]
        alt_last = alt.loc[alt["date"] == alt_last_date, "alt_value"]
        if not alt_last.empty and not cmc_next.empty:
            add(
                "jump_if_alt_used_until_its_end_then_cmc",
                round(float(cmc_next.iloc[0] - alt_last.iloc[0]), 4),
                "Shows why switching at CMC start is cleaner than waiting until AlternativeMe ends.",
            )
    add(
        "recommendation",
        "acceptable_with_source_flag",
        "Use as a coverage blend, not as proof the vendors are identical.",
    )
    return pd.DataFrame(rows)


def build_blended_fear_greed(
    project_root: Path, *, splice_date: str = "2023-06-29"
) -> pd.DataFrame:
    """Blend AlternativeMe before CMC starts and CMC after the splice date."""

    alt, cmc = load_alt_and_cmc_fear_greed(project_root)
    if alt.empty or cmc.empty:
        return pd.DataFrame(
            columns=[
                "date",
                "fng_value",
                "fng_classification",
                "source",
                "splice_rule",
                "is_post_splice",
            ]
        )
    splice = pd.Timestamp(splice_date)
    alt_part = alt[alt["date"] < splice].rename(
        columns={"alt_value": "fng_value", "alt_classification": "fng_classification"}
    )
    alt_part["source"] = "alternative_me"
    cmc_part = cmc[cmc["date"] >= splice].rename(
        columns={"cmc_value": "fng_value", "cmc_classification": "fng_classification"}
    )
    cmc_part["source"] = "coinmarketcap"
    blended = pd.concat(
        [
            alt_part[["date", "fng_value", "fng_classification", "source"]],
            cmc_part[["date", "fng_value", "fng_classification", "source"]],
        ],
        ignore_index=True,
    ).sort_values("date")
    blended["splice_rule"] = (
        f"alternative_me_before_{splice_date}__coinmarketcap_from_{splice_date}"
    )
    blended["is_post_splice"] = blended["date"] >= splice
    blended["date"] = blended["date"].dt.date
    return blended[
        ["date", "fng_value", "fng_classification", "source", "splice_rule", "is_post_splice"]
    ]


def write_sentiment_blend_files(
    project_root: Path, out_dir: Path, skipped: list[str]
) -> list[Path]:
    """Write the curated blended Fear & Greed file and overlap diagnostics."""

    written: list[Path] = []
    blended = build_blended_fear_greed(project_root)
    overlap = sentiment_overlap_diagnostics(project_root)
    summary = sentiment_overlap_summary(project_root)
    if blended.empty:
        skipped.append(
            "Fear & Greed blend skipped because CMC or AlternativeMe data is unavailable."
        )
        return written
    written.append(write_csv(out_dir / "fear_greed_altme_pre_cmc_post__daily.csv", blended))
    written.append(write_csv(out_dir / "fear_greed_source_overlap__daily.csv", overlap))
    written.append(write_csv(out_dir / "fear_greed_source_overlap_summary.csv", summary))
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
    cmc_path = (
        project_root / "Data" / "MarketStructure" / "CoinMarketCap" / "cmc_fear_greed__daily.csv"
    )
    if cmc_path.exists():
        frames.append(pd.read_csv(cmc_path))
    if not frames:
        return pd.DataFrame(columns=["source", "date", "fng_value", "fng_classification"])
    return pd.concat(frames, ignore_index=True).sort_values(["source", "date"])


def stablecoin_tvl_regimes(project_root: Path) -> pd.DataFrame:
    metrics_path = (
        project_root / "Data" / "DefiLlama" / "ChainMetrics" / "all_dex_metrics__daily.csv"
    )
    tvl_path = project_root / "Data" / "DefiLlama" / "TVL" / "Daily" / "tvl_all_chains_daily.csv"
    if not metrics_path.exists() and not tvl_path.exists():
        return pd.DataFrame(
            columns=[
                "date",
                "defi_tvl_usd",
                "stablecoins_mcap_usd",
                "dex_volume_usd",
                "stablecoin_tvl_ratio",
                "regime",
            ]
        )

    if metrics_path.exists():
        metrics = pd.read_csv(metrics_path, parse_dates=["date"])
        frame = pd.DataFrame({"date": metrics["date"]})
        frame["stablecoins_mcap_usd"] = pd.to_numeric(
            metrics.get("Stablecoins Mcap"), errors="coerce"
        )
        frame["dex_volume_usd"] = pd.to_numeric(metrics.get("DEXs Volume"), errors="coerce")
        frame["defi_tvl_usd"] = pd.to_numeric(metrics.get("TVL"), errors="coerce")
    else:
        frame = pd.DataFrame()
    if tvl_path.exists():
        tvl = pd.read_csv(tvl_path, parse_dates=["date"])
        tvl["defi_tvl_usd_alt"] = pd.to_numeric(tvl.get("TVL"), errors="coerce")
        frame = (
            frame.merge(tvl[["date", "defi_tvl_usd_alt"]], on="date", how="outer")
            if not frame.empty
            else tvl[["date", "defi_tvl_usd_alt"]]
        )
        frame["defi_tvl_usd"] = (
            frame.get("defi_tvl_usd").combine_first(frame["defi_tvl_usd_alt"])
            if "defi_tvl_usd" in frame
            else frame["defi_tvl_usd_alt"]
        )
    frame = frame.drop(columns=[col for col in ["defi_tvl_usd_alt"] if col in frame])
    frame["stablecoin_tvl_ratio"] = frame["stablecoins_mcap_usd"] / frame["defi_tvl_usd"]
    monthly = frame.set_index("date").resample("ME").last().reset_index()
    median = monthly["stablecoin_tvl_ratio"].median(skipna=True)
    monthly["regime"] = monthly["stablecoin_tvl_ratio"].map(
        lambda value: (
            "high_stablecoin_to_tvl"
            if pd.notna(value) and value >= median
            else "low_stablecoin_to_tvl"
        )
    )
    monthly["date"] = monthly["date"].dt.date
    return monthly


def cex_dex_activity(project_root: Path) -> pd.DataFrame:
    dex_path = project_root / "Data" / "DefiLlama" / "ChainMetrics" / "all_dex_metrics__daily.csv"
    cex_path = (
        project_root / "Data" / "DefiLlama" / "CEX" / "cex_net_inflows_by_exchange__daily.csv"
    )
    frames: list[pd.DataFrame] = []
    if dex_path.exists():
        dex = pd.read_csv(dex_path, parse_dates=["date"])
        frames.append(
            pd.DataFrame(
                {
                    "date": dex["date"],
                    "metric": "dex_volume_usd",
                    "value": pd.to_numeric(dex.get("DEXs Volume"), errors="coerce"),
                }
            )
        )
    if cex_path.exists():
        cex = pd.read_csv(cex_path, parse_dates=["date"])
        value_cols = [col for col in cex.columns if col != "date"]
        values = cex[value_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1, min_count=1)
        frames.append(
            pd.DataFrame({"date": cex["date"], "metric": "cex_net_inflows_usd", "value": values})
        )
    if not frames:
        return pd.DataFrame(columns=["date", "metric", "value"])
    out = pd.concat(frames, ignore_index=True)
    out = (
        out.set_index("date")
        .groupby("metric")
        .resample("ME")["value"]
        .sum(min_count=1)
        .reset_index()
    )
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
        rows.append(
            pd.DataFrame({"date": rwa["date"], "metric": "rwa_onchain_mcap_usd", "value": values})
        )
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


def load_monthly_market_universe(
    project_root: Path, overrides: dict[str, set[str]]
) -> pd.DataFrame:
    """Load the normalized monthly point-in-time market-cap universe when present."""

    path = project_root / MONTHLY_UNIVERSE_CURATED
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_csv(path, parse_dates=["snapshot_date"])
    frame["snapshot_date"] = frame["snapshot_date"].dt.date
    return classify_market_universe(frame, overrides)


def write_market_cap_universe_outputs(
    project_root: Path,
    dirs: dict[str, Path],
    universe: pd.DataFrame,
) -> list[Path]:
    """Write market-cap universe tables when a point-in-time source exists."""

    if universe.empty:
        return []
    output_files: list[Path] = []
    clean_risk = clean_risk_top100(universe)
    composition = market_structure_composition(universe)
    turnover = rank_turnover(universe)
    cycle_phase = cycle_phase_market_structure(composition)
    summary = market_evolution_summary(universe, composition, turnover)
    output_files.append(write_csv(dirs["tables"] / "T40_crypto_universe_monthly.csv", universe))
    output_files.append(write_csv(dirs["tables"] / "T41_clean_risk_top100_monthly.csv", clean_risk))
    output_files.append(
        write_csv(dirs["tables"] / "T42_market_structure_composition.csv", composition)
    )
    output_files.append(write_csv(dirs["tables"] / "T43_rank_turnover.csv", turnover))
    output_files.append(
        write_csv(dirs["tables"] / "T44_cycle_phase_market_structure.csv", cycle_phase)
    )
    output_files.append(write_text(dirs["tables"] / "T45_market_evolution_summary.md", summary))
    output_files.extend(
        write_market_structure_feature_outputs(project_root, dirs, universe, composition, turnover)
    )
    return output_files


def write_market_structure_feature_outputs(
    project_root: Path,
    dirs: dict[str, Path],
    universe: pd.DataFrame,
    composition: pd.DataFrame,
    turnover: pd.DataFrame,
) -> list[Path]:
    """Write monthly feature, daily context, and descriptive regime diagnostics."""

    output_files: list[Path] = []
    monthly_features = market_structure_monthly_features(universe, composition, turnover)
    output_files.append(
        write_csv(dirs["tables"] / "T46_market_structure_monthly_features.csv", monthly_features)
    )

    panel_path = project_root / "reports" / "panels" / "master_daily.parquet"
    if panel_path.exists():
        try:
            daily_panel = pd.read_parquet(panel_path)
        except (ImportError, ValueError, OSError) as exc:
            daily_panel = pd.DataFrame()
            note = f"Daily context skipped because master_daily.parquet could not be read: {exc}"
        else:
            note = ""
    else:
        daily_panel = pd.DataFrame()
        note = "Daily context skipped because reports/panels/master_daily.parquet is unavailable."

    daily_context = build_market_structure_daily_context(daily_panel, monthly_features)
    return_regimes = market_structure_return_regimes(daily_context)
    composition_shift = market_structure_composition_shift(monthly_features)
    turnover_by_phase = market_structure_turnover_by_phase(monthly_features)
    summary = market_structure_modeling_summary(
        monthly_features,
        daily_context,
        return_regimes,
        composition_shift,
        turnover_by_phase,
    )
    if note:
        summary += f"\n\nPipeline note: {note}\n"
    output_files.append(
        write_csv(dirs["tables"] / "T47_market_structure_daily_context.csv", daily_context)
    )
    output_files.append(
        write_csv(dirs["tables"] / "T48_market_structure_return_regimes.csv", return_regimes)
    )
    output_files.append(
        write_csv(dirs["tables"] / "T49_market_structure_composition_shift.csv", composition_shift)
    )
    output_files.append(
        write_csv(dirs["tables"] / "T50_market_structure_turnover_by_phase.csv", turnover_by_phase)
    )
    output_files.append(
        write_text(dirs["tables"] / "T51_market_structure_modeling_summary.md", summary)
    )
    output_files.append(
        write_text(
            project_root / "outputs" / "report" / "market_structure_modeling_thesis.md", summary
        )
    )
    return output_files


def write_constituent_rotation_outputs(
    project_root: Path,
    dirs: dict[str, Path],
    daily_constituents: pd.DataFrame,
) -> tuple[list[Path], list[str]]:
    """Write daily constituent breadth, rotation, beta, and event-response outputs."""

    if daily_constituents.empty:
        remove_constituent_rotation_outputs(project_root)
        return [], [
            "Daily constituent OHLCV skipped because no normalized top50 constituent file exists."
        ]

    output_files: list[Path] = []
    tables = build_constituent_rotation_tables(
        daily_constituents,
        events_path=project_root / "config" / "events.yml",
    )
    output_files.append(
        write_csv(dirs["tables"] / "T52_constituent_daily_ohlcv.csv", daily_constituents)
    )
    output_files.append(write_csv(dirs["tables"] / "T53_altseason_breadth.csv", tables["breadth"]))
    output_files.append(
        write_csv(dirs["tables"] / "T54_constituent_return_indexes.csv", tables["indexes"])
    )
    output_files.append(
        write_csv(dirs["tables"] / "T55_return_dispersion.csv", tables["dispersion"])
    )
    output_files.append(
        write_csv(dirs["tables"] / "T56_rolling_beta_to_btc_eth.csv", tables["beta"])
    )
    output_files.append(
        write_csv(dirs["tables"] / "T57_category_rotation_returns.csv", tables["rotation"])
    )
    output_files.append(
        write_csv(dirs["tables"] / "T58_event_response_top50.csv", tables["events"])
    )
    output_files.append(
        write_csv(dirs["tables"] / "T59_constituent_data_gap_report.csv", tables["gap"])
    )
    summary = constituent_rotation_summary(tables)
    output_files.append(write_text(dirs["tables"] / "T60_altseason_rotation_summary.md", summary))
    output_files.append(
        write_text(project_root / "outputs" / "report" / "altseason_rotation_lab.md", summary)
    )
    return output_files, []


def remove_market_cap_universe_outputs(project_root: Path) -> None:
    """Remove stale market-cap universe outputs when the source is unavailable."""

    for relpath in [
        "outputs/tables/T40_crypto_universe_monthly.csv",
        "outputs/tables/T41_clean_risk_top100_monthly.csv",
        "outputs/tables/T42_market_structure_composition.csv",
        "outputs/tables/T43_rank_turnover.csv",
        "outputs/tables/T44_cycle_phase_market_structure.csv",
        "outputs/tables/T45_market_evolution_summary.md",
        "outputs/tables/T46_market_structure_monthly_features.csv",
        "outputs/tables/T47_market_structure_daily_context.csv",
        "outputs/tables/T48_market_structure_return_regimes.csv",
        "outputs/tables/T49_market_structure_composition_shift.csv",
        "outputs/tables/T50_market_structure_turnover_by_phase.csv",
        "outputs/tables/T51_market_structure_modeling_summary.md",
        "outputs/figures/F38_market_structure_composition.png",
        "outputs/figures/F39_top100_concentration.png",
        "outputs/figures/F40_rank_turnover.png",
        "outputs/figures/F41_cycle_phase_market_structure.png",
        "outputs/figures/F42_market_evolution_dashboard.png",
        "outputs/figures/F43_market_structure_monthly_features.png",
        "outputs/figures/F44_market_structure_return_regimes.png",
        "outputs/figures/F45_market_structure_composition_shift.png",
        "outputs/figures/F46_market_structure_turnover_by_phase.png",
        "outputs/figures/F47_market_structure_modeling_dashboard.png",
        "outputs/report/market_structure_modeling_thesis.md",
    ]:
        path = project_root / relpath
        if path.exists():
            path.unlink()


def remove_constituent_rotation_outputs(project_root: Path) -> None:
    """Remove stale daily constituent outputs when the source is unavailable."""

    for relpath in [
        "outputs/tables/T52_constituent_daily_ohlcv.csv",
        "outputs/tables/T53_altseason_breadth.csv",
        "outputs/tables/T54_constituent_return_indexes.csv",
        "outputs/tables/T55_return_dispersion.csv",
        "outputs/tables/T56_rolling_beta_to_btc_eth.csv",
        "outputs/tables/T57_category_rotation_returns.csv",
        "outputs/tables/T58_event_response_top50.csv",
        "outputs/tables/T59_constituent_data_gap_report.csv",
        "outputs/tables/T60_altseason_rotation_summary.md",
        "outputs/report/altseason_rotation_lab.md",
        "outputs/figures/F48_altseason_breadth.png",
        "outputs/figures/F49_constituent_return_indexes.png",
        "outputs/figures/F50_return_dispersion.png",
        "outputs/figures/F51_rolling_beta_to_btc.png",
        "outputs/figures/F52_event_response_top50.png",
        "outputs/figures/F53_rotation_dashboard.png",
    ]:
        path = project_root / relpath
        if path.exists():
            path.unlink()


def feature_panel_summary(
    sentiment: pd.DataFrame,
    stablecoin_tvl: pd.DataFrame,
    activity: pd.DataFrame,
    ranks: pd.DataFrame,
    market_cap_top100_rows: int = 0,
) -> pd.DataFrame:
    market_status = "available" if market_cap_top100_rows else "skipped_no_point_in_time_source"
    ranks_skipped = (
        "status" in ranks and ranks["status"].astype(str).str.startswith("skipped").all()
    )
    rank_rows = 0 if ranks.empty or ranks_skipped else len(ranks)
    rank_status = "available" if rank_rows else "skipped_no_kline_cache"
    rows = [
        {
            "feature_family": "sentiment",
            "rows": len(sentiment),
            "status": "available" if len(sentiment) else "missing",
        },
        {
            "feature_family": "stablecoin_tvl_regime",
            "rows": len(stablecoin_tvl),
            "status": "available" if len(stablecoin_tvl) else "missing",
        },
        {
            "feature_family": "cex_dex_activity",
            "rows": len(activity),
            "status": "available" if len(activity) else "missing",
        },
        {"feature_family": "binance_liquidity_top100", "rows": rank_rows, "status": rank_status},
        {
            "feature_family": "market_cap_top100",
            "rows": market_cap_top100_rows,
            "status": market_status,
        },
    ]
    return pd.DataFrame(rows)


def build_outputs(project_root: Path = ROOT) -> MarketStructureBuildResult:
    """Build market-structure public tables, figures, reports, and manifest patch."""

    dirs = ensure_dirs(project_root)
    output_files: list[Path] = []
    skipped: list[str] = []

    endpoint_rows = pd.DataFrame(endpoint_audit_rows(all_endpoint_specs()))
    output_files.append(
        write_csv(dirs["tables"] / "T28_market_structure_source_capabilities.csv", endpoint_rows)
    )

    overrides = load_classification_overrides(
        project_root / "config" / "asset_classification_overrides.yml"
    )
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
    output_files.append(
        write_csv(
            dirs["tables"] / "T29_asset_classification_summary.csv",
            classification_summary(classified),
        )
    )

    ranks_path = (
        project_root
        / "Data"
        / "MarketStructure"
        / "Binance"
        / "binance_liquidity_top100__monthly.csv"
    )
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
    if not (
        project_root / "Data" / "MarketStructure" / "CoinMarketCap" / "cmc_fear_greed__daily.csv"
    ).exists():
        skipped.append(
            "CMC Fear & Greed skipped because CMC_API_KEY/cache is unavailable; AlternativeMe baseline used."
        )
    output_files.append(write_csv(dirs["tables"] / "T31_sentiment_comparison.csv", sentiment))
    sentiment_dir = project_root / "Data" / "MarketStructure" / "Sentiment"
    blend_path = sentiment_dir / "fear_greed_altme_pre_cmc_post__daily.csv"
    overlap_summary_path = sentiment_dir / "fear_greed_source_overlap_summary.csv"
    if blend_path.exists():
        output_files.append(
            write_csv(dirs["tables"] / "T38_fear_greed_blended_daily.csv", pd.read_csv(blend_path))
        )
    if overlap_summary_path.exists():
        output_files.append(
            write_csv(
                dirs["tables"] / "T39_fear_greed_source_overlap_summary.csv",
                pd.read_csv(overlap_summary_path),
            )
        )
    stablecoin_tvl = stablecoin_tvl_regimes(project_root)
    output_files.append(
        write_csv(dirs["tables"] / "T32_stablecoin_tvl_regimes.csv", stablecoin_tvl)
    )
    activity = cex_dex_activity(project_root)
    output_files.append(write_csv(dirs["tables"] / "T33_cex_dex_activity.csv", activity))
    cycle = btc_cycle_overlay(project_root)
    output_files.append(write_csv(dirs["tables"] / "T34_btc_cycle_overlay.csv", cycle))
    rwa_dat = rwa_dat_growth(project_root)
    output_files.append(write_csv(dirs["tables"] / "T35_rwa_dat_growth.csv", rwa_dat))

    market_universe = load_monthly_market_universe(project_root, overrides)
    has_market_universe = not market_universe.empty
    gap = market_cap_top100_gap_report(has_market_universe)
    if has_market_universe:
        output_files.extend(write_market_cap_universe_outputs(project_root, dirs, market_universe))
    else:
        remove_market_cap_universe_outputs(project_root)
        skipped.append(
            "Historical market-cap top100 skipped because no point-in-time source is available."
        )
    daily_constituents = load_daily_constituents(project_root)
    constituent_files, constituent_skipped = write_constituent_rotation_outputs(
        project_root, dirs, daily_constituents
    )
    output_files.extend(constituent_files)
    skipped.extend(constituent_skipped)
    output_files.append(write_csv(dirs["tables"] / "T36_market_cap_top100_gap.csv", gap))
    market_cap_top100_rows = (
        int(market_universe["in_full_top100"].sum()) if has_market_universe else 0
    )
    feature_panel = feature_panel_summary(
        sentiment,
        stablecoin_tvl,
        activity,
        ranks,
        market_cap_top100_rows,
    )
    if blend_path.exists():
        blend_rows = len(pd.read_csv(blend_path))
        feature_panel = pd.concat(
            [
                feature_panel,
                pd.DataFrame(
                    [
                        {
                            "feature_family": "fear_greed_blended_altme_pre_cmc_post",
                            "rows": blend_rows,
                            "status": "available",
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    monthly_context_path = dirs["tables"] / "T47_market_structure_daily_context.csv"
    if monthly_context_path.exists():
        monthly_context_rows = len(pd.read_csv(monthly_context_path))
        feature_panel = pd.concat(
            [
                feature_panel,
                pd.DataFrame(
                    [
                        {
                            "feature_family": "monthly_market_structure_daily_context",
                            "rows": monthly_context_rows,
                            "status": "available"
                            if monthly_context_rows
                            else "skipped_no_daily_panel",
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    if not daily_constituents.empty:
        feature_panel = pd.concat(
            [
                feature_panel,
                pd.DataFrame(
                    [
                        {
                            "feature_family": "daily_constituent_rotation_lab",
                            "rows": len(daily_constituents),
                            "status": "available",
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    output_files.append(
        write_csv(dirs["tables"] / "T37_market_structure_feature_panel.csv", feature_panel)
    )

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
    key_required = (
        endpoint_rows[endpoint_rows["requires_key_env"].astype(str) != ""]
        if "requires_key_env" in endpoint_rows
        else pd.DataFrame()
    )
    key_available = (
        int(key_required["key_available"].sum()) if "key_available" in key_required else 0
    )
    cmc_path = (
        project_root / "Data" / "MarketStructure" / "CoinMarketCap" / "cmc_fear_greed__daily.csv"
    )
    cmc_rows = len(pd.read_csv(cmc_path)) if cmc_path.exists() else 0
    market_row = feature_panel[feature_panel["feature_family"] == "market_cap_top100"]
    market_universe_available = (
        not market_row.empty and str(market_row["status"].iloc[0]) == "available"
    )
    market_universe_note = (
        "The local DefiLlama monthly point-in-time top200 universe is integrated for market-cap composition, concentration, clean-risk top100 construction, rank turnover, and cycle/ETF phase structure."
        if market_universe_available
        else "Point-in-time market-cap universe outputs remain skipped until `data_cache/defillama/crypto_universe_monthly_2020_2026.csv` is supplied and ingested."
    )
    market_table_lines = (
        "- `T40_crypto_universe_monthly.csv`"
        "\n- `T41_clean_risk_top100_monthly.csv`"
        "\n- `T42_market_structure_composition.csv`"
        "\n- `T43_rank_turnover.csv`"
        "\n- `T44_cycle_phase_market_structure.csv`"
        "\n- `T45_market_evolution_summary.md`"
        "\n- `T46_market_structure_monthly_features.csv`"
        "\n- `T47_market_structure_daily_context.csv`"
        "\n- `T48_market_structure_return_regimes.csv`"
        "\n- `T49_market_structure_composition_shift.csv`"
        "\n- `T50_market_structure_turnover_by_phase.csv`"
        "\n- `T51_market_structure_modeling_summary.md`"
        if market_universe_available
        else ""
    )
    daily_row = feature_panel[feature_panel["feature_family"] == "daily_constituent_rotation_lab"]
    daily_constituents_available = (
        not daily_row.empty and str(daily_row["status"].iloc[0]) == "available"
    )
    daily_table_lines = (
        "- `T52_constituent_daily_ohlcv.csv`"
        "\n- `T53_altseason_breadth.csv`"
        "\n- `T54_constituent_return_indexes.csv`"
        "\n- `T55_return_dispersion.csv`"
        "\n- `T56_rolling_beta_to_btc_eth.csv`"
        "\n- `T57_category_rotation_returns.csv`"
        "\n- `T58_event_response_top50.csv`"
        "\n- `T59_constituent_data_gap_report.csv`"
        "\n- `T60_altseason_rotation_summary.md`"
        if daily_constituents_available
        else ""
    )
    daily_note = (
        "The available DefiLlama daily top50 ex-stablecoin OHLCV sample is integrated for exploratory altseason breadth, dispersion, rolling beta, rotation, and event-response diagnostics. It is explicitly labeled as a current-constituent sample rather than a point-in-time top100 panel."
        if daily_constituents_available
        else "Daily constituent OHLCV remains skipped until a local top100/top200 constituent price/market-cap/volume file is supplied and ingested."
    )
    return [
        write_text(
            report_dir / "market_evolution_thesis.md",
            f"""# Market Evolution Thesis

The market-structure extension adds a public, reduced-form context layer around the factor lab: DeFi TVL, stablecoin supply, CEX/DEX activity, sentiment, BTC dominance/cycle markers, RWA/DAT growth, and optional Binance liquidity ranks.

The release is designed to work without paid/live data. It uses the frozen tracked dataset first and enriches from `data_cache/` only when optional DefiLlama, Binance, or CoinMarketCap cache is available. Generated feature rows across the public market-structure tables: {rows}.

{market_universe_note} When the frozen master daily panel is available, the build also creates a lagged/as-of monthly context layer and descriptive BTC/ETH return-regime diagnostics.

{daily_note}

Monthly snapshots support composition, concentration, rank turnover, and cycle-phase structure. A full point-in-time daily OHLCV/mcap constituent panel is still required for survivorship-free returns, breadth, volatility, beta, drawdowns, dispersion, and event-response analysis.

Interpretation stays descriptive. Binance ranks are exchange-liquidity ranks, stablecoin/TVL variables are liquidity proxies, and ETF-flow language remains contemporaneous association rather than causal identification.
""",
        ),
        write_text(
            report_dir / "market_structure_methodology.md",
            """# Market-Structure Methodology

Raw optional payloads are stored in gitignored `data_cache/{defillama,binance,coinmarketcap}/raw`. Normalized release-ready CSVs are written under `Data/MarketStructure/`.

Point-in-time market-cap top100 universes require point-in-time market-cap source data. The pipeline refuses to backfill a historical top100 from a current list. Binance top100 outputs are labeled as exchange-liquidity ranks based on rolling quote volume.

When `data_cache/defillama/crypto_universe_monthly_2020_2026.csv` is present, `scripts/ingest_defillama_monthly_universe.py` validates and normalizes it into `Data/MarketStructure/DefiLlama/`. The build then constructs full, ex-stable, and clean-risk top100 universes using internal classifications rather than upstream risk labels.

CMC Fear & Greed uses the official `v3/fear-and-greed/historical` client when `CMC_API_KEY` is available. Once cached, the normalized CMC history can be rebuilt without the key. If no CMC cache exists, the tracked AlternativeMe series remains the baseline sentiment source.

When `data_cache/defillama/top50_current_ex_stable_daily_ohlcv_2020_2026.csv` is present, `scripts/ingest_defillama_daily_constituents.py` validates and normalizes it into `Data/MarketStructure/DefiLlama/`. The resulting daily lab is explicitly labeled as a current top50 ex-stablecoin sample, not a point-in-time top100/top200 universe.
""",
        ),
        write_text(
            report_dir / "market_structure_data_inventory.md",
            f"""# Market-Structure Data Inventory

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
- `T38_fear_greed_blended_daily.csv`
- `T39_fear_greed_source_overlap_summary.csv`
{market_table_lines if market_table_lines else ""}
{daily_table_lines if daily_table_lines else ""}

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
- CMC Fear & Greed live refresh requires `CMC_API_KEY`; cached history is included when present.
- Monthly market-cap snapshots support structure/composition diagnostics only; a full point-in-time daily OHLCV/mcap panel is required for survivorship-free altseason performance, breadth, volatility, beta, drawdown, dispersion, and event-return analysis.
- The current daily constituent lab uses a DefiLlama current top50 ex-stablecoin sample and should be interpreted as exploratory.
""",
        ),
        write_text(
            report_dir / "market_structure_fetch_diagnostics.md",
            f"""# Market-Structure Fetch Diagnostics

Endpoint rows audited: {len(endpoint_rows)}

Optional key-gated endpoints available now: {key_available}/{len(key_required)}

Cached CMC Fear & Greed rows available: {cmc_rows}

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


def _phase_label(value: object) -> str:
    return str(value).replace("_", "\n")


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
        ax.plot(
            st["date"],
            st["stablecoins_mcap_usd"],
            label="Stablecoin mcap",
            color=COLORS["stablecoin"],
        )
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
    if (
        "rolling_quote_volume_usd" in ranks
        and pd.to_numeric(ranks["rolling_quote_volume_usd"], errors="coerce").notna().any()
    ):
        latest_month = ranks["month"].dropna().iloc[-1]
        latest = ranks[ranks["month"] == latest_month].head(20)
        ax.barh(
            latest["symbol"],
            pd.to_numeric(latest["rolling_quote_volume_usd"], errors="coerce"),
            color=COLORS["btc"],
        )
    else:
        ax.text(
            0.5,
            0.5,
            "No Binance kline cache\nliquidity ranks skipped",
            ha="center",
            va="center",
            color=COLORS["muted"],
            transform=ax.transAxes,
        )
        ax.set_xticks([])
        ax.set_yticks([])
    ax.set_title("Binance Exchange-Liquidity Universe", color=COLORS["text"], fontweight="bold")
    _style_axis(ax)
    written.append(save_fig(fig, figures / "F34_binance_liquidity_universe.png"))

    cycle = pd.read_csv(tables / "T34_btc_cycle_overlay.csv", parse_dates=["date"])
    fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    if not cycle.empty:
        ax.plot(cycle["date"], cycle["btc_dominance_close"], color=COLORS["btc"], linewidth=1.2)
        for date_str, label in [
            ("2020-05-11", "2020 halving"),
            ("2024-01-11", "BTC ETF"),
            ("2024-04-20", "2024 halving"),
            ("2024-07-23", "ETH ETF"),
        ]:
            ax.axvline(pd.Timestamp(date_str), color=COLORS["neutral"], linewidth=0.8, alpha=0.5)
            ax.text(
                pd.Timestamp(date_str),
                ax.get_ylim()[1],
                label,
                rotation=90,
                va="top",
                fontsize=7,
                color=COLORS["muted"],
            )
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
    ax.text(
        0.02,
        0.75,
        "Market-Cap Top100",
        color=COLORS["text"],
        fontsize=18,
        fontweight="bold",
        transform=ax.transAxes,
    )
    ax.text(
        0.02,
        0.55,
        str(gap.loc[0, "status"]).upper(),
        color=COLORS["risk"],
        fontsize=28,
        fontweight="bold",
        transform=ax.transAxes,
    )
    ax.text(
        0.02,
        0.36,
        str(gap.loc[0, "reason"]),
        color=COLORS["muted"],
        fontsize=11,
        wrap=True,
        transform=ax.transAxes,
    )
    ax.text(
        0.02,
        0.18,
        "Guardrail: no current-top100 historical backfill.",
        color=COLORS["muted"],
        fontsize=10,
        transform=ax.transAxes,
    )
    written.append(save_fig(fig, figures / "F37_market_cap_top100_gap.png"))

    universe_path = tables / "T40_crypto_universe_monthly.csv"
    composition_path = tables / "T42_market_structure_composition.csv"
    turnover_path = tables / "T43_rank_turnover.csv"
    cycle_path = tables / "T44_cycle_phase_market_structure.csv"
    if (
        universe_path.exists()
        and composition_path.exists()
        and turnover_path.exists()
        and cycle_path.exists()
    ):
        universe = pd.read_csv(universe_path, parse_dates=["snapshot_date"])
        composition = pd.read_csv(composition_path, parse_dates=["snapshot_date"])
        turnover = pd.read_csv(turnover_path, parse_dates=["snapshot_date"])
        cycle_phase = pd.read_csv(cycle_path)
        palette = [
            COLORS["btc"],
            COLORS["eth"],
            COLORS["stablecoin"],
            COLORS["institutional"],
            COLORS["liquidity"],
            COLORS["gold"],
            COLORS["native"],
            COLORS["neutral"],
        ]

        full_comp = composition[composition["universe_type"] == "full_top100"]
        pivot = (
            full_comp.pivot_table(
                index="snapshot_date",
                columns="asset_class",
                values="market_cap_share",
                aggfunc="sum",
                fill_value=0,
            )
            .sort_index()
            .clip(lower=0)
        )
        fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
        if not pivot.empty:
            ax.stackplot(
                pivot.index,
                [pivot[col] for col in pivot.columns],
                labels=list(pivot.columns),
                colors=palette[: len(pivot.columns)],
                alpha=0.9,
            )
            ax.legend(frameon=False, fontsize=7, ncol=2, loc="upper left")
            ax.set_ylim(0, 1)
            ax.yaxis.set_major_formatter(PercentFormatter(1.0))
        ax.set_title(
            "Full Top100 Market-Structure Composition", color=COLORS["text"], fontweight="bold"
        )
        ax.set_ylabel("Market-cap share")
        _style_axis(ax)
        written.append(save_fig(fig, figures / "F38_market_structure_composition.png"))

        full_top100 = universe[universe["in_full_top100"]].copy()
        concentration_rows = []
        for snapshot_date, group in full_top100.groupby("snapshot_date"):
            total = group["market_cap_usd"].sum()
            top10_share = group.nsmallest(10, "rank_full_market")["market_cap_usd"].sum() / total
            btc_eth_share = (
                group[group["symbol"].isin(["BTC", "ETH"])]["market_cap_usd"].sum() / total
            )
            concentration_rows.append(
                {
                    "snapshot_date": snapshot_date,
                    "top10_share": top10_share,
                    "btc_eth_share": btc_eth_share,
                }
            )
        concentration = pd.DataFrame(concentration_rows)
        fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
        if not concentration.empty:
            ax.plot(
                concentration["snapshot_date"],
                concentration["top10_share"],
                label="Top10 share",
                color=COLORS["btc"],
            )
            ax.plot(
                concentration["snapshot_date"],
                concentration["btc_eth_share"],
                label="BTC+ETH share",
                color=COLORS["eth"],
            )
            ax.set_ylim(0, 1)
            ax.yaxis.set_major_formatter(PercentFormatter(1.0))
            ax.legend(frameon=False)
        ax.set_title("Top100 Concentration", color=COLORS["text"], fontweight="bold")
        ax.set_ylabel("Share of top100 market cap")
        _style_axis(ax)
        written.append(save_fig(fig, figures / "F39_top100_concentration.png"))

        clean_turnover = turnover[turnover["universe_type"] == "clean_risk_top100"]
        plot_turnover = clean_turnover[
            pd.to_numeric(clean_turnover["continuing_assets"], errors="coerce") > 0
        ]
        fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
        if not plot_turnover.empty:
            ax.plot(
                plot_turnover["snapshot_date"],
                plot_turnover["entrants"],
                label="Entrants",
                color=COLORS["positive"],
            )
            ax.plot(
                plot_turnover["snapshot_date"],
                plot_turnover["exits"],
                label="Exits",
                color=COLORS["negative"],
            )
            ax.legend(frameon=False)
        ax.set_title("Clean-Risk Top100 Rank Turnover", color=COLORS["text"], fontweight="bold")
        ax.set_ylabel("Assets")
        _style_axis(ax)
        written.append(save_fig(fig, figures / "F40_rank_turnover.png"))

        phase_full = cycle_phase[cycle_phase["universe_type"] == "full_top100"]
        phase_pivot = phase_full.pivot_table(
            index="cycle_phase",
            columns="asset_class",
            values="mean_market_cap_share",
            aggfunc="sum",
            fill_value=0,
        )
        fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
        if not phase_pivot.empty:
            phase_pivot.plot(
                kind="bar",
                stacked=True,
                ax=ax,
                color=palette[: len(phase_pivot.columns)],
                width=0.78,
            )
            ax.legend(frameon=False, fontsize=7, ncol=2)
            ax.set_ylim(0, 1)
            ax.yaxis.set_major_formatter(PercentFormatter(1.0))
            ax.set_xticklabels(
                [_phase_label(label.get_text()) for label in ax.get_xticklabels()],
                rotation=0,
                ha="center",
            )
        ax.set_title("Cycle-Phase Market Structure", color=COLORS["text"], fontweight="bold")
        ax.set_ylabel("Mean market-cap share")
        _style_axis(ax)
        written.append(save_fig(fig, figures / "F41_cycle_phase_market_structure.png"))

        fig, axes = plt.subplots(2, 2, figsize=(12, 8), facecolor=COLORS["bg"])
        axes = axes.flatten()
        if not pivot.empty:
            axes[0].stackplot(
                pivot.index,
                [pivot[col] for col in pivot.columns],
                labels=list(pivot.columns),
                colors=palette[: len(pivot.columns)],
                alpha=0.9,
            )
            axes[0].set_ylim(0, 1)
            axes[0].yaxis.set_major_formatter(PercentFormatter(1.0))
            axes[0].legend(frameon=False, fontsize=7, ncol=2, loc="upper left")
        axes[0].set_title("Composition", color=COLORS["text"], fontweight="bold")
        if not concentration.empty:
            axes[1].plot(
                concentration["snapshot_date"],
                concentration["top10_share"],
                color=COLORS["btc"],
                label="Top10",
            )
            axes[1].plot(
                concentration["snapshot_date"],
                concentration["btc_eth_share"],
                color=COLORS["eth"],
                label="BTC+ETH",
            )
            axes[1].set_ylim(0, 1)
            axes[1].yaxis.set_major_formatter(PercentFormatter(1.0))
            axes[1].legend(frameon=False, fontsize=7)
        axes[1].set_title("Concentration", color=COLORS["text"], fontweight="bold")
        if not plot_turnover.empty:
            axes[2].bar(
                plot_turnover["snapshot_date"],
                plot_turnover["entrants"],
                color=COLORS["positive"],
                label="Entrants",
            )
            axes[2].bar(
                plot_turnover["snapshot_date"],
                -plot_turnover["exits"],
                color=COLORS["negative"],
                label="Exits",
            )
            axes[2].legend(frameon=False, fontsize=7)
        axes[2].set_title("Turnover", color=COLORS["text"], fontweight="bold")
        if not phase_pivot.empty:
            phase_pivot.plot(
                kind="bar",
                stacked=True,
                ax=axes[3],
                color=palette[: len(phase_pivot.columns)],
                legend=False,
            )
            axes[3].set_ylim(0, 1)
            axes[3].yaxis.set_major_formatter(PercentFormatter(1.0))
            axes[3].set_xticklabels(
                [_phase_label(label.get_text()) for label in axes[3].get_xticklabels()],
                rotation=0,
                ha="center",
                fontsize=7,
            )
        axes[3].set_title("Cycle Phases", color=COLORS["text"], fontweight="bold")
        for axis in axes:
            _style_axis(axis)
        fig.suptitle("Market Evolution Dashboard", color=COLORS["text"], fontweight="bold")
        fig.tight_layout()
        written.append(save_fig(fig, figures / "F42_market_evolution_dashboard.png"))

        monthly_path = tables / "T46_market_structure_monthly_features.csv"
        regimes_path = tables / "T48_market_structure_return_regimes.csv"
        shift_path = tables / "T49_market_structure_composition_shift.csv"
        phase_turnover_path = tables / "T50_market_structure_turnover_by_phase.csv"
        if (
            monthly_path.exists()
            and regimes_path.exists()
            and shift_path.exists()
            and phase_turnover_path.exists()
        ):
            monthly = pd.read_csv(monthly_path, parse_dates=["snapshot_date"])
            regimes = pd.read_csv(regimes_path)
            shift = pd.read_csv(shift_path)
            phase_turnover = pd.read_csv(phase_turnover_path)

            share_cols = [
                ("btc_eth_share_full_top100", "BTC+ETH", COLORS["btc"]),
                ("top10_share_full_top100", "Top10", COLORS["eth"]),
                ("stable_like_share_full_top100", "Stable-like", COLORS["stablecoin"]),
                ("productized_share_full_top100", "Productized", COLORS["institutional"]),
                ("clean_risk_share_full_top100", "Clean risk", COLORS["liquidity"]),
            ]
            fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
            for col, label, color in share_cols:
                ax.plot(
                    monthly["snapshot_date"], monthly[col], label=label, color=color, linewidth=1.6
                )
            ax.set_ylim(0, 1)
            ax.yaxis.set_major_formatter(PercentFormatter(1.0))
            ax.set_title(
                "Monthly Market-Structure Feature Layer", color=COLORS["text"], fontweight="bold"
            )
            ax.set_ylabel("Share of full top100 market cap")
            ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper left")
            _style_axis(ax)
            written.append(save_fig(fig, figures / "F43_market_structure_monthly_features.png"))

            focused = regimes[
                (
                    regimes["feature"].isin(
                        ["top10_share_full_top100", "clean_risk_share_full_top100"]
                    )
                )
                & (regimes["asset"].isin(["BTC", "ETH"]))
            ].copy()
            fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
            if not focused.empty:
                focused["label"] = (
                    focused["feature"]
                    .str.replace("_share_full_top100", "", regex=False)
                    .str.replace("_", " ")
                    + " / "
                    + focused["bucket"].astype(str)
                    + " / "
                    + focused["asset"]
                )
                focused = focused.sort_values("mean_return_1d")
                colors = [
                    COLORS["eth"] if asset == "ETH" else COLORS["btc"] for asset in focused["asset"]
                ]
                ax.barh(focused["label"], focused["mean_return_1d"], color=colors)
                ax.axvline(0, color=COLORS["axis"], linewidth=0.8)
                ax.xaxis.set_major_formatter(PercentFormatter(1.0))
            ax.set_title(
                "BTC/ETH Returns by Lagged Monthly Context Bucket",
                color=COLORS["text"],
                fontweight="bold",
            )
            ax.set_xlabel("Mean daily return")
            _style_axis(ax)
            written.append(save_fig(fig, figures / "F44_market_structure_return_regimes.png"))

            fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
            if not shift.empty:
                plot_shift = shift.dropna(subset=["delta"]).copy()
                plot_shift["label"] = (
                    plot_shift["metric"]
                    .str.replace("_full_top100", "", regex=False)
                    .str.replace("_", " ")
                )
                plot_shift = plot_shift.sort_values("delta")
                colors = [
                    COLORS["liquidity"] if value >= 0 else COLORS["gold"]
                    for value in plot_shift["delta"]
                ]
                ax.barh(plot_shift["label"], plot_shift["delta"], color=colors)
                ax.axvline(0, color=COLORS["axis"], linewidth=0.8)
                ax.xaxis.set_major_formatter(PercentFormatter(1.0))
            ax.set_title(
                "ETF-Era Market-Structure Composition Shift",
                color=COLORS["text"],
                fontweight="bold",
            )
            ax.set_xlabel("Post BTC ETF mean minus pre BTC ETF mean")
            _style_axis(ax)
            written.append(save_fig(fig, figures / "F45_market_structure_composition_shift.png"))

            fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
            if not phase_turnover.empty:
                phase_plot = phase_turnover.copy()
                x = range(len(phase_plot))
                ax.bar(
                    [idx - 0.18 for idx in x],
                    phase_plot["mean_clean_risk_entrants"],
                    width=0.36,
                    label="Entrants",
                    color=COLORS["positive"],
                )
                ax.bar(
                    [idx + 0.18 for idx in x],
                    phase_plot["mean_clean_risk_exits"],
                    width=0.36,
                    label="Exits",
                    color=COLORS["negative"],
                )
                ax.set_xticks(list(x))
                ax.set_xticklabels(
                    [_phase_label(value) for value in phase_plot["cycle_phase"]],
                    rotation=0,
                    fontsize=7,
                )
                ax.legend(frameon=False, fontsize=8)
            ax.set_title(
                "Clean-Risk Top100 Turnover by Cycle/ETF Phase",
                color=COLORS["text"],
                fontweight="bold",
            )
            ax.set_ylabel("Mean assets per snapshot")
            _style_axis(ax)
            written.append(save_fig(fig, figures / "F46_market_structure_turnover_by_phase.png"))

            fig, axes = plt.subplots(2, 2, figsize=(12, 8), facecolor=COLORS["bg"])
            axes = axes.flatten()
            for col, label, color in share_cols[:4]:
                axes[0].plot(
                    monthly["snapshot_date"], monthly[col], label=label, color=color, linewidth=1.35
                )
            axes[0].set_ylim(0, 1)
            axes[0].yaxis.set_major_formatter(PercentFormatter(1.0))
            axes[0].legend(frameon=False, fontsize=7, ncol=2)
            axes[0].set_title("Monthly context features", color=COLORS["text"], fontweight="bold")
            if not focused.empty:
                short = focused[focused["feature"] == "top10_share_full_top100"].sort_values(
                    "mean_return_1d"
                )
                short_colors = [
                    COLORS["eth"] if asset == "ETH" else COLORS["btc"] for asset in short["asset"]
                ]
                axes[1].barh(
                    short["bucket"] + " / " + short["asset"],
                    short["mean_return_1d"],
                    color=short_colors,
                )
                axes[1].axvline(0, color=COLORS["axis"], linewidth=0.8)
                axes[1].xaxis.set_major_formatter(PercentFormatter(1.0))
            axes[1].set_title("Return buckets", color=COLORS["text"], fontweight="bold")
            if not shift.empty:
                plot_shift = shift.dropna(subset=["delta"]).sort_values("delta")
                shift_colors = [
                    COLORS["liquidity"] if value >= 0 else COLORS["gold"]
                    for value in plot_shift["delta"]
                ]
                axes[2].barh(
                    plot_shift["metric"]
                    .str.replace("_full_top100", "", regex=False)
                    .str.replace("_", " "),
                    plot_shift["delta"],
                    color=shift_colors,
                )
                axes[2].axvline(0, color=COLORS["axis"], linewidth=0.8)
                axes[2].xaxis.set_major_formatter(PercentFormatter(1.0))
            axes[2].set_title("ETF-era deltas", color=COLORS["text"], fontweight="bold")
            if not phase_turnover.empty:
                axes[3].barh(
                    phase_turnover["cycle_phase"].map(_phase_label),
                    phase_turnover["mean_clean_risk_entrants"],
                    color=COLORS["positive"],
                )
            axes[3].set_title("Clean-risk entrants", color=COLORS["text"], fontweight="bold")
            for axis in axes:
                _style_axis(axis)
            fig.suptitle(
                "Market-Structure Modeling Dashboard", color=COLORS["text"], fontweight="bold"
            )
            fig.tight_layout()
            written.append(save_fig(fig, figures / "F47_market_structure_modeling_dashboard.png"))

    breadth_path = tables / "T53_altseason_breadth.csv"
    indexes_path = tables / "T54_constituent_return_indexes.csv"
    dispersion_path = tables / "T55_return_dispersion.csv"
    beta_path = tables / "T56_rolling_beta_to_btc_eth.csv"
    events_path = tables / "T58_event_response_top50.csv"
    if (
        breadth_path.exists()
        and indexes_path.exists()
        and dispersion_path.exists()
        and beta_path.exists()
        and events_path.exists()
    ):
        breadth = pd.read_csv(breadth_path, parse_dates=["date"])
        indexes = pd.read_csv(indexes_path, parse_dates=["date"])
        dispersion = pd.read_csv(dispersion_path, parse_dates=["date"])
        beta = pd.read_csv(beta_path, parse_dates=["date"])
        events = pd.read_csv(events_path)

        fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
        if not breadth.empty:
            ax.plot(
                breadth["date"],
                breadth["share_risk_beating_btc_90d"],
                color=COLORS["liquidity"],
                linewidth=1.6,
                label="Risk sample beating BTC",
            )
            ax.axhline(0.70, color=COLORS["positive"], linestyle="--", linewidth=1, alpha=0.7)
            ax.axhline(0.30, color=COLORS["gold"], linestyle="--", linewidth=1, alpha=0.7)
            ax.set_ylim(0, 1)
            ax.yaxis.set_major_formatter(PercentFormatter(1.0))
            ax.legend(frameon=False, fontsize=8)
        ax.set_title(
            "Altseason Breadth: Current Top50 Sample", color=COLORS["text"], fontweight="bold"
        )
        ax.set_ylabel("Share beating BTC over 90 days")
        _style_axis(ax)
        written.append(save_fig(fig, figures / "F48_altseason_breadth.png"))

        fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
        if not indexes.empty:
            for universe, label, color in [
                ("btc", "BTC", COLORS["btc"]),
                ("eth", "ETH", COLORS["eth"]),
                ("top50_ex_btc_eth", "Top50 ex BTC/ETH", COLORS["liquidity"]),
                ("top10_ex_btc_eth", "Top10 ex BTC/ETH", COLORS["institutional"]),
            ]:
                series = indexes[indexes["universe"] == universe]
                if not series.empty:
                    ax.plot(
                        series["date"],
                        series["cumulative_index"],
                        label=label,
                        color=color,
                        linewidth=1.35,
                    )
            ax.set_yscale("log")
            ax.legend(frameon=False, fontsize=8)
        ax.set_title("Constituent Rotation Indexes", color=COLORS["text"], fontweight="bold")
        ax.set_ylabel("Cumulative index, log scale")
        _style_axis(ax)
        written.append(save_fig(fig, figures / "F49_constituent_return_indexes.png"))

        fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
        if not dispersion.empty:
            ax.fill_between(
                dispersion["date"],
                dispersion["p10_return_1d"],
                dispersion["p90_return_1d"],
                color=COLORS["eth"],
                alpha=0.18,
                label="P10-P90 daily return range",
            )
            ax.plot(
                dispersion["date"],
                dispersion["median_return_1d"],
                color=COLORS["btc"],
                linewidth=1.2,
                label="Median",
            )
            ax.axhline(0, color=COLORS["axis"], linewidth=0.8)
            ax.yaxis.set_major_formatter(PercentFormatter(1.0))
            ax.legend(frameon=False, fontsize=8)
        ax.set_title("Daily Return Dispersion", color=COLORS["text"], fontweight="bold")
        ax.set_ylabel("Clean-risk ex BTC/ETH daily returns")
        _style_axis(ax)
        written.append(save_fig(fig, figures / "F50_return_dispersion.png"))

        fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
        if not beta.empty:
            plot_beta = beta[
                (beta["window_days"] == 180)
                & (beta["benchmark"] == "btc")
                & (
                    beta["universe"].isin(
                        ["top50_ex_btc_eth", "top10_ex_btc_eth", "clean_risk_ex_btc_eth"]
                    )
                )
            ]
            for universe, label, color in [
                ("top50_ex_btc_eth", "Top50 ex BTC/ETH", COLORS["liquidity"]),
                ("top10_ex_btc_eth", "Top10 ex BTC/ETH", COLORS["institutional"]),
                ("clean_risk_ex_btc_eth", "Clean risk ex BTC/ETH", COLORS["native"]),
            ]:
                series = plot_beta[plot_beta["universe"] == universe]
                if not series.empty:
                    ax.plot(series["date"], series["beta"], label=label, color=color, linewidth=1.2)
            ax.axhline(1, color=COLORS["axis"], linewidth=0.8, linestyle="--")
            ax.legend(frameon=False, fontsize=8)
        ax.set_title("Rolling Beta to BTC", color=COLORS["text"], fontweight="bold")
        ax.set_ylabel("180-day beta")
        _style_axis(ax)
        written.append(save_fig(fig, figures / "F51_rolling_beta_to_btc.png"))

        fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
        if not events.empty:
            event_plot = events[
                (events["window_days"] == 10) & (events["universe"] == "top50_ex_btc_eth")
            ].copy()
            event_plot = event_plot.dropna(subset=["post_window_return"]).tail(10)
            if not event_plot.empty:
                label_map = {
                    "btc_spot_etf_launch": "BTC ETF launch",
                    "eth_spot_etf_launch": "ETH ETF launch",
                    "bitcoin_halving_2024": "2024 halving",
                    "dencun_upgrade": "Dencun",
                    "luna_collapse_2022": "Luna",
                    "ftx_collapse_2022": "FTX",
                    "svb_crisis_2023": "SVB",
                    "yen_carry_unwind_2024": "Yen carry",
                    "sec_generic_etp_listing_standards_2025": "SEC ETP rule",
                    "crypto_liquidation_tariff_shock_2025": "Oct. 2025 shock",
                }
                event_plot["label"] = (
                    event_plot["event_id"]
                    .map(label_map)
                    .fillna(event_plot["event_id"].astype(str).str.replace("_", " "))
                )
                colors = [
                    COLORS["liquidity"] if value >= 0 else COLORS["gold"]
                    for value in event_plot["post_window_return"]
                ]
                ax.barh(event_plot["label"], event_plot["post_window_return"], color=colors)
                ax.axvline(0, color=COLORS["axis"], linewidth=0.8)
                ax.xaxis.set_major_formatter(PercentFormatter(1.0))
        ax.set_title("Event Response: Top50 ex BTC/ETH", color=COLORS["text"], fontweight="bold")
        ax.set_xlabel("Post-event 10-day return")
        _style_axis(ax)
        written.append(save_fig(fig, figures / "F52_event_response_top50.png"))

        fig, axes = plt.subplots(2, 2, figsize=(12, 8), facecolor=COLORS["bg"])
        axes = axes.flatten()
        if not breadth.empty:
            axes[0].plot(
                breadth["date"],
                breadth["share_risk_beating_btc_90d"],
                color=COLORS["liquidity"],
                linewidth=1.3,
            )
            axes[0].axhline(0.70, color=COLORS["positive"], linestyle="--", linewidth=0.9)
            axes[0].set_ylim(0, 1)
            axes[0].yaxis.set_major_formatter(PercentFormatter(1.0))
        axes[0].set_title("90-day breadth", color=COLORS["text"], fontweight="bold")
        if not indexes.empty:
            for universe, label, color in [
                ("btc", "BTC", COLORS["btc"]),
                ("eth", "ETH", COLORS["eth"]),
                ("top50_ex_btc_eth", "Top50 ex BTC/ETH", COLORS["liquidity"]),
            ]:
                series = indexes[indexes["universe"] == universe]
                if not series.empty:
                    axes[1].plot(
                        series["date"],
                        series["cumulative_index"],
                        label=label,
                        color=color,
                        linewidth=1.1,
                    )
            axes[1].set_yscale("log")
            axes[1].legend(frameon=False, fontsize=7)
        axes[1].set_title("Rotation indexes", color=COLORS["text"], fontweight="bold")
        if not dispersion.empty:
            axes[2].plot(
                dispersion["date"],
                dispersion["dispersion_1d_p90_minus_p10"],
                color=COLORS["eth"],
                linewidth=1.1,
            )
            axes[2].yaxis.set_major_formatter(PercentFormatter(1.0))
        axes[2].set_title("Daily dispersion", color=COLORS["text"], fontweight="bold")
        if not beta.empty:
            series = beta[
                (beta["window_days"] == 180)
                & (beta["benchmark"] == "btc")
                & (beta["universe"] == "top50_ex_btc_eth")
            ]
            axes[3].plot(series["date"], series["beta"], color=COLORS["btc"], linewidth=1.1)
            axes[3].axhline(1, color=COLORS["axis"], linestyle="--", linewidth=0.8)
        axes[3].set_title("Top50 beta to BTC", color=COLORS["text"], fontweight="bold")
        for axis in axes:
            _style_axis(axis)
        fig.suptitle("Altseason and Rotation Dashboard", color=COLORS["text"], fontweight="bold")
        fig.tight_layout()
        written.append(save_fig(fig, figures / "F53_rotation_dashboard.png"))

    return written


def update_outputs_readme(project_root: Path) -> Path:
    """Add the market-structure extension map to outputs/README.md."""

    path = project_root / "outputs" / "README.md"
    text = path.read_text(encoding="utf-8") if path.exists() else "# Canonical Outputs\n"
    marker = "\n## Market-Structure Extension\n"
    text = text.split(marker, 1)[0].rstrip()
    figures = project_root / "outputs" / "figures"
    tables = project_root / "outputs" / "tables"
    market_figure_lines = (
        "- `figures/F38_market_structure_composition.png`"
        "\n- `figures/F39_top100_concentration.png`"
        "\n- `figures/F40_rank_turnover.png`"
        "\n- `figures/F41_cycle_phase_market_structure.png`"
        "\n- `figures/F42_market_evolution_dashboard.png`"
        "\n- `figures/F43_market_structure_monthly_features.png`"
        "\n- `figures/F44_market_structure_return_regimes.png`"
        "\n- `figures/F45_market_structure_composition_shift.png`"
        "\n- `figures/F46_market_structure_turnover_by_phase.png`"
        "\n- `figures/F47_market_structure_modeling_dashboard.png`"
        if (figures / "F38_market_structure_composition.png").exists()
        else ""
    )
    daily_figure_lines = (
        "- `figures/F48_altseason_breadth.png`"
        "\n- `figures/F49_constituent_return_indexes.png`"
        "\n- `figures/F50_return_dispersion.png`"
        "\n- `figures/F51_rolling_beta_to_btc.png`"
        "\n- `figures/F52_event_response_top50.png`"
        "\n- `figures/F53_rotation_dashboard.png`"
        if (figures / "F48_altseason_breadth.png").exists()
        else ""
    )
    market_table_lines = (
        "- `tables/T40_crypto_universe_monthly.csv`"
        "\n- `tables/T41_clean_risk_top100_monthly.csv`"
        "\n- `tables/T42_market_structure_composition.csv`"
        "\n- `tables/T43_rank_turnover.csv`"
        "\n- `tables/T44_cycle_phase_market_structure.csv`"
        "\n- `tables/T45_market_evolution_summary.md`"
        "\n- `tables/T46_market_structure_monthly_features.csv`"
        "\n- `tables/T47_market_structure_daily_context.csv`"
        "\n- `tables/T48_market_structure_return_regimes.csv`"
        "\n- `tables/T49_market_structure_composition_shift.csv`"
        "\n- `tables/T50_market_structure_turnover_by_phase.csv`"
        "\n- `tables/T51_market_structure_modeling_summary.md`"
        if (tables / "T40_crypto_universe_monthly.csv").exists()
        else ""
    )
    daily_table_lines = (
        "- `tables/T52_constituent_daily_ohlcv.csv`"
        "\n- `tables/T53_altseason_breadth.csv`"
        "\n- `tables/T54_constituent_return_indexes.csv`"
        "\n- `tables/T55_return_dispersion.csv`"
        "\n- `tables/T56_rolling_beta_to_btc_eth.csv`"
        "\n- `tables/T57_category_rotation_returns.csv`"
        "\n- `tables/T58_event_response_top50.csv`"
        "\n- `tables/T59_constituent_data_gap_report.csv`"
        "\n- `tables/T60_altseason_rotation_summary.md`"
        if (tables / "T52_constituent_daily_ohlcv.csv").exists()
        else ""
    )
    section = f"""{marker}
The additive market-structure layer integrates tracked DefiLlama/AlternativeMe/TradingView context with optional DefiLlama, Binance, and CoinMarketCap cache. It does not require API keys for the public build.

Reports:

- `report/altseason_rotation_lab.md`
- `report/market_evolution_thesis.md`
- `report/market_structure_modeling_thesis.md`
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
{market_figure_lines if market_figure_lines else ""}
{daily_figure_lines if daily_figure_lines else ""}

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
- `tables/T38_fear_greed_blended_daily.csv`
- `tables/T39_fear_greed_source_overlap_summary.csv`
{market_table_lines if market_table_lines else ""}
{daily_table_lines if daily_table_lines else ""}

Guardrails:

- Binance top100 is exchange-liquidity based, not historical market-cap rank.
- CMC live fetch requires `CMC_API_KEY`; cached CMC history is included when present.
- Monthly universe snapshots support composition and turnover analysis, not daily performance or event-return claims.
- Daily constituent diagnostics are a current top50 ex-stablecoin sample, not a point-in-time top100 panel.
- Raw source responses stay in gitignored `data_cache/`.
"""
    return write_text(path, text + "\n" + section)


def patch_outputs_manifest(
    project_root: Path, output_files: list[Path], skipped: list[str]
) -> Path:
    manifest_path = project_root / "outputs" / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {}
    generated_at = datetime.now(UTC)
    manifest["market_structure"] = {
        "generated_at_utc": generated_at.isoformat(),
        "source_table_bundle_date": generated_at.date().isoformat(),
        "figure_bundle_start": "F30",
        "table_bundle_start": "T28",
        "commands": [
            "uv run python scripts/audit_market_structure_endpoints.py --dry-run",
            "uv run python scripts/fetch_market_structure_raw.py --dry-run",
            "uv run python scripts/fetch_market_structure_raw.py --cache-only",
            "uv run python scripts/ingest_defillama_monthly_universe.py",
            "uv run python scripts/ingest_defillama_daily_constituents.py",
            "uv run python scripts/normalize_market_structure_cache.py --cache-only",
            "uv run python scripts/build_market_structure_outputs.py",
        ],
        "outputs": [rel(path, project_root) for path in output_files if path.exists()],
        "skipped": skipped,
        "guardrails": [
            "Binance top100 is exchange-liquidity based, not market-cap based.",
            "CMC live fetch requires CMC_API_KEY; cached CMC history is included when present.",
            "Monthly point-in-time universes support composition and turnover, not daily return-performance claims.",
            "Daily constituent diagnostics use a current top50 ex-stablecoin sample and are labeled as exploratory.",
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
    roots = [
        project_root / "README.md",
        project_root / "outputs",
        project_root / "docs",
        project_root / "Data" / "MarketStructure",
    ]
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
        elif root.exists():
            files.extend(
                path
                for path in root.rglob("*")
                if path.suffix.lower() in {".md", ".json", ".csv", ".txt"}
            )
    files = [path for path in files if path.name != "market_structure_public_surface_check.md"]
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for rule, terms in patterns.items():
            for term in terms:
                if term in text:
                    allowed = path.name == ".env.example" or "guardrail" in text.lower()
                    rows.append(
                        {
                            "file": rel(path, project_root),
                            "rule": rule,
                            "term": term,
                            "status": "allowed_context" if allowed else "violation",
                        }
                    )
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
    for term in [
        "portfolio_v2",
        "v2.1",
        "v2.2",
        "v2.0",
        "career",
        "recruiter",
        "LinkedIn",
        "interview",
    ]:
        if term.lower() in readme.lower():
            rows.append(
                {
                    "file": "README.md",
                    "rule": "banned_readme_term",
                    "term": term,
                    "status": "violation",
                }
            )
    if "results at a glance" not in readme.lower():
        rows.append(
            {
                "file": "README.md",
                "rule": "required_section",
                "term": "Results at a Glance",
                "status": "violation",
            }
        )
    if "t11_results_at_a_glance.md" not in readme.lower():
        rows.append(
            {
                "file": "README.md",
                "rule": "required_table_link",
                "term": "T11_results_at_a_glance.md",
                "status": "violation",
            }
        )
    old_figs = [
        "F02_btc_model_sensitivity.png",
        "F01_data_inventory.png",
        "F02_btc_model_sensitivity",
        "F01_data_inventory",
    ]
    for raw_path in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme):
        if "archive/" in raw_path or "reports/portfolio_" in raw_path:
            rows.append(
                {
                    "file": "README.md",
                    "rule": "banned_image_path",
                    "term": raw_path,
                    "status": "violation",
                }
            )
        for old_fig in old_figs:
            if old_fig in raw_path:
                rows.append(
                    {
                        "file": "README.md",
                        "rule": "old_figure_name",
                        "term": old_fig,
                        "status": "violation",
                    }
                )
        if not (project_root / raw_path).exists():
            rows.append(
                {
                    "file": "README.md",
                    "rule": "missing_image_path",
                    "term": raw_path,
                    "status": "violation",
                }
            )
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
