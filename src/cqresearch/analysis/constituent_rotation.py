"""Daily constituent breadth and rotation diagnostics for market structure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from cqresearch.analysis.asset_classification import load_classification_overrides
from cqresearch.analysis.market_universe import (
    CLEAN_RISK_EXCLUDED_CLASSES,
    classify_universe_asset,
)

DAILY_CONSTITUENT_CACHE = (
    Path("data_cache") / "defillama" / "top50_current_ex_stable_daily_ohlcv_2020_2026.csv"
)
DAILY_CONSTITUENT_CURATED = (
    Path("Data")
    / "MarketStructure"
    / "DefiLlama"
    / "crypto_constituents_daily_ohlcv_top50_current_2020_2026.csv"
)

REQUIRED_COLUMNS = {
    "date",
    "rank",
    "symbol",
    "coingecko_id",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "mcap",
}

SAMPLE_NOTE = (
    "Current-top50 exploratory ex-stablecoin cohort from DefiLlama daily OHLCV. "
    "Use for current-cohort diagnostics only; it is survivorship-biased, not point-in-time, "
    "and not the primary altseason backtest."
)


class ConstituentValidationError(ValueError):
    """Raised when a present daily constituent source file is invalid."""


def read_defillama_daily_constituent_raw(path: Path) -> pd.DataFrame:
    """Read a DefiLlama daily constituent CSV with an optional metadata first row."""

    first_line = path.read_text(encoding="utf-8", errors="ignore").splitlines()[0]
    skiprows = 1 if first_line.startswith("##") else 0
    return pd.read_csv(path, skiprows=skiprows)


def normalize_defillama_daily_constituents(raw: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize a current-top50 exploratory daily OHLCV constituent file."""

    missing = REQUIRED_COLUMNS - set(raw.columns)
    if missing:
        raise ConstituentValidationError(f"Missing daily constituent column(s): {sorted(missing)}")
    out = raw.copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.date
    out["rank"] = pd.to_numeric(out["rank"], errors="coerce")
    out["symbol"] = out["symbol"].astype(str).str.strip().str.upper().str.removeprefix("$")
    out["coingecko_id"] = out["coingecko_id"].astype(str).str.strip()
    rename = {
        "open": "open_usd",
        "high": "high_usd",
        "low": "low_usd",
        "close": "close_usd",
        "volume": "volume_usd",
        "mcap": "market_cap_usd",
    }
    out = out.rename(columns=rename)
    numeric_cols = ["open_usd", "high_usd", "low_usd", "close_usd", "volume_usd", "market_cap_usd"]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.dropna(subset=["date", "rank", "symbol", "close_usd"])
    if out.empty:
        raise ConstituentValidationError(
            "Daily constituent file has no valid rows after normalization."
        )
    if (out["close_usd"] <= 0).any():
        raise ConstituentValidationError("close_usd must be positive.")
    out["market_cap_missing_or_nonpositive"] = out["market_cap_usd"].isna() | (
        out["market_cap_usd"] <= 0
    )
    out.loc[out["market_cap_missing_or_nonpositive"], "market_cap_usd"] = pd.NA
    if out.duplicated(["date", "symbol"]).any():
        raise ConstituentValidationError(
            "Daily constituent file contains duplicate date/symbol rows."
        )
    out["rank"] = out["rank"].astype(int)
    out["month"] = pd.to_datetime(out["date"]).dt.to_period("M").astype(str)
    out["source"] = "defillama_current_top50_exploratory_daily_ohlcv"
    out["universe_label"] = "current_top50_exploratory_current_cohort"
    out["method_note"] = SAMPLE_NOTE
    cols = [
        "source",
        "date",
        "month",
        "rank",
        "symbol",
        "coingecko_id",
        "open_usd",
        "high_usd",
        "low_usd",
        "close_usd",
        "volume_usd",
        "market_cap_usd",
        "market_cap_missing_or_nonpositive",
        "universe_label",
        "method_note",
    ]
    return out[cols].sort_values(["date", "rank", "symbol"]).reset_index(drop=True)


