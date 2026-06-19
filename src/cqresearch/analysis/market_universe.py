"""Universe builders for market-structure outputs."""

from __future__ import annotations

import pandas as pd


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
        reason = "Point-in-time market-cap source is present."
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
