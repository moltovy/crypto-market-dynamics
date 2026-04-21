"""Calendar utilities.

Two calendars matter in this project:

* **Crypto-7** (``crypto7``): every UTC calendar day. The native clock for
  price, on-chain, and DeFi series. This is the **master panel calendar**.
* **Business-5** (``business5``): Mon-Fri excluding US holidays. Native for
  equity ETFs, FRED macro, DXY, Farside ETF flows.

The `align_to_master` helper forward-fills business-5 "stock" variables into
the crypto-7 calendar (forward-fill limit from ``config/calendars.yml``,
``calendar_daily.ffill_limit``) and pads business-5 "flow" variables (ETF
flows, returns) with 0 on weekends because "no trading day" is an *actual*
zero inflow, not a missing observation.

**Headline regressions (Paper 1):** mixed TradFi + crypto models should also
be run on **US market trading days** only (see :func:`business_day_mask`) to
avoid weekend flat-lines in TradFi returns; full calendar-daily results are
reported as robustness.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

import numpy as np
import pandas as pd
import yaml

from config.paths import CALENDARS_YML

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


@lru_cache(maxsize=1)
def _calendar_yaml() -> dict:
    """Parse ``config/calendars.yml`` once (source of truth for ffill limits)."""

    if not CALENDARS_YML.is_file():
        return {}
    return yaml.safe_load(CALENDARS_YML.read_text(encoding="utf-8")) or {}


def get_master_ffill_limit() -> int:
    """Forward-fill cap (days) when aligning stock/rate series to the crypto-7 master index."""

    cfg = _calendar_yaml()
    daily = cfg.get("calendar_daily") or {}
    return int(daily.get("ffill_limit", 3))


def business_day_mask(index: pd.DatetimeIndex) -> pd.Series:
    """True on US **weekday** rows (Mon–Fri). Use as a filter for headline macro/ETF regressions.

    Note: This does not remove US market holidays; for a full NYSE calendar,
    plug in ``pandas_market_calendars`` or an exchange calendar in a later revision.
    """

    return pd.Series(index.weekday < 5, index=index, name="is_business_day")


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
    ffill_limit_days: int | None = None,
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
        If ``None``, uses :func:`get_master_ffill_limit` (from ``config/calendars.yml``).

    Returns
    -------
    pd.Series aligned to ``master_index`` with NaNs preserved *outside* the
    series' actual observation window (so pre-history is never fabricated).
    """

    if master_index is None:
        master_index = crypto_index()

    if ffill_limit_days is None:
        ffill_limit_days = get_master_ffill_limit()

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