def ingest_defillama_daily_constituents(project_root: Path) -> tuple[Path | None, list[str]]:
    """Normalize the local daily constituent OHLCV cache file when present."""

    source_path = project_root / DAILY_CONSTITUENT_CACHE
    if not source_path.exists():
        return None, [
            f"{DAILY_CONSTITUENT_CACHE.as_posix()} not found; daily rotation lab skipped."
        ]
    raw = read_defillama_daily_constituent_raw(source_path)
    normalized = normalize_defillama_daily_constituents(raw)
    out_path = project_root / DAILY_CONSTITUENT_CURATED
    out_path.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_csv(out_path, index=False)
    return out_path, []


def load_daily_constituents(project_root: Path) -> pd.DataFrame:
    """Load normalized daily constituents and attach internal asset classes."""

    path = project_root / DAILY_CONSTITUENT_CURATED
    if not path.exists():
        return pd.DataFrame()
    out = pd.read_csv(path, parse_dates=["date"])
    overrides = load_classification_overrides(
        project_root / "config" / "asset_classification_overrides.yml"
    )
    out["asset_class"] = out.apply(
        lambda row: classify_universe_asset(str(row["symbol"]), str(row["symbol"]), overrides),
        axis=1,
    )
    out["is_clean_risk"] = ~out["asset_class"].isin(CLEAN_RISK_EXCLUDED_CLASSES)
    out["is_btc"] = out["symbol"] == "BTC"
    out["is_eth"] = out["symbol"] == "ETH"
    out["is_top10_ex_btc_eth"] = out["rank"].le(10) & ~out["symbol"].isin(["BTC", "ETH"])
    return out.sort_values(["date", "rank", "symbol"]).reset_index(drop=True)


def build_constituent_rotation_tables(
    daily: pd.DataFrame,
    *,
    events_path: Path | None = None,
) -> dict[str, pd.DataFrame]:
    """Build all daily constituent breadth, rotation, beta, and event-response tables."""

    if daily.empty:
        return {
            "gap": constituent_gap_report(False),
            "breadth": empty_altseason_breadth(),
            "indexes": empty_return_indexes(),
            "dispersion": empty_return_dispersion(),
            "beta": empty_rolling_beta(),
            "rotation": empty_rotation_returns(),
            "events": empty_event_response(),
        }
    prepared = _prepare_returns(daily)
    indexes = constituent_return_indexes(prepared)
    breadth = altseason_breadth(prepared, indexes)
    dispersion = return_dispersion(prepared)
    beta = rolling_beta_to_btc_eth(indexes)
    rotation = category_rotation_returns(indexes, breadth)
    events = (
        event_response_top_constituents(indexes, events_path)
        if events_path
        else empty_event_response()
    )
    return {
        "gap": constituent_gap_report(True, daily),
        "breadth": breadth,
        "indexes": indexes,
        "dispersion": dispersion,
        "beta": beta,
        "rotation": rotation,
        "events": events,
    }


def constituent_gap_report(
    has_daily_constituents: bool,
    daily: pd.DataFrame | None = None,
) -> pd.DataFrame:
    status = "available" if has_daily_constituents else "skipped"
    reason = (
        "Current-top50 exploratory daily OHLCV cohort is present."
        if has_daily_constituents
        else "No normalized daily constituent OHLCV file is available."
    )
    frame = daily if daily is not None else pd.DataFrame()
    missing_market_cap_rows = (
        int(frame["market_cap_missing_or_nonpositive"].sum())
        if "market_cap_missing_or_nonpositive" in frame
        else 0
    )
    row_count = len(frame)
    return pd.DataFrame(
        [
            {
                "dataset": "daily_constituent_ohlcv",
                "status": status,
                "reason": reason,
                "row_count": row_count,
                "market_cap_missing_or_nonpositive_rows": missing_market_cap_rows,
                "market_cap_missing_or_nonpositive_share": (
                    missing_market_cap_rows / row_count if row_count else 0
                ),
                "guardrail": "current_top50_exploratory_survivorship_biased_not_primary_altseason",
            }
        ]
    )


