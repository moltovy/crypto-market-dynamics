"""Return/volatility feature construction.

All return series are **log** returns unless explicitly noted (additive across
time, closer to normality, standard practice). Daily first-differences are
used for interest-rate levels since log-returns on rates are undefined at 0%.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def log_return(price: pd.Series) -> pd.Series:
    """Daily log return: ``log(P_t / P_{t-1})``.

    Produces NaN for the first observation and wherever either side is NaN."""

    out = np.log(price.astype(float)) - np.log(price.astype(float).shift(1))
    return out.rename(f"{price.name}_logret" if price.name else "logret")


def first_diff(series: pd.Series) -> pd.Series:
    """First difference — appropriate for interest-rate levels."""

    return (series.astype(float) - series.astype(float).shift(1)).rename(
        f"{series.name}_d1" if series.name else "d1"
    )


def winsorize(series: pd.Series, q: float = 0.01) -> pd.Series:
    """Symmetric winsorization at the ``q`` / ``1-q`` quantiles (full-sample)."""

    lo = series.quantile(q)
    hi = series.quantile(1 - q)
    return series.clip(lower=lo, upper=hi)


def realized_vol(logret: pd.Series, window: int = 21, annualize: bool = True) -> pd.Series:
    """Rolling realized volatility of daily log returns.

    Default ``window=21`` is ~1 trading month; annualization factor √365 for
    crypto-7 calendars (not √252)."""

    s = logret.rolling(window, min_periods=window).std()
    if annualize:
        s = s * np.sqrt(365)
    return s.rename(f"{logret.name}_rvol{window}" if logret.name else f"rvol{window}")


def garman_klass(
    high: pd.Series, low: pd.Series, open_: pd.Series, close: pd.Series,
    window: int = 21, annualize: bool = True,
) -> pd.Series:
    """Garman-Klass volatility estimator — efficient OHLC volatility.

    Uses the same rolling/annualization conventions as :func:`realized_vol`."""

    log_hl = (np.log(high) - np.log(low)) ** 2
    log_co = (np.log(close) - np.log(open_)) ** 2
    gk = 0.5 * log_hl - (2 * np.log(2) - 1) * log_co
    out = gk.rolling(window, min_periods=window).mean().apply(np.sqrt)
    if annualize:
        out = out * np.sqrt(365)
    return out.rename("gk_vol")


def zscore(series: pd.Series, window: int | None = None) -> pd.Series:
    """Full-sample z-score (``window=None``) or rolling z-score."""

    if window is None:
        return (series - series.mean()) / series.std(ddof=0)
    mu = series.rolling(window, min_periods=window).mean()
    sd = series.rolling(window, min_periods=window).std(ddof=0)
    return (series - mu) / sd


__all__ = ["log_return", "first_diff", "winsorize", "realized_vol", "garman_klass", "zscore"]
