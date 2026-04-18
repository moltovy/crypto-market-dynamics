"""VAR + FEVD with BIC lag selection.

Implements a Diebold-Yilmaz-style connectedness computation on a small VAR
using statsmodels. Inputs must be stationary (first-differences/returns).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR


@dataclass
class FevdResult:
    horizon: int
    table: pd.DataFrame  # row = from, col = to; entries sum to 1 per row
    lag_order: int
    n: int


def select_lag(df: pd.DataFrame, maxlags: int = 10) -> int:
    model = VAR(df)
    sel = model.select_order(maxlags=maxlags)
    return int(sel.bic)


def fit_var_fevd(
    df: pd.DataFrame, horizon: int = 10, maxlags: int = 10,
) -> FevdResult:
    df_ = df.dropna().copy()
    p = max(1, select_lag(df_, maxlags=maxlags))
    res = VAR(df_).fit(p)
    fevd = res.fevd(horizon)
    # fevd.decomp has shape (n_vars, horizon, n_vars) — use the last step
    decomp_h = fevd.decomp[:, horizon - 1, :]
    # Normalize each row to 1
    decomp_h = decomp_h / decomp_h.sum(axis=1, keepdims=True)
    out = pd.DataFrame(decomp_h, index=df_.columns, columns=df_.columns)
    out.index.name = "from"
    out.columns.name = "to"
    return FevdResult(horizon=horizon, table=out, lag_order=p, n=len(df_))


def connectedness_index(fevd: FevdResult) -> float:
    """Diebold-Yilmaz total connectedness index (0-100)."""

    tab = fevd.table.to_numpy()
    off_diag = tab.sum() - np.trace(tab)
    n = tab.shape[0]
    return float(100.0 * off_diag / n)


__all__ = ["FevdResult", "select_lag", "fit_var_fevd", "connectedness_index"]
