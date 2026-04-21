"""Rolling OLS with **drop-one marginal R²** (not Shapley/Owen).

For each regressor :math:`x_j`, we compare the full-window RSS to the RSS from
the model that drops :math:`x_j` only, then report :math:`(RSS_{-j}-RSS)/TSS`.
This measures incremental variance **conditional on the ordering implied by
single-variable deletion**, not a fair Shapley allocation across correlated blocks.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


def _rss(y: np.ndarray, X: np.ndarray) -> float:
    if X.shape[1] == 0 or len(y) == 0:
        return float(np.var(y) * len(y))
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    return float(resid @ resid)


def rolling_ols(
    y: pd.Series,
    X: pd.DataFrame,
    window: int = 180,
    min_periods: int | None = None,
    dropna_first: bool = True,
) -> pd.DataFrame:
    """Rolling OLS with intercept. Returns per-date β, R², RSS, N.

    Row ``t`` uses observations ``[t-window+1, t]`` inclusive.

    ``dropna_first=True`` (default) drops any row with a NaN in ``y`` or
    ``X`` **before** rolling, so each window is dense. The output is still
    indexed on the surviving dates. This is the correct treatment when
    regressors have scattered missingness and you don't want window size to
    depend on gaps.
    """

    if min_periods is None:
        min_periods = window

    df = pd.concat([y.rename("y"), X], axis=1)
    if dropna_first:
        df = df.dropna()
    col_x = list(X.columns)

    rows = []
    y_arr = df["y"].to_numpy(dtype=float)
    X_arr_full = df[col_x].to_numpy(dtype=float)
    idx = df.index
    n = len(df)

    for t in range(n):
        lo = t - window + 1
        if lo < 0:
            continue
        yw = y_arr[lo : t + 1]
        Xw = X_arr_full[lo : t + 1]
        mask = np.isfinite(yw) & np.all(np.isfinite(Xw), axis=1)
        if mask.sum() < min_periods:
            continue
        yw = yw[mask]
        Xw = Xw[mask]
        Xw_c = np.column_stack([np.ones(len(Xw)), Xw])  # intercept
        beta, *_ = np.linalg.lstsq(Xw_c, yw, rcond=None)
        resid = yw - Xw_c @ beta
        tss = float(((yw - yw.mean()) ** 2).sum())
        rss = float(resid @ resid)
        r2 = 1.0 - rss / tss if tss > 0 else np.nan

        # Partial R² for each regressor: drop it, refit, measure RSS rise
        partial_r2 = {}
        for j, name in enumerate(col_x):
            cols = [k for k in range(Xw.shape[1]) if k != j]
            Xw_j = Xw[:, cols] if cols else np.zeros((len(yw), 0))
            Xw_jc = np.column_stack([np.ones(len(yw)), Xw_j]) if Xw_j.shape[1] else np.ones((len(yw), 1))
            beta_j, *_ = np.linalg.lstsq(Xw_jc, yw, rcond=None)
            resid_j = yw - Xw_jc @ beta_j
            rss_j = float(resid_j @ resid_j)
            partial_r2[name] = (rss_j - rss) / tss if tss > 0 else np.nan

        row = {"date": idx[t], "n": int(mask.sum()), "r2": r2, "rss": rss}
        row["intercept"] = float(beta[0])
        for j, name in enumerate(col_x, start=1):
            row[f"beta_{name}"] = float(beta[j])
            row[f"pr2_{name}"] = float(partial_r2[name])
        rows.append(row)

    if not rows:
        return pd.DataFrame(columns=["n", "r2", "rss", "intercept"]).rename_axis("date")
    return pd.DataFrame(rows).set_index("date")


__all__ = ["rolling_ols"]
