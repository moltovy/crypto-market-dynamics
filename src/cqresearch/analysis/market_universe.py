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
    "tokenized_rwa",
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
    "token_id": ["token_id", "tokenid", "asset_id", "assetid", "defillama_id", "defillamaid"],
    "coingecko_id": ["coingecko_id", "coingeckoid", "cg_id", "cgid"],
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
    token_col = _optional_column(raw, "token_id")
    coingecko_col = _optional_column(raw, "coingecko_id")

    out = pd.DataFrame(
        {
            "snapshot_date": pd.to_datetime(raw[date_col], errors="coerce").dt.date,
            "symbol": raw[symbol_col].map(_symbol),
            "market_cap_usd": pd.to_numeric(raw[market_cap_col], errors="coerce"),
        }
    )
    out["asset_name"] = raw[name_col].astype(str).str.strip() if name_col else out["symbol"]
    out["price_usd"] = pd.to_numeric(raw[price_col], errors="coerce") if price_col else pd.NA
    out["token_id"] = raw[token_col].astype(str).str.strip() if token_col else ""
    out["coingecko_id"] = raw[coingecko_col].astype(str).str.strip() if coingecko_col else ""
    out["asset_key"] = out["coingecko_id"].where(out["coingecko_id"].ne(""), out["token_id"])
    out["asset_key"] = out["asset_key"].where(out["asset_key"].ne(""), out["symbol"])
    if rank_col:
        out["source_rank_full_market"] = pd.to_numeric(raw[rank_col], errors="coerce")
        if out["source_rank_full_market"].isna().any():
            raise UniverseValidationError("source rank column contains null or non-numeric values.")
    else:
        out["source_rank_full_market"] = pd.NA

    out = out.dropna(subset=["snapshot_date", "symbol", "market_cap_usd"])
    if (out["market_cap_usd"] <= 0).any():
        raise UniverseValidationError("market_cap_usd must be positive and non-null for every row.")
    if out.duplicated(["snapshot_date", "asset_key"]).any():
        raise UniverseValidationError("Monthly universe contains duplicate asset-key/date rows.")

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
        raise UniverseValidationError(
            f"Final snapshot must be the partial month date {partial_month_date}."
        )

    required_symbols = {"BTC", "ETH"}
    missing_symbol_snapshots = []
    for snapshot_date, group in out.groupby("snapshot_date"):
        symbols = set(group["symbol"])
        if not required_symbols.issubset(symbols):
            missing_symbol_snapshots.append(str(snapshot_date))
    if missing_symbol_snapshots:
        sample = ", ".join(missing_symbol_snapshots[:5])
        raise UniverseValidationError(f"BTC/ETH missing from snapshot(s): {sample}.")

    out = out.sort_values(
        ["snapshot_date", "market_cap_usd", "symbol"], ascending=[True, False, True]
    )
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
    out["source_rank_full_market"] = (
        out["source_rank_full_market"].fillna(out["rank_full_market"]).astype(int)
    )
    out["month"] = pd.to_datetime(out["snapshot_date"]).dt.to_period("M").astype(str)
    out["is_partial_month"] = out["snapshot_date"] == partial_date
    out["source"] = "defillama_monthly_universe"
    cols = [
        "source",
        "snapshot_date",
        "month",
        "asset_key",
        "token_id",
        "coingecko_id",
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
        return None, [
            f"{MONTHLY_UNIVERSE_CACHE.as_posix()} not found; market-cap universe skipped."
        ]
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
    latest["base_asset"] = latest["symbol"].str.extract(r"^([A-Z0-9]+?)(?:USDT|USDC|FDUSD|BUSD)$")[
        0
    ]
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


def classify_market_universe(
    universe: pd.DataFrame, overrides: dict[str, set[str]]
) -> pd.DataFrame:
    """Add internal classification and top100 membership flags to a monthly universe."""

    if universe.empty:
        return pd.DataFrame()
    out = universe.copy()
    if "asset_key" not in out:
        out["asset_key"] = out["symbol"]
    out["asset_class"] = out.apply(
        lambda row: classify_universe_asset(
            str(row["symbol"]), str(row.get("asset_name", "")), overrides
        ),
        axis=1,
    )
    out["in_full_top100"] = out["rank_full_market"] <= 100
    ex_stable = _rerank_monthly(
        out[~out["asset_class"].isin(STABLE_LIKE_CLASSES)], "rank_ex_stable"
    )
    clean_risk = _rerank_monthly(
        out[~out["asset_class"].isin(CLEAN_RISK_EXCLUDED_CLASSES)],
        "rank_clean_risk",
    )
    out = out.merge(
        ex_stable[["snapshot_date", "asset_key", "rank_ex_stable"]],
        on=["snapshot_date", "asset_key"],
        how="left",
    )
    out = out.merge(
        clean_risk[["snapshot_date", "asset_key", "rank_clean_risk"]],
        on=["snapshot_date", "asset_key"],
        how="left",
    )
    out["in_ex_stable_top100"] = out["rank_ex_stable"].le(100).fillna(False)
    out["in_clean_risk_top100"] = out["rank_clean_risk"].le(100).fillna(False)
    return out.sort_values(["snapshot_date", "rank_full_market"]).reset_index(drop=True)


def classify_universe_asset(symbol: str, asset_name: str, overrides: dict[str, set[str]]) -> str:
    """Classify a universe asset using symbol overrides plus productized-name hints."""

    symbol_token = symbol.upper().strip()
    name_token = asset_name.upper().strip()
    override_class = classify_asset(symbol_token, overrides)
    if override_class not in {"base_assets", "risk_assets"}:
        return override_class
    if "STAKED" in name_token or "RESTAKED" in name_token or symbol_token in {"RSETH", "WEETH"}:
        return "lst_restaking"
    if "USD" in name_token and ("YIELD" in name_token or "LIQUIDITY FUND" in name_token):
        return "stable_yield_tokens"
    if symbol_token.startswith("USD") or symbol_token.endswith("USD") or " USD" in name_token:
        return "stablecoins"
    return override_class


def _rerank_monthly(frame: pd.DataFrame, rank_col: str) -> pd.DataFrame:
    ranked = frame.sort_values(
        ["snapshot_date", "market_cap_usd", "symbol"], ascending=[True, False, True]
    ).copy()
    ranked[rank_col] = ranked.groupby("snapshot_date").cumcount() + 1
    return ranked


def clean_risk_top100(universe: pd.DataFrame) -> pd.DataFrame:
    """Return internally rebuilt clean-risk top100 by month."""

    if universe.empty or "rank_clean_risk" not in universe:
        return pd.DataFrame()
    cols = [
        "snapshot_date",
        "month",
        "asset_key",
        "token_id",
        "coingecko_id",
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
        _universe_slice(
            universe[universe["in_ex_stable_top100"]], "ex_stable_top100", "rank_ex_stable"
        ),
        _universe_slice(
            universe[universe["in_clean_risk_top100"]], "clean_risk_top100", "rank_clean_risk"
        ),
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
        .agg(asset_count=("asset_key", "nunique"), market_cap_usd=("market_cap_usd", "sum"))
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
        prev_assets: set[str] = set()
        prev_ranks: dict[str, float] = {}
        subset = universe[universe[flag_col]].copy()
        for snapshot_date, group in subset.groupby("snapshot_date", sort=True):
            current_assets = set(group["asset_key"])
            current_ranks = dict(zip(group["asset_key"], group[rank_col], strict=False))
            continuing = current_assets & prev_assets
            rank_changes = [
                abs(float(current_ranks[asset]) - float(prev_ranks[asset])) for asset in continuing
            ]
            rows.append(
                {
                    "snapshot_date": snapshot_date,
                    "month": group["month"].iloc[0],
                    "universe_type": universe_type,
                    "entrants": len(current_assets - prev_assets),
                    "exits": len(prev_assets - current_assets),
                    "continuing_assets": len(continuing),
                    "avg_abs_rank_change": sum(rank_changes) / len(rank_changes)
                    if rank_changes
                    else pd.NA,
                    "median_abs_rank_change": pd.Series(rank_changes).median()
                    if rank_changes
                    else pd.NA,
                }
            )
            prev_assets = current_assets
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
    latest = universe[
        (universe["snapshot_date"] == latest_date) & universe["in_full_top100"]
    ].copy()
    total = latest["market_cap_usd"].sum()
    btc_eth = latest[latest["symbol"].isin(["BTC", "ETH"])]["market_cap_usd"].sum() / total
    top10 = latest.nsmallest(10, "rank_full_market")["market_cap_usd"].sum() / total
    stable = latest[latest["asset_class"].isin(STABLE_LIKE_CLASSES)]["market_cap_usd"].sum() / total
    productized = (
        latest[latest["asset_class"].isin(CLEAN_RISK_EXCLUDED_CLASSES - STABLE_LIKE_CLASSES)][
            "market_cap_usd"
        ].sum()
        / total
    )
    risk = (
        latest[~latest["asset_class"].isin(CLEAN_RISK_EXCLUDED_CLASSES)]["market_cap_usd"].sum()
        / total
    )
    latest_turnover = turnover[
        (turnover["universe_type"] == "clean_risk_top100")
        & (turnover["snapshot_date"] == latest_date)
    ]
    entrants = int(latest_turnover["entrants"].iloc[0]) if not latest_turnover.empty else 0
    exits = int(latest_turnover["exits"].iloc[0]) if not latest_turnover.empty else 0
    phase_rows = (
        composition.assign(
            cycle_phase=pd.to_datetime(composition["snapshot_date"]).map(_cycle_phase)
        )
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


def market_structure_monthly_features(
    universe: pd.DataFrame,
    composition: pd.DataFrame,
    turnover: pd.DataFrame,
) -> pd.DataFrame:
    """Build one monthly feature row per point-in-time universe snapshot."""

    columns = [
        "snapshot_date",
        "month",
        "cycle_phase",
        "full_top100_total_market_cap_usd",
        "btc_eth_share_full_top100",
        "top10_share_full_top100",
        "stable_like_share_full_top100",
        "productized_share_full_top100",
        "clean_risk_share_full_top100",
        "clean_risk_asset_count_top100",
        "clean_risk_entrants",
        "clean_risk_exits",
        "clean_risk_avg_abs_rank_change",
        "is_partial_month",
        "method_note",
    ]
    if universe.empty:
        return pd.DataFrame(columns=columns)

    rows: list[dict[str, Any]] = []
    turnover_frame = turnover.copy()
    if not turnover_frame.empty:
        turnover_frame["snapshot_date"] = pd.to_datetime(turnover_frame["snapshot_date"]).dt.date
    for snapshot_date, group in universe[universe["in_full_top100"]].groupby(
        "snapshot_date", sort=True
    ):
        full = group.copy()
        total = float(pd.to_numeric(full["market_cap_usd"], errors="coerce").sum())
        if total <= 0:
            continue
        productized_classes = CLEAN_RISK_EXCLUDED_CLASSES - STABLE_LIKE_CLASSES
        turn = turnover_frame[
            (turnover_frame["snapshot_date"] == snapshot_date)
            & (turnover_frame["universe_type"] == "clean_risk_top100")
        ]
        rows.append(
            {
                "snapshot_date": snapshot_date,
                "month": str(full["month"].iloc[0]),
                "cycle_phase": _cycle_phase(pd.Timestamp(snapshot_date)),
                "full_top100_total_market_cap_usd": total,
                "btc_eth_share_full_top100": _share(
                    full, total, full["symbol"].isin(["BTC", "ETH"])
                ),
                "top10_share_full_top100": _share(full, total, full["rank_full_market"] <= 10),
                "stable_like_share_full_top100": _share(
                    full,
                    total,
                    full["asset_class"].isin(STABLE_LIKE_CLASSES),
                ),
                "productized_share_full_top100": _share(
                    full,
                    total,
                    full["asset_class"].isin(productized_classes),
                ),
                "clean_risk_share_full_top100": _share(
                    full,
                    total,
                    ~full["asset_class"].isin(CLEAN_RISK_EXCLUDED_CLASSES),
                ),
                "clean_risk_asset_count_top100": int(full["in_clean_risk_top100"].sum()),
                "clean_risk_entrants": int(turn["entrants"].iloc[0]) if not turn.empty else 0,
                "clean_risk_exits": int(turn["exits"].iloc[0]) if not turn.empty else 0,
                "clean_risk_avg_abs_rank_change": (
                    float(turn["avg_abs_rank_change"].iloc[0])
                    if not turn.empty and pd.notna(turn["avg_abs_rank_change"].iloc[0])
                    else pd.NA
                ),
                "is_partial_month": bool(full["is_partial_month"].iloc[0]),
                "method_note": "Lagged/as-of monthly market-cap context; descriptive, not causal.",
            }
        )
    return pd.DataFrame(rows, columns=columns)


def build_market_structure_daily_context(
    daily_panel: pd.DataFrame,
    monthly_features: pd.DataFrame,
) -> pd.DataFrame:
    """Join monthly market-structure features to daily BTC/ETH returns as-of date."""

    columns = [
        "date",
        "market_structure_snapshot_date",
        "btc_return_1d",
        "eth_return_1d",
        "btc_realized_vol_30d",
        "eth_realized_vol_30d",
        "cycle_phase",
        "btc_eth_share_full_top100",
        "top10_share_full_top100",
        "stable_like_share_full_top100",
        "productized_share_full_top100",
        "clean_risk_share_full_top100",
        "clean_risk_entrants",
        "clean_risk_exits",
        "clean_risk_avg_abs_rank_change",
        "method_note",
    ]
    if daily_panel.empty or monthly_features.empty:
        return pd.DataFrame(columns=columns)
    source_panel = daily_panel.copy()
    if "date" not in source_panel.columns:
        source_panel = source_panel.reset_index()
        if "index" in source_panel.columns and "date" not in source_panel.columns:
            source_panel = source_panel.rename(columns={"index": "date"})
    required = {"date", "btc_close", "eth_close"}
    if not required.issubset(source_panel.columns):
        return pd.DataFrame(columns=columns)

    daily = source_panel.copy()
    daily["date"] = (
        pd.to_datetime(daily["date"], errors="coerce").dt.normalize().astype("datetime64[ns]")
    )
    daily["btc_close"] = pd.to_numeric(daily["btc_close"], errors="coerce")
    daily["eth_close"] = pd.to_numeric(daily["eth_close"], errors="coerce")
    daily = daily.dropna(subset=["date"]).sort_values("date")
    daily["btc_return_1d"] = daily["btc_close"].pct_change()
    daily["eth_return_1d"] = daily["eth_close"].pct_change()
    daily["btc_realized_vol_30d"] = daily["btc_return_1d"].rolling(30, min_periods=20).std() * (
        365**0.5
    )
    daily["eth_realized_vol_30d"] = daily["eth_return_1d"].rolling(30, min_periods=20).std() * (
        365**0.5
    )

    monthly = monthly_features.copy()
    monthly["snapshot_date"] = (
        pd.to_datetime(monthly["snapshot_date"], errors="coerce")
        .dt.normalize()
        .astype("datetime64[ns]")
    )
    monthly = monthly.dropna(subset=["snapshot_date"]).sort_values("snapshot_date")
    monthly = monthly.rename(columns={"snapshot_date": "market_structure_snapshot_date"})
    joined = pd.merge_asof(
        daily[
            [
                "date",
                "btc_return_1d",
                "eth_return_1d",
                "btc_realized_vol_30d",
                "eth_realized_vol_30d",
            ]
        ],
        monthly,
        left_on="date",
        right_on="market_structure_snapshot_date",
        direction="backward",
    )
    joined["method_note"] = "Monthly universe features are joined as-of the latest prior snapshot."
    return joined[columns].dropna(subset=["market_structure_snapshot_date"]).reset_index(drop=True)


def market_structure_return_regimes(daily_context: pd.DataFrame) -> pd.DataFrame:
    """Summarize BTC/ETH returns and volatility across market-structure buckets."""

    columns = [
        "feature",
        "bucket",
        "asset",
        "observations",
        "mean_return_1d",
        "median_return_1d",
        "annualized_vol_from_daily_returns",
        "mean_realized_vol_30d",
        "positive_day_share",
        "method_note",
    ]
    if daily_context.empty:
        return pd.DataFrame(columns=columns)
    features = [
        "btc_eth_share_full_top100",
        "top10_share_full_top100",
        "stable_like_share_full_top100",
        "productized_share_full_top100",
        "clean_risk_share_full_top100",
        "clean_risk_entrants",
    ]
    rows: list[dict[str, Any]] = []
    for feature in features:
        if feature not in daily_context:
            continue
        frame = daily_context.dropna(subset=[feature]).copy()
        if frame[feature].nunique(dropna=True) < 3:
            continue
        frame["bucket"] = _tercile_bucket(frame[feature])
        frame = frame.dropna(subset=["bucket"])
        for bucket, bucket_frame in frame.groupby("bucket", sort=False):
            for asset in ["btc", "eth"]:
                ret_col = f"{asset}_return_1d"
                vol_col = f"{asset}_realized_vol_30d"
                returns = pd.to_numeric(bucket_frame[ret_col], errors="coerce").dropna()
                if returns.empty:
                    continue
                rows.append(
                    {
                        "feature": feature,
                        "bucket": str(bucket),
                        "asset": asset.upper(),
                        "observations": int(returns.shape[0]),
                        "mean_return_1d": float(returns.mean()),
                        "median_return_1d": float(returns.median()),
                        "annualized_vol_from_daily_returns": float(returns.std() * (365**0.5)),
                        "mean_realized_vol_30d": float(
                            pd.to_numeric(bucket_frame[vol_col], errors="coerce").mean()
                        ),
                        "positive_day_share": float((returns > 0).mean()),
                        "method_note": "Descriptive same-day return distribution by lagged monthly context bucket.",
                    }
                )
    return pd.DataFrame(rows, columns=columns)


def market_structure_composition_shift(monthly_features: pd.DataFrame) -> pd.DataFrame:
    """Compare market-structure metrics before and after the spot BTC ETF date."""

    columns = [
        "metric",
        "pre_btc_etf_mean",
        "btc_etf_era_mean",
        "delta",
        "snapshots_pre",
        "snapshots_post",
    ]
    if monthly_features.empty:
        return pd.DataFrame(columns=columns)
    frame = monthly_features.copy()
    frame["snapshot_date"] = pd.to_datetime(frame["snapshot_date"], errors="coerce")
    pre = frame[frame["snapshot_date"] < pd.Timestamp("2024-01-11")]
    post = frame[frame["snapshot_date"] >= pd.Timestamp("2024-01-11")]
    metrics = [
        "btc_eth_share_full_top100",
        "top10_share_full_top100",
        "stable_like_share_full_top100",
        "productized_share_full_top100",
        "clean_risk_share_full_top100",
    ]
    rows = []
    for metric in metrics:
        pre_mean = pd.to_numeric(pre[metric], errors="coerce").mean()
        post_mean = pd.to_numeric(post[metric], errors="coerce").mean()
        rows.append(
            {
                "metric": metric,
                "pre_btc_etf_mean": float(pre_mean) if pd.notna(pre_mean) else pd.NA,
                "btc_etf_era_mean": float(post_mean) if pd.notna(post_mean) else pd.NA,
                "delta": float(post_mean - pre_mean)
                if pd.notna(pre_mean) and pd.notna(post_mean)
                else pd.NA,
                "snapshots_pre": int(pre.shape[0]),
                "snapshots_post": int(post.shape[0]),
            }
        )
    return pd.DataFrame(rows, columns=columns)


def market_structure_turnover_by_phase(monthly_features: pd.DataFrame) -> pd.DataFrame:
    """Aggregate clean-risk turnover by coarse cycle/ETF phase."""

    columns = [
        "cycle_phase",
        "snapshots",
        "mean_clean_risk_entrants",
        "mean_clean_risk_exits",
        "mean_clean_risk_avg_abs_rank_change",
        "mean_top10_share_full_top100",
        "mean_clean_risk_share_full_top100",
    ]
    if monthly_features.empty:
        return pd.DataFrame(columns=columns)
    return (
        monthly_features.groupby("cycle_phase", as_index=False)
        .agg(
            snapshots=("snapshot_date", "nunique"),
            mean_clean_risk_entrants=("clean_risk_entrants", "mean"),
            mean_clean_risk_exits=("clean_risk_exits", "mean"),
            mean_clean_risk_avg_abs_rank_change=("clean_risk_avg_abs_rank_change", "mean"),
            mean_top10_share_full_top100=("top10_share_full_top100", "mean"),
            mean_clean_risk_share_full_top100=("clean_risk_share_full_top100", "mean"),
        )
        .sort_values("cycle_phase")
    )


def market_structure_modeling_summary(
    monthly_features: pd.DataFrame,
    daily_context: pd.DataFrame,
    return_regimes: pd.DataFrame,
    composition_shift: pd.DataFrame,
    turnover_by_phase: pd.DataFrame,
) -> str:
    """Build a concise Markdown summary of the monthly feature diagnostics."""

    if monthly_features.empty:
        return "# Market-Structure Modeling Summary\n\nMonthly market-structure features are unavailable.\n"
    latest = monthly_features.sort_values("snapshot_date").iloc[-1]
    best_bucket = ""
    if not return_regimes.empty:
        btc_rows = return_regimes[return_regimes["asset"] == "BTC"].copy()
        if not btc_rows.empty:
            row = btc_rows.sort_values("mean_return_1d", ascending=False).iloc[0]
            best_bucket = (
                f"\n- Highest descriptive BTC mean daily return bucket: `{row['feature']}` "
                f"/ `{row['bucket']}` ({float(row['mean_return_1d']):.3%}, n={int(row['observations'])})."
            )
    shift_line = ""
    if not composition_shift.empty:
        metric = "top10_share_full_top100"
        row = composition_shift[composition_shift["metric"] == metric]
        if not row.empty and pd.notna(row["delta"].iloc[0]):
            shift_line = f"\n- ETF-era average top10 concentration delta: {float(row['delta'].iloc[0]):+.1%}."
    phase_line = ""
    if not turnover_by_phase.empty:
        row = turnover_by_phase.sort_values("mean_clean_risk_entrants", ascending=False).iloc[0]
        phase_line = (
            f"\n- Highest mean clean-risk entry turnover phase: `{row['cycle_phase']}` "
            f"({float(row['mean_clean_risk_entrants']):.1f} entrants/snapshot)."
        )
    return f"""# Market-Structure Modeling Summary

The monthly point-in-time universe is now converted into a lagged/as-of context layer and joined to the frozen daily BTC/ETH panel. This is descriptive regime analysis, not a causal or predictive return model.

- Monthly feature snapshots: {len(monthly_features)}
- Daily panel rows with market-structure context: {len(daily_context)}
- Latest context snapshot: `{latest["snapshot_date"]}`
- Latest BTC+ETH share of full top100: {float(latest["btc_eth_share_full_top100"]):.1%}
- Latest top10 concentration: {float(latest["top10_share_full_top100"]):.1%}
- Latest clean-risk share: {float(latest["clean_risk_share_full_top100"]):.1%}{best_bucket}{shift_line}{phase_line}

Guardrail: monthly snapshots support composition, concentration, rank-turnover, and broad regime context. They do not identify daily altseason returns, intraday market microstructure, or causal ETF/stablecoin effects.
"""


def _share(frame: pd.DataFrame, total: float, mask: pd.Series) -> float:
    if total <= 0:
        return 0.0
    return float(pd.to_numeric(frame.loc[mask, "market_cap_usd"], errors="coerce").sum() / total)


def _tercile_bucket(series: pd.Series) -> pd.Series:
    labels = ["low", "mid", "high"]
    ranked = series.rank(method="first")
    try:
        return pd.qcut(ranked, q=3, labels=labels, duplicates="drop")
    except ValueError:
        return pd.Series(pd.NA, index=series.index)
