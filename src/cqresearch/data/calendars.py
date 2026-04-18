"""Calendar utilities.

Two calendars matter in this project:

* **Crypto-7** (``crypto7``): every UTC calendar day. The native clock for
  price, on-chain, and DeFi series. This is the **master panel calendar**.
* **Business-5** (``business5``): Mon-Fri excluding US holidays. Native for
  equity ETFs, FRED macro, DXY, Farside ETF flows.

The `align_to_master` helper forward-fills business-5 "stock" variables into
the crypto-7 calendar (up to 4-day gap to cover long weekends) and pads
business-5 "flow" variables (ETF flows, returns) with 0 on weekends because
"no trading day" is an *actual* zero inflow, not a missing observation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

SeriesKind = Literal["stock", "flow", "rate"]

# Default sample window for v0.1 analyses.
DEFAULT_START: pd.Timestamp = pd.Timestamp("2020-01-01")
DEFAULT_END: pd.Timestamp = pd.Timestamp("2026-04-11")


@dataclass(frozen=True)
class Calendar:
    name: str
    freq: str  # pandas freq alias
    description: str


CRYPTO_7 = Calendar("crypto7", "D", "All UTC calendar days")
BUSINESS_5 = Calendar("business5", "B", "Mon-Fri, US business days")


def crypto_index(
    start: pd.Timestamp | str = DEFAULT_START,
    end: pd.Timestamp | str = DEFAULT_END,
) -> pd.DatetimeIndex:
    """Inclusive daily UTC index for the master panel."""

    return pd.date_range(start=pd.Timestamp(start), end=pd.Timestamp(end), freq="D")


def to_daily_utc(ts: pd.Series | pd.Index) -> pd.DatetimeIndex:
    """Normalize any datetime-like series to UTC midnight (`date` resolution)."""

    out = pd.to_datetime(ts, errors="coerce", utc=True)
    # `out` may be a Series or Index; convert to DatetimeIndex then strip tz.
    di = pd.DatetimeIndex(out)
    if di.tz is not None:
        di = di.tz_convert("UTC").tz_localize(None)
    return di.normalize()


def align_to_master(
    series: pd.Series,
    kind: SeriesKind,
    master_index: pd.DatetimeIndex | None = None,
    ffill_limit_days: int = 4,
) -> pd.Series:
    """Reindex a daily series onto the master crypto-7 calendar.

    Parameters
    ----------
    series
        Indexed by date. Must already be deduped + sorted.
    kind
        * ``"stock"``  — level variable (price, market cap, TVL). Forward-fill
          up to ``ffill_limit_days`` to cover weekends/holidays, then leave NaN.
        * ``"flow"``   — flow variable (ETF inflow, log return). Weekends are
          *actual zeros*; fill with 0.
        * ``"rate"``   — interest / implied-vol level. Forward-fill up to
          ``ffill_limit_days`` only (no zero-fill).
    master_index
        Target index. Defaults to the project default crypto-7 window.
    ffill_limit_days
        Max number of consecutive days to forward-fill for stock/rate kinds.

    Returns
    -------
    pd.Series aligned to ``master_index`` with NaNs preserved *outside* the
    series' actual observation window (so pre-history is never fabricated).
    """

    if master_index is None:
        master_index = crypto_index()

    s = series.copy()
    s.index = to_daily_utc(s.index)
    s = s[~s.index.duplicated(keep="last")].sort_index()

    first_valid = s.first_valid_index()
    last_valid = s.last_valid_index()

    s = s.reindex(master_index)

    if first_valid is None:
        return s  # all-NaN

    if kind == "flow":
        # Only pad with 0 *within* the series' natural window, never before
        # the first observation (don't fabricate pre-history).
        mask = (s.index >= first_valid) & (s.index <= last_valid)
        s.loc[mask] = s.loc[mask].fillna(0.0)
    elif kind in ("stock", "rate"):
        s = s.ffill(limit=ffill_limit_days)
        # Kill any ffill leakage before the first actual observation.
        s.loc[s.index < first_valid] = np.nan
    else:  # pragma: no cover - defensive
        raise ValueError(f"Unknown kind: {kind!r}")
    return s


def sample_mask(
    index: pd.DatetimeIndex,
    start: pd.Timestamp | str = DEFAULT_START,
    end: pd.Timestamp | str = DEFAULT_END,
) -> pd.Series:
    start_ts, end_ts = pd.Timestamp(start), pd.Timestamp(end)
    return pd.Series(
        (index >= start_ts) & (index <= end_ts), index=index, name="in_sample"
    )
