"""Structural-break diagnostics.

Implements:

* :func:`chow_test` — F test for a known breakpoint on OLS coefficients.
* :func:`sup_f_sweep` — supremum-F sweep (Andrews 1993) for a **single** unknown
  break over a trimmed interior window (15%..85%). This is **not** the
  Bai–Perron (1998) dynamic-programming **multi-break** estimator; do not label
  results as full Bai–Perron unless that procedure is implemented separately.
* :func:`placebo_breaks` — Monte-Carlo p-value for a supF by resampling dates
  under the null of no break.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


def _fit(y: np.ndarray, X: np.ndarray) -> tuple[np.ndarray, float]:
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    rss = float(resid @ resid)
    return beta, rss


@dataclass
class ChowResult:
    f_stat: float
    p_value: float
    n: int
    k: int
    breakpoint: pd.Timestamp


def chow_test(
    y: pd.Series, X: pd.DataFrame, breakpoint: pd.Timestamp,
) -> ChowResult:
    """Classical Chow F-test of coefficient equality across ``breakpoint``."""

    from scipy import stats

    df = pd.concat([y.rename("y"), X], axis=1).dropna()
    df = df.sort_index()
    bp = pd.Timestamp(breakpoint)
    pre = df[df.index < bp]
    post = df[df.index >= bp]
    if len(pre) < 2 * X.shape[1] + 2 or len(post) < 2 * X.shape[1] + 2:
        raise ValueError("insufficient obs on one side of breakpoint")

    def design(d: pd.DataFrame) -> np.ndarray:
        return np.column_stack([np.ones(len(d)), d[X.columns].to_numpy(float)])

    _, rss_full = _fit(df["y"].to_numpy(float), design(df))
    _, rss_pre = _fit(pre["y"].to_numpy(float), design(pre))
    _, rss_post = _fit(post["y"].to_numpy(float), design(post))

    rss_unr = rss_pre + rss_post
    k = X.shape[1] + 1  # intercept + regressors
    n = len(df)
    f = ((rss_full - rss_unr) / k) / (rss_unr / (n - 2 * k))
    p = 1 - stats.f.cdf(f, k, n - 2 * k)
    return ChowResult(f_stat=float(f), p_value=float(p), n=n, k=k, breakpoint=bp)


@dataclass
class SupFResult:
    sup_f: float
    argmax_date: pd.Timestamp
    trim: float
    f_series: pd.Series  # per-date F


def sup_f_sweep(
    y: pd.Series, X: pd.DataFrame, trim: float = 0.15,
) -> SupFResult:
    """Compute a Chow-F statistic for every candidate breakpoint in the
    trimmed interior window and return the maximum.

    ``trim=0.15`` excludes the first and last 15% of observations (standard
    Andrews/Bai-Perron trimming to avoid edge degeneracies).
    """

    df = pd.concat([y.rename("y"), X], axis=1).dropna().sort_index()
    n = len(df)
    lo, hi = int(n * trim), int(n * (1 - trim))
    if hi <= lo:
        raise ValueError("trim too wide")
    k = X.shape[1] + 1

    y_arr = df["y"].to_numpy(float)
    X_arr = np.column_stack([np.ones(n), df[X.columns].to_numpy(float)])

    _, rss_full = _fit(y_arr, X_arr)

    f_vals = np.full(n, np.nan)
    for i in range(lo, hi):
        _, rss_pre = _fit(y_arr[:i], X_arr[:i])
        _, rss_post = _fit(y_arr[i:], X_arr[i:])
        rss_unr = rss_pre + rss_post
        denom = rss_unr / (n - 2 * k)
        num = (rss_full - rss_unr) / k
        if denom <= 0 or num < 0:
            continue
        f_vals[i] = num / denom

    f_series = pd.Series(f_vals, index=df.index, name="supF")
    argmax = f_series.idxmax()
    return SupFResult(
        sup_f=float(f_series.max()),
        argmax_date=argmax,
        trim=trim,
        f_series=f_series,
    )


def placebo_breaks(
    y: pd.Series, X: pd.DataFrame, n_permutations: int = 500, trim: float = 0.15,
    seed: int = 42,
) -> tuple[float, np.ndarray]:
    """Return (empirical p-value, null distribution of supF) under shuffled y."""

    rng = np.random.default_rng(seed)
    df = pd.concat([y.rename("y"), X], axis=1).dropna().sort_index()
    base = sup_f_sweep(df["y"], df[X.columns], trim=trim).sup_f

    null = np.empty(n_permutations)
    y_arr = df["y"].to_numpy(float)
    for i in range(n_permutations):
        perm = rng.permutation(y_arr)
        y_perm = pd.Series(perm, index=df.index, name=y.name)
        null[i] = sup_f_sweep(y_perm, df[X.columns], trim=trim).sup_f
    p = float((null >= base).mean())
    return p, null


__all__ = ["ChowResult", "SupFResult", "chow_test", "sup_f_sweep", "placebo_breaks"]