def _prepare_returns(daily: pd.DataFrame) -> pd.DataFrame:
    out = daily.copy()
    out["date"] = pd.to_datetime(out["date"])
    out = out.sort_values(["symbol", "date"])
    out["return_1d"] = out.groupby("symbol")["close_usd"].pct_change()
    out["return_30d"] = out.groupby("symbol")["close_usd"].pct_change(30)
    out["return_90d"] = out.groupby("symbol")["close_usd"].pct_change(90)
    out["return_180d"] = out.groupby("symbol")["close_usd"].pct_change(180)
    out["market_cap_lag1"] = out.groupby("symbol")["market_cap_usd"].shift(1)
    return out


def constituent_return_indexes(prepared: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for date_value, group in prepared.groupby("date", sort=True):
        specs = {
            "top50_current_sample": group["symbol"].notna(),
            "top50_ex_btc_eth": ~group["symbol"].isin(["BTC", "ETH"]),
            "top10_ex_btc_eth": group["is_top10_ex_btc_eth"],
            "clean_risk_ex_btc_eth": group["is_clean_risk"] & ~group["symbol"].isin(["BTC", "ETH"]),
            "btc": group["symbol"] == "BTC",
            "eth": group["symbol"] == "ETH",
        }
        for universe, mask in specs.items():
            subset = group[mask].dropna(subset=["return_1d"])
            if subset.empty:
                continue
            weights = pd.to_numeric(subset["market_cap_lag1"], errors="coerce")
            returns = pd.to_numeric(subset["return_1d"], errors="coerce")
            if weights.notna().sum() and weights.sum() > 0:
                daily_return = float(np.average(returns.fillna(0), weights=weights.fillna(0)))
            else:
                daily_return = float(returns.mean())
            rows.append(
                {
                    "date": date_value,
                    "universe": universe,
                    "asset_count": int(subset["symbol"].nunique()),
                    "daily_return": daily_return,
                    "method_note": SAMPLE_NOTE,
                }
            )
    out = pd.DataFrame(rows)
    if out.empty:
        return empty_return_indexes()
    out = out.sort_values(["universe", "date"])
    out["cumulative_index"] = out.groupby("universe")["daily_return"].transform(
        lambda series: (1 + series.fillna(0)).cumprod() * 100
    )
    out["return_30d"] = out.groupby("universe")["cumulative_index"].pct_change(30)
    out["return_90d"] = out.groupby("universe")["cumulative_index"].pct_change(90)
    return out.sort_values(["date", "universe"]).reset_index(drop=True)


def altseason_breadth(prepared: pd.DataFrame, indexes: pd.DataFrame) -> pd.DataFrame:
    if prepared.empty or indexes.empty:
        return empty_altseason_breadth()
    btc = prepared[prepared["symbol"] == "BTC"][["date", "return_90d"]].rename(
        columns={"return_90d": "btc_return_90d"}
    )
    eth = prepared[prepared["symbol"] == "ETH"][["date", "return_90d"]].rename(
        columns={"return_90d": "eth_return_90d"}
    )
    risk = prepared[prepared["is_clean_risk"] & ~prepared["symbol"].isin(["BTC", "ETH"])].copy()
    risk = risk.merge(btc, on="date", how="left").merge(eth, on="date", how="left")
    grouped = risk.dropna(subset=["return_90d", "btc_return_90d"]).groupby("date")
    rows = []
    for date_value, group in grouped:
        share_beating_btc = float((group["return_90d"] > group["btc_return_90d"]).mean())
        share_beating_eth = float((group["return_90d"] > group["eth_return_90d"]).mean())
        median_risk = float(group["return_90d"].median())
        btc_ret = float(group["btc_return_90d"].iloc[0])
        eth_ret = (
            float(group["eth_return_90d"].iloc[0])
            if pd.notna(group["eth_return_90d"].iloc[0])
            else np.nan
        )
        rows.append(
            {
                "date": date_value,
                "risk_asset_count": int(group["symbol"].nunique()),
                "share_risk_beating_btc_90d": share_beating_btc,
                "share_risk_beating_eth_90d": share_beating_eth,
                "median_risk_return_90d": median_risk,
                "btc_return_90d": btc_ret,
                "eth_return_90d": eth_ret,
                "breadth_regime": classify_breadth_regime(
                    share_beating_btc, btc_ret, eth_ret, median_risk
                ),
                "method_note": SAMPLE_NOTE,
            }
        )
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def classify_breadth_regime(
    share_beating_btc: float,
    btc_return_90d: float,
    eth_return_90d: float,
    median_risk_return_90d: float,
) -> str:
    if share_beating_btc >= 0.70:
        return "current_cohort_broad_breadth"
    if share_beating_btc < 0.30:
        return "current_cohort_btc_dominant_or_risk_off"
    if btc_return_90d > eth_return_90d and btc_return_90d > median_risk_return_90d:
        return "current_cohort_btc_led"
    if eth_return_90d > btc_return_90d and eth_return_90d > median_risk_return_90d:
        return "current_cohort_eth_led"
    return "current_cohort_mixed_rotation"


def return_dispersion(prepared: pd.DataFrame) -> pd.DataFrame:
    risk = prepared[prepared["is_clean_risk"] & ~prepared["symbol"].isin(["BTC", "ETH"])].copy()
    if risk.empty:
        return empty_return_dispersion()
    rows = []
    for date_value, group in risk.groupby("date", sort=True):
        returns = pd.to_numeric(group["return_1d"], errors="coerce").dropna()
        returns_30d = pd.to_numeric(group["return_30d"], errors="coerce").dropna()
        if returns.empty:
            continue
        rows.append(
            {
                "date": date_value,
                "asset_count": int(group["symbol"].nunique()),
                "mean_return_1d": float(returns.mean()),
                "median_return_1d": float(returns.median()),
                "p10_return_1d": float(returns.quantile(0.10)),
                "p90_return_1d": float(returns.quantile(0.90)),
                "dispersion_1d_p90_minus_p10": float(
                    returns.quantile(0.90) - returns.quantile(0.10)
                ),
                "positive_share_1d": float((returns > 0).mean()),
                "dispersion_30d_std": float(returns_30d.std()) if not returns_30d.empty else np.nan,
                "method_note": SAMPLE_NOTE,
            }
        )
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def rolling_beta_to_btc_eth(
    indexes: pd.DataFrame, windows: tuple[int, ...] = (90, 180)
) -> pd.DataFrame:
    if indexes.empty:
        return empty_rolling_beta()
    wide = indexes.pivot(index="date", columns="universe", values="daily_return").sort_index()
    rows: list[dict[str, Any]] = []
    for universe in ["top50_ex_btc_eth", "top10_ex_btc_eth", "clean_risk_ex_btc_eth"]:
        if universe not in wide:
            continue
        for benchmark in ["btc", "eth"]:
            if benchmark not in wide:
                continue
            for window in windows:
                cov = (
                    wide[universe]
                    .rolling(window, min_periods=max(30, window // 2))
                    .cov(wide[benchmark])
                )
                var = wide[benchmark].rolling(window, min_periods=max(30, window // 2)).var()
                corr = (
                    wide[universe]
                    .rolling(window, min_periods=max(30, window // 2))
                    .corr(wide[benchmark])
                )
                beta = cov / var
                for date_value, beta_value in beta.dropna().items():
                    rows.append(
                        {
                            "date": date_value,
                            "universe": universe,
                            "benchmark": benchmark,
                            "window_days": window,
                            "beta": float(beta_value),
                            "correlation": float(corr.loc[date_value])
                            if pd.notna(corr.loc[date_value])
                            else np.nan,
                            "method_note": SAMPLE_NOTE,
                        }
                    )
    return (
        pd.DataFrame(rows)
        .sort_values(["date", "universe", "benchmark", "window_days"])
        .reset_index(drop=True)
    )


def category_rotation_returns(indexes: pd.DataFrame, breadth: pd.DataFrame) -> pd.DataFrame:
    if indexes.empty:
        return empty_rotation_returns()
    wide = indexes.pivot(index="date", columns="universe", values="return_90d").sort_index()
    breadth_regime = (
        breadth.set_index("date")["breadth_regime"]
        if not breadth.empty
        else pd.Series(dtype=object)
    )
    rows = []
    for date_value, row in wide.dropna(how="all").iterrows():
        btc_ret = row.get("btc", np.nan)
        eth_ret = row.get("eth", np.nan)
        risk_ret = row.get("clean_risk_ex_btc_eth", np.nan)
        top10_ret = row.get("top10_ex_btc_eth", np.nan)
        rows.append(
            {
                "date": date_value,
                "btc_return_90d": btc_ret,
                "eth_return_90d": eth_ret,
                "clean_risk_ex_btc_eth_return_90d": risk_ret,
                "top10_ex_btc_eth_return_90d": top10_ret,
                "large_cap_rotation_vs_btc": top10_ret - btc_ret
                if pd.notna(top10_ret) and pd.notna(btc_ret)
                else np.nan,
                "risk_rotation_vs_btc": risk_ret - btc_ret
                if pd.notna(risk_ret) and pd.notna(btc_ret)
                else np.nan,
                "breadth_regime": breadth_regime.get(date_value, ""),
                "method_note": SAMPLE_NOTE,
            }
        )
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def event_response_top_constituents(
    indexes: pd.DataFrame, events_path: Path | None
) -> pd.DataFrame:
    if indexes.empty or events_path is None or not events_path.exists():
        return empty_event_response()
    events = _load_events(events_path)
    if not events:
        return empty_event_response()
    wide = indexes.pivot(index="date", columns="universe", values="cumulative_index").sort_index()
    wide.index = pd.to_datetime(wide.index)
    rows = []
    for event in events:
        event_date = pd.Timestamp(event["date"])
        if event_date < wide.index.min() or event_date > wide.index.max():
            continue
        nearest = wide.index[wide.index.get_indexer([event_date], method="nearest")[0]]
        for universe in [
            "btc",
            "eth",
            "top50_ex_btc_eth",
            "top10_ex_btc_eth",
            "clean_risk_ex_btc_eth",
        ]:
            if universe not in wide:
                continue
            series = wide[universe].dropna()
            if nearest not in series.index:
                continue
            event_level = series.loc[nearest]
            for window in [1, 5, 10, 20]:
                pre_idx = _nearest_date(series.index, nearest - pd.Timedelta(days=window))
                post_idx = _nearest_date(series.index, nearest + pd.Timedelta(days=window))
                rows.append(
                    {
                        "event_id": event["id"],
                        "event_date": event["date"],
                        "event_label": event["description"],
                        "aligned_date": nearest.date().isoformat(),
                        "universe": universe,
                        "window_days": window,
                        "pre_window_return": float(event_level / series.loc[pre_idx] - 1)
                        if pre_idx is not None
                        else np.nan,
                        "post_window_return": float(series.loc[post_idx] / event_level - 1)
                        if post_idx is not None
                        else np.nan,
                        "method_note": SAMPLE_NOTE,
                    }
                )
    return (
        pd.DataFrame(rows)
        .sort_values(["event_date", "universe", "window_days"])
        .reset_index(drop=True)
    )


def constituent_rotation_summary(tables: dict[str, pd.DataFrame]) -> str:
    gap = tables.get("gap", pd.DataFrame())
    if gap.empty or gap["status"].iloc[0] != "available":
        return "# Current-Cohort Rotation Lab\n\nDaily constituent OHLCV is unavailable; outputs are skipped.\n"
    breadth = tables["breadth"]
    indexes = tables["indexes"]
    events = tables["events"]
    latest = breadth.dropna(subset=["share_risk_beating_btc_90d"]).tail(1)
    latest_line = ""
    if not latest.empty:
        row = latest.iloc[0]
        latest_line = (
            f"\n- Latest 90-day breadth: {float(row['share_risk_beating_btc_90d']):.1%} "
            f"of clean-risk sample assets beat BTC; regime `{row['breadth_regime']}`."
        )
    index_line = ""
    if not indexes.empty:
        span = f"{pd.to_datetime(indexes['date']).min().date()} to {pd.to_datetime(indexes['date']).max().date()}"
        index_line = f"\n- Daily constituent span: {span}; index rows: {len(indexes):,}."
    event_line = f"\n- Event-response rows: {len(events):,}." if not events.empty else ""
    return f"""# Current-Cohort Rotation Lab

The current-cohort daily layer adds exploratory breadth, dispersion, rolling beta, rotation, and event-response diagnostics from the available DefiLlama current-top50 ex-stablecoin OHLCV sample.

{SAMPLE_NOTE}

Definitions:

- `current_cohort_broad_breadth`: at least 70% of clean-risk ex-BTC/ETH current-cohort constituents beat BTC over 90 days.
- `current_cohort_btc_led`: BTC beats ETH and the median clean-risk current-cohort sample over 90 days.
- `current_cohort_eth_led`: ETH beats BTC and the median clean-risk current-cohort sample over 90 days.
- `large_cap_rotation_vs_btc`: top10 ex-BTC/ETH 90-day return minus BTC 90-day return.
{latest_line}{index_line}{event_line}

Guardrail: this is a current-top50 cohort diagnostic. It is survivorship-biased, not point-in-time, and not the primary altseason backtest. Treat it as exploratory until a full point-in-time daily OHLCV/mcap file is supplied for every asset that ever appears in the PIT top100/top200 universe.
"""


def _load_events(path: Path) -> list[dict[str, str]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows: list[dict[str, str]] = []
    for section in ["primary_breaks", "secondary_candidates"]:
        for item in data.get(section, []) or []:
            if "date" in item and "id" in item:
                rows.append(
                    {
                        "id": str(item["id"]),
                        "date": str(item["date"]),
                        "description": str(item.get("description", item["id"])),
                    }
                )
    return rows


def _nearest_date(index: pd.DatetimeIndex, target: pd.Timestamp) -> pd.Timestamp | None:
    if index.empty:
        return None
    pos = index.get_indexer([target], method="nearest")[0]
    if pos < 0:
        return None
    return index[pos]


def empty_altseason_breadth() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "date",
            "risk_asset_count",
            "share_risk_beating_btc_90d",
            "share_risk_beating_eth_90d",
            "median_risk_return_90d",
            "btc_return_90d",
            "eth_return_90d",
            "breadth_regime",
            "method_note",
        ]
    )


def empty_return_indexes() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "date",
            "universe",
            "asset_count",
            "daily_return",
            "method_note",
            "cumulative_index",
            "return_30d",
            "return_90d",
        ]
    )


def empty_return_dispersion() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "date",
            "asset_count",
            "mean_return_1d",
            "median_return_1d",
            "p10_return_1d",
            "p90_return_1d",
            "dispersion_1d_p90_minus_p10",
            "positive_share_1d",
            "dispersion_30d_std",
            "method_note",
        ]
    )


def empty_rolling_beta() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "date",
            "universe",
            "benchmark",
            "window_days",
            "beta",
            "correlation",
            "method_note",
        ]
    )


def empty_rotation_returns() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "date",
            "btc_return_90d",
            "eth_return_90d",
            "clean_risk_ex_btc_eth_return_90d",
            "top10_ex_btc_eth_return_90d",
            "large_cap_rotation_vs_btc",
            "risk_rotation_vs_btc",
            "breadth_regime",
            "method_note",
        ]
    )


def empty_event_response() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "event_id",
            "event_date",
            "event_label",
            "aligned_date",
            "universe",
            "window_days",
            "pre_window_return",
            "post_window_return",
            "method_note",
        ]
    )
