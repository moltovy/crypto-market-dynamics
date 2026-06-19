"""Universe builders for market-structure outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from cqresearch.analysis.asset_classification import classify_asset

MONTHLY_UNIVERSE_FILENAME = "crypto_universe_monthly_2020_2026.csv"
MONTHLY_UNIVERSE_CACHE = Path("data_cache") / "defillama" / MONTHLY_UNIVERSE_FILENAME
MONTHLY_UNIVERSE_CURATED = (
    Path("Data") / "MarketStructure" / "DefiLlama" / MONTHLY_UNIVERSE_FILENAME
)

DEFAULT_EXPECTED_SNAPSHOTS = 78
DEFAULT_ROWS_PER_SNAPSHOT = 200
DEFAULT_PARTIAL_MONTH_DATE = "2026-06-16"

STABLE_LIKE_CLASSES = {"stablecoins", "synthetic_stables", "stable_yield_tokens", "bridged_stables"}
CLEAN_RISK_EXCLUDED_CLASSES = STABLE_LIKE_CLASSES | {
    "wrapped_assets",
    "lst_restaking",
    "tokenized_commodities",
    "bridged_duplicates",
}

COLUMN_ALIASES = {
    "snapshot_date": [
        "snapshot_date",
        "snapshotdate",
        "date",
        "month",
        "timestamp",
        "datetime",
    ],
    "symbol": [
        "symbol",
        "ticker",
        "token_symbol",
        "tokensymbol",
        "asset_symbol",
        "assetsymbol",
        "coin_symbol",
        "coinsymbol",
    ],
    "asset_name": [
        "asset_name",
        "assetname",
        "name",
        "coin_name",
        "coinname",
        "token_name",
        "tokenname",
    ],
    "price_usd": [
        "price_usd",
        "priceusd",
        "price",
        "current_price",
        "currentprice",
    ],
    "market_cap_usd": [
        "market_cap_usd",
        "marketcapusd",
        "market_cap",
        "marketcap",
        "mcap",
        "market_capitalization",
        "marketcapitalization",
    ],
    "source_rank_full_market": [
        "source_rank_full_market",
        "rank_full_market",
        "rankfullmarket",
        "market_cap_rank",
        "marketcaprank",
        "mcap_rank",
        "mcaprank",
        "rank",
    ],
}


class UniverseValidationError(ValueError):
    """Raised when the point-in-time universe source is present but invalid."""


def _clean_col(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum() or ch == "_")


def _column_lookup(frame: pd.DataFrame) -> dict[str, str]:
    return {_clean_col(str(column)): str(column) for column in frame.columns}


def _required_column(frame: pd.DataFrame, canonical: str) -> str:
    lookup = _column_lookup(frame)
    for alias in COLUMN_ALIASES[canonical]:
        if alias in lookup:
            return lookup[alias]
    raise UniverseValidationError(f"Missing required column for {canonical}.")


def _optional_column(frame: pd.DataFrame, canonical: str) -> str | None:
    lookup = _column_lookup(frame)
    for alias in COLUMN_ALIASES[canonical]:
        if alias in lookup:
            return lookup[alias]
    return None


def _symbol(value: Any) -> str:
    return str(value).strip().upper().removeprefix("$")


def normalize_defillama_monthly_universe(
    raw: pd.DataFrame,
    *,
    expected_snapshots: int = DEFAULT_EXPECTED_SNAPSHOTS,
    rows_per_snapshot: int = DEFAULT_ROWS_PER_SNAPSHOT,
    partial_month_date: str = DEFAULT_PARTIAL_MONTH_DATE,
) -> pd.DataFrame:
    """Validate and normalize a DefiLlama monthly point-in-time universe CSV."""

    if raw.empty:
        raise UniverseValidationError("Monthly universe file is empty.")

    date_col = _required_column(raw, "snapshot_date")
    symbol_col = _required_column(raw, "symbol")
    market_cap_col = _required_column(raw, "market_cap_usd")
    name_col = _optional_column(raw, "asset_name")
    price_col = _optional_column(raw, "price_usd")
    rank_col = _optional_column(raw, "source_rank_full_market")

    out = pd.DataFrame(
        {
            "snapshot_date": pd.to_datetime(raw[date_col], errors="coerce").dt.date,
            "symbol": raw[symbol_col].map(_symbol),
            "market_cap_usd": pd.to_numeric(raw[market_cap_col], errors="coerce"),
        }
    )
    out["asset_name"] = raw[name_col].astype(str).str.strip() if name_col else out["symbol"]
    out["price_usd"] = pd.to_numeric(raw[price_col], errors="coerce") if price_col else pd.NA
    if rank_col:
        out["source_rank_full_market"] = pd.to_numeric(raw[rank_col], errors="coerce")
        if out["source_rank_full_market"].isna().any():
            raise UniverseValidationError("source rank column contains null or non-numeric values.")
    else:
        out["source_rank_full_market"] = pd.NA

    out = out.dropna(subset=["snapshot_date", "symbol", "market_cap_usd"])
    if (out["market_cap_usd"] <= 0).any():
        raise UniverseValidationError("market_cap_usd must be positive and non-null for every row.")
    if out.duplicated(["snapshot_date", "symbol"]).any():
        raise UniverseValidationError("Monthly universe contains duplicate symbol/date rows.")

    snapshots = sorted(out["snapshot_date"].unique())
    if len(snapshots) != expected_snapshots:
        raise UniverseValidationError(
            f"Expected {expected_snapshots} monthly snapshots, found {len(snapshots)}."
        )
    rows_by_snapshot = out.groupby("snapshot_date").size()
    bad_counts = rows_by_snapshot[rows_by_snapshot != rows_per_snapshot]
    if not bad_counts.empty:
        details = ", ".join(f"{date}:{count}" for date, count in bad_counts.head(5).items())
        raise UniverseValidationError(
            f"Expected {rows_per_snapshot} rows per snapshot; mismatches: {details}."
        )

    partial_date = pd.Timestamp(partial_month_date).date()
    if max(snapshots) != partial_date:
        raise UniverseValidationError(f"Final snapshot must be the partial month date {partial_month_date}.")

    required_symbols = {"BTC", "ETH"}
    missing_symbol_snapshots = []
    for snapshot_date, group in out.groupby("snapshot_date"):
        symbols = set(group["symbol"])
        if not required_symbols.issubset(symbols):
            missing_symbol_snapshots.append(str(snapshot_date))
    if missing_symbol_snapshots:
        sample = ", ".join(missing_symbol_snapshots[:5])
        raise UniverseValidationError(f"BTC/ETH missing from snapshot(s): {sample}.")

    out = out.sort_values(["snapshot_date", "market_cap_usd", "symbol"], ascending=[True, False, True])
    computed_rank = out.groupby("snapshot_date").cumcount() + 1
    if rank_col:
        source_rank = out["source_rank_full_market"].astype(int)
        mismatches = out.loc[source_rank != computed_rank, ["snapshot_date", "symbol"]]
        if not mismatches.empty:
            row = mismatches.iloc[0]
            raise UniverseValidationError(
                "rank_full_market does not match descending market_cap_usd; "
                f"first mismatch {row['snapshot_date']} {row['symbol']}."
            )
    out["rank_full_market"] = computed_rank
    out["source_rank_full_market"] = out["source_rank_full_market"].fillna(out["rank_full_market"]).astype(int)
    out["month"] = pd.to_datetime(out["snapshot_date"]).dt.to_period("M").astype(str)
    out["is_partial_month"] = out["snapshot_date"] == partial_date
    out["source"] = "defillama_monthly_universe"
    cols = [
        "source",
        "snapshot_date",
        "month",
        "symbol",
        "asset_name",
        "price_usd",
        "market_cap_usd",
        "source_rank_full_market",
        "rank_full_market",
        "is_partial_month",
    ]
    return out[cols].sort_values(["snapshot_date", "rank_full_market"]).reset_index(drop=True)


def ingest_defillama_monthly_universe(
    project_root: Path,
    *,
    expected_snapshots: int = DEFAULT_EXPECTED_SNAPSHOTS,
    rows_per_snapshot: int = DEFAULT_ROWS_PER_SNAPSHOT,
    partial_month_date: str = DEFAULT_PARTIAL_MONTH_DATE,
) -> tuple[Path | None, list[str]]:
    """Normalize the local monthly universe cache file if it exists."""

    source_path = project_root / MONTHLY_UNIVERSE_CACHE
    if not source_path.exists():
        return None, [f"{MONTHLY_UNIVERSE_CACHE.as_posix()} not found; market-cap universe skipped."]
    raw = pd.read_csv(source_path)
    normalized = normalize_defillama_monthly_universe(
        raw,
        expected_snapshots=expected_snapshots,
        rows_per_snapshot=rows_per_snapshot,
        partial_month_date=partial_month_date,
    )
    out_path = project_root / MONTHLY_UNIVERSE_CURATED
    out_path.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_csv(out_path, index=False)
    return out_path, []


def build_binance_liquidity_ranks(
    klines: pd.DataFrame,
    *,
    top_n: int = 100,
    window_days: int = 30,
) -> pd.DataFrame:
    """Build monthly Binance exchange-liquidity ranks from quote volume.

    This is intentionally not a market-cap universe. It ranks symbols by rolling
    quote-asset volume on Binance spot klines.
    """

    required = {"date", "symbol", "quote_asset_volume"}
    if klines.empty or not required.issubset(klines.columns):
        return pd.DataFrame(
            columns=[
                "month",
                "symbol",
                "base_asset",
                "quote_asset",
                "rolling_quote_volume_usd",
                "liquidity_rank",
                "universe_label",
            ]
        )
    frame = klines.copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame = frame.dropna(subset=["date", "symbol", "quote_asset_volume"])
    frame["quote_asset_volume"] = pd.to_numeric(frame["quote_asset_volume"], errors="coerce")
    frame = frame.sort_values(["symbol", "date"])
    frame["rolling_quote_volume_usd"] = frame.groupby("symbol")["quote_asset_volume"].transform(
        lambda series: series.rolling(window_days, min_periods=max(5, min(window_days, 10))).mean()
    )
    frame["month"] = frame["date"].dt.to_period("M").dt.to_timestamp("M").dt.date
    latest = frame.sort_values("date").groupby(["month", "symbol"], as_index=False).tail(1)
    latest["liquidity_rank"] = latest.groupby("month")["rolling_quote_volume_usd"].rank(
        ascending=False,
        method="first",
    )
    latest = latest[latest["liquidity_rank"] <= top_n].copy()
    latest["base_asset"] = latest["symbol"].str.extract(r"^([A-Z0-9]+?)(?:USDT|USDC|FDUSD|BUSD)$")[0]
    latest["quote_asset"] = latest["symbol"].str.extract(r"(USDT|USDC|FDUSD|BUSD)$")[0]
    latest["universe_label"] = f"Binance exchange-liquidity top{top_n}"
    cols = [
        "month",
        "symbol",
        "base_asset",
        "quote_asset",
        "rolling_quote_volume_usd",
        "liquidity_rank",
        "universe_label",
    ]
    return latest[cols].sort_values(["month", "liquidity_rank"])


def market_cap_top100_gap_report(has_point_in_time_source: bool) -> pd.DataFrame:
    """Document why market-cap top100 output is skipped or available."""

    if has_point_in_time_source:
        status = "available"
        reason = "Point-in-time monthly market-cap universe source is present."
    else:
        status = "skipped"
        reason = "No point-in-time top100 market-cap source is available; current top100 backfill is disallowed."
    return pd.DataFrame(
        [
            {
                "dataset": "market_cap_top100",
                "status": status,
                "reason": reason,
                "guardrail": "do_not_current_top100_backfill",
            }
        ]
    )


def classify_market_universe(universe: pd.DataFrame, overrides: dict[str, set[str]]) -> pd.DataFrame:
    """Add internal classification and top100 membership flags to a monthly universe."""

    if universe.empty:
        return pd.DataFrame()
    out = universe.copy()
    out["asset_class"] = out["symbol"].map(lambda value: classify_asset(str(value), overrides))
    out["in_full_top100"] = out["rank_full_market"] <= 100
    ex_stable = _rerank_monthly(out[~out["asset_class"].isin(STABLE_LIKE_CLASSES)], "rank_ex_stable")
    clean_risk = _rerank_monthly(
        out[~out["asset_class"].isin(CLEAN_RISK_EXCLUDED_CLASSES)],
        "rank_clean_risk",
    )
    out = out.merge(
        ex_stable[["snapshot_date", "symbol", "rank_ex_stable"]],
        on=["snapshot_date", "symbol"],
        how="left",
    )
    out = out.merge(
        clean_risk[["snapshot_date", "symbol", "rank_clean_risk"]],
        on=["snapshot_date", "symbol"],
        how="left",
    )
    out["in_ex_stable_top100"] = out["rank_ex_stable"].le(100).fillna(False)
    out["in_clean_risk_top100"] = out["rank_clean_risk"].le(100).fillna(False)
    return out.sort_values(["snapshot_date", "rank_full_market"]).reset_index(drop=True)


def _rerank_monthly(frame: pd.DataFrame, rank_col: str) -> pd.DataFrame:
    ranked = frame.sort_values(["snapshot_date", "market_cap_usd", "symbol"], ascending=[True, False, True]).copy()
    ranked[rank_col] = ranked.groupby("snapshot_date").cumcount() + 1
    return ranked


def clean_risk_top100(universe: pd.DataFrame) -> pd.DataFrame:
    """Return internally rebuilt clean-risk top100 by month."""

    if universe.empty or "rank_clean_risk" not in universe:
        return pd.DataFrame()
    cols = [
        "snapshot_date",
        "month",
        "symbol",
        "asset_name",
        "asset_class",
        "price_usd",
        "market_cap_usd",
        "rank_full_market",
        "rank_clean_risk",
        "is_partial_month",
    ]
    return (
        universe[universe["in_clean_risk_top100"]]
        .copy()
        .sort_values(["snapshot_date", "rank_clean_risk"])[cols]
    )


def market_structure_composition(universe: pd.DataFrame) -> pd.DataFrame:
    """Build class composition by monthly universe definition."""

    frames = [
        _universe_slice(universe[universe["in_full_top100"]], "full_top100", "rank_full_market"),
        _universe_slice(universe[universe["in_ex_stable_top100"]], "ex_stable_top100", "rank_ex_stable"),
        _universe_slice(universe[universe["in_clean_risk_top100"]], "clean_risk_top100", "rank_clean_risk"),
    ]
    combined = pd.concat([frame for frame in frames if not frame.empty], ignore_index=True)
    if combined.empty:
        return pd.DataFrame(
            columns=[
                "snapshot_date",
                "month",
                "universe_type",
                "asset_class",
                "asset_count",
                "market_cap_usd",
                "total_market_cap_usd",
                "market_cap_share",
            ]
        )
    grouped = (
        combined.groupby(["snapshot_date", "month", "universe_type", "asset_class"], as_index=False)
        .agg(asset_count=("symbol", "nunique"), market_cap_usd=("market_cap_usd", "sum"))
        .sort_values(["snapshot_date", "universe_type", "asset_class"])
    )
    totals = grouped.groupby(["snapshot_date", "universe_type"])["market_cap_usd"].transform("sum")
    grouped["total_market_cap_usd"] = totals
    grouped["market_cap_share"] = grouped["market_cap_usd"] / totals
    return grouped


def _universe_slice(frame: pd.DataFrame, universe_type: str, rank_col: str) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    out = frame.copy()
    out["universe_type"] = universe_type
    out["rank_universe"] = out[rank_col]
    return out


def rank_turnover(universe: pd.DataFrame) -> pd.DataFrame:
    """Compute month-to-month entries, exits, and rank movement."""

    specs = [
        ("full_top100", "in_full_top100", "rank_full_market"),
        ("ex_stable_top100", "in_ex_stable_top100", "rank_ex_stable"),
        ("clean_risk_top100", "in_clean_risk_top100", "rank_clean_risk"),
    ]
    rows: list[dict[str, Any]] = []
    for universe_type, flag_col, rank_col in specs:
        prev_symbols: set[str] = set()
        prev_ranks: dict[str, float] = {}
        subset = universe[universe[flag_col]].copy()
        for snapshot_date, group in subset.groupby("snapshot_date", sort=True):
            current_symbols = set(group["symbol"])
            current_ranks = dict(zip(group["symbol"], group[rank_col], strict=False))
            continuing = current_symbols & prev_symbols
            rank_changes = [
                abs(float(current_ranks[symbol]) - float(prev_ranks[symbol])) for symbol in continuing
            ]
            rows.append(
                {
                    "snapshot_date": snapshot_date,
                    "month": group["month"].iloc[0],
                    "universe_type": universe_type,
                    "entrants": len(current_symbols - prev_symbols),
                    "exits": len(prev_symbols - current_symbols),
                    "continuing_assets": len(continuing),
                    "avg_abs_rank_change": sum(rank_changes) / len(rank_changes) if rank_changes else pd.NA,
                    "median_abs_rank_change": pd.Series(rank_changes).median() if rank_changes else pd.NA,
                }
            )
            prev_symbols = current_symbols
            prev_ranks = current_ranks
    return pd.DataFrame(rows)


def cycle_phase_market_structure(composition: pd.DataFrame) -> pd.DataFrame:
    """Summarize class composition by coarse cycle/ETF phase."""

    if composition.empty:
        return pd.DataFrame(
            columns=[
                "cycle_phase",
                "universe_type",
                "asset_class",
                "snapshots",
                "mean_asset_count",
                "mean_market_cap_share",
            ]
        )
    frame = composition.copy()
    frame["cycle_phase"] = pd.to_datetime(frame["snapshot_date"]).map(_cycle_phase)
    return (
        frame.groupby(["cycle_phase", "universe_type", "asset_class"], as_index=False)
        .agg(
            snapshots=("snapshot_date", "nunique"),
            mean_asset_count=("asset_count", "mean"),
            mean_market_cap_share=("market_cap_share", "mean"),
        )
        .sort_values(["cycle_phase", "universe_type", "asset_class"])
    )


def _cycle_phase(date: pd.Timestamp) -> str:
    if date < pd.Timestamp("2020-05-11"):
        return "pre_2020_halving"
    if date < pd.Timestamp("2024-01-11"):
        return "post_2020_halving"
    if date < pd.Timestamp("2024-04-20"):
        return "btc_etf_era_pre_2024_halving"
    if date < pd.Timestamp("2024-07-23"):
        return "post_2024_halving_pre_eth_etf"
    return "eth_etf_era"


def market_evolution_summary(
    universe: pd.DataFrame,
    composition: pd.DataFrame,
    turnover: pd.DataFrame,
) -> str:
    """Build a compact Markdown summary for the monthly universe extension."""

    if universe.empty:
        return "# Market Evolution Summary\n\nPoint-in-time monthly universe data is unavailable.\n"
    latest_date = max(universe["snapshot_date"])
    latest = universe[(universe["snapshot_date"] == latest_date) & universe["in_full_top100"]].copy()
    total = latest["market_cap_usd"].sum()
    btc_eth = latest[latest["symbol"].isin(["BTC", "ETH"])]["market_cap_usd"].sum() / total
    top10 = latest.nsmallest(10, "rank_full_market")["market_cap_usd"].sum() / total
    stable = latest[latest["asset_class"].isin(STABLE_LIKE_CLASSES)]["market_cap_usd"].sum() / total
    productized = latest[latest["asset_class"].isin(CLEAN_RISK_EXCLUDED_CLASSES - STABLE_LIKE_CLASSES)][
        "market_cap_usd"
    ].sum() / total
    risk = latest[~latest["asset_class"].isin(CLEAN_RISK_EXCLUDED_CLASSES)]["market_cap_usd"].sum() / total
    latest_turnover = turnover[
        (turnover["universe_type"] == "clean_risk_top100") & (turnover["snapshot_date"] == latest_date)
    ]
    entrants = int(latest_turnover["entrants"].iloc[0]) if not latest_turnover.empty else 0
    exits = int(latest_turnover["exits"].iloc[0]) if not latest_turnover.empty else 0
    phase_rows = (
        composition.assign(cycle_phase=pd.to_datetime(composition["snapshot_date"]).map(_cycle_phase))
        if not composition.empty
        else pd.DataFrame()
    )
    phase_count = int(phase_rows["cycle_phase"].nunique()) if not phase_rows.empty else 0
    return f"""# Market Evolution Summary

The monthly point-in-time top200 universe is integrated for composition and structure analysis.

Latest snapshot: `{latest_date}`.

- BTC plus ETH share of full top100 market cap: {btc_eth:.1%}
- Top10 concentration in full top100: {top10:.1%}
- Stable/synthetic/stable-yield share of full top100: {stable:.1%}
- Wrapped/LST/tokenized commodity share of full top100: {productized:.1%}
- Clean-risk asset share of full top100: {risk:.1%}
- Latest clean-risk top100 turnover: {entrants} entrants and {exits} exits
- Cycle/ETF phases represented: {phase_count}

Monthly snapshots support composition, concentration, rank turnover, and cycle-phase structure.
Daily OHLCV is still required for returns, breadth, volatility, beta, drawdowns, dispersion, and event-response analysis.
"""
