"""Event study on daily log returns.

We estimate abnormal returns under a simple **market model** fit to a
pre-event estimation window (default: 180 trading days ending 10 days before
the event), then aggregate into cumulative abnormal returns (CARs) over
symmetric windows around the event date. Placebo dates are supported for
statistical inference under the null of no event effect.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm


@dataclass
class EventResult:
    event_date: pd.Timestamp
    car_by_window: pd.DataFrame  # columns: window, car, t_stat
    daily_ar: pd.Series            # AR series over [-max_window, +max_window]
    alpha: float
    beta: float
    sigma_e: float


def _estimation_window(
    idx: pd.DatetimeIndex, event_date: pd.Timestamp, n: int, gap: int,
) -> slice:
    pos = idx.get_indexer([event_date], method="nearest")[0]
    start = max(0, pos - gap - n)
    end = max(0, pos - gap)
    return slice(start, end)


def market_model_event(
    ret_asset: pd.Series,
    ret_market: pd.Series,
    event_date: pd.Timestamp,
    *,
    estimation_n: int = 180,
    estimation_gap: int = 10,
    windows: tuple[tuple[int, int], ...] = ((-1, 1), (-5, 5), (0, 5), (0, 30)),
) -> EventResult:
    """Run a market-model event study.

    Both series must be daily log returns indexed by date.
    """

    df = pd.concat([ret_asset.rename("r"), ret_market.rename("m")], axis=1).dropna()
    idx = df.index
    ed = pd.Timestamp(event_date)

    # Estimation window
    est_sl = _estimation_window(idx, ed, estimation_n, estimation_gap)
    est = df.iloc[est_sl]
    if len(est) < 30:
        raise ValueError(f"too few estimation obs for {ed.date()}: {len(est)}")
    X = sm.add_constant(est["m"])
    res = sm.OLS(est["r"], X).fit()
    alpha, beta = float(res.params["const"]), float(res.params["m"])
    sigma_e = float(np.sqrt(res.mse_resid))

    # Event window — use widest window for AR series
    max_left = min(w[0] for w in windows)
    max_right = max(w[1] for w in windows)
    pos = idx.get_indexer([ed], method="nearest")[0]
    lo = max(0, pos + max_left)
    hi = min(len(idx) - 1, pos + max_right)
    evt = df.iloc[lo : hi + 1].copy()
    evt["expected"] = alpha + beta * evt["m"]
    evt["ar"] = evt["r"] - evt["expected"]
    evt["rel_day"] = range(lo - pos, hi - pos + 1)
    evt = evt.set_index("rel_day")

    rows = []
    for left, right in windows:
        wnd = evt.loc[left:right]
        car = float(wnd["ar"].sum())
        n_days = len(wnd)
        t = car / (sigma_e * np.sqrt(max(n_days, 1)))
        rows.append({"window": f"[{left:+d},{right:+d}]", "car": car, "t_stat": float(t), "n_days": n_days})

    return EventResult(
        event_date=ed,
        car_by_window=pd.DataFrame(rows),
        daily_ar=evt["ar"].rename(f"ar_{ed.date()}"),
        alpha=alpha,
        beta=beta,
        sigma_e=sigma_e,
    )


def placebo_cars(
    ret_asset: pd.Series,
    ret_market: pd.Series,
    event_date: pd.Timestamp,
    *,
    window: tuple[int, int] = (-5, 5),
    n_placebos: int = 200,
    seed: int = 42,
    min_offset: int = 60,
) -> tuple[float, np.ndarray, float]:
    """Return ``(empirical p-value, null distribution, actual CAR)``.

    Draws ``n_placebos`` random dates in the returns sample that are at least
    ``min_offset`` days away from any pre-registered event date (using this
    single ``event_date``), runs the same market-model CAR calculation, and
    computes a two-sided p-value."""

    rng = np.random.default_rng(seed)
    base = market_model_event(ret_asset, ret_market, event_date, windows=(window,))
    actual = float(base.car_by_window.iloc[0]["car"])

    idx = ret_asset.dropna().index
    candidates = [d for d in idx if abs((d - event_date).days) >= min_offset]
    if len(candidates) < n_placebos:
        n_placebos = len(candidates)
    picks = rng.choice(candidates, size=n_placebos, replace=False)

    null = np.empty(n_placebos)
    for i, d in enumerate(picks):
        try:
            r = market_model_event(ret_asset, ret_market, pd.Timestamp(d), windows=(window,))
            null[i] = float(r.car_by_window.iloc[0]["car"])
        except Exception:
            null[i] = np.nan
    null = null[np.isfinite(null)]
    p = float((np.abs(null) >= abs(actual)).mean()) if len(null) else np.nan
    return p, null, actual


__all__ = ["EventResult", "market_model_event", "placebo_cars"]
