"""OLS with HAC (Newey-West) standard errors and subsample convenience.

We standardize *all* OLS inference on HAC with Bartlett kernel, lags = 5 for
daily returns (roughly 1 week of serial-correlation/conditional-heteroscedasticity
protection). This is conservative for daily crypto returns which exhibit fat
tails and volatility clustering.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm


@dataclass
class OLSResult:
    params: pd.Series
    hac_se: pd.Series
    tvals: pd.Series
    pvals: pd.Series
    r2: float
    adj_r2: float
    nobs: int
    label: str

    def to_frame(self) -> pd.DataFrame:
        out = pd.concat(
            [self.params, self.hac_se, self.tvals, self.pvals], axis=1
        )
        out.columns = ["beta", "hac_se", "t", "p"]
        out["label"] = self.label
        out["n"] = self.nobs
        out["r2"] = self.r2
        out["adj_r2"] = self.adj_r2
        return out


def fit_ols(
    y: pd.Series,
    X: pd.DataFrame,
    *,
    hac_lags: int = 5,
    add_const: bool = True,
    label: str = "",
) -> OLSResult:
    """Fit OLS with Newey-West HAC standard errors on aligned ``y`` / ``X``.

    Rows with any NaN in ``y`` or ``X`` are dropped pairwise."""

    df = pd.concat([y, X], axis=1).dropna()
    if add_const:
        Xf = sm.add_constant(df[X.columns], has_constant="add")
    else:
        Xf = df[X.columns]
    res = sm.OLS(df[y.name], Xf).fit(cov_type="HAC", cov_kwds={"maxlags": hac_lags})
    return OLSResult(
        params=res.params,
        hac_se=res.bse,
        tvals=res.tvalues,
        pvals=res.pvalues,
        r2=float(res.rsquared),
        adj_r2=float(res.rsquared_adj),
        nobs=int(res.nobs),
        label=label,
    )


def subsample_ols(
    y: pd.Series,
    X: pd.DataFrame,
    breakpoint: pd.Timestamp,
    *,
    hac_lags: int = 5,
    labels: tuple[str, str] = ("pre", "post"),
) -> dict[str, OLSResult]:
    """Fit ``y ~ X`` separately *before* and *from* ``breakpoint``."""

    bp = pd.Timestamp(breakpoint)
    pre_mask = y.index < bp
    post_mask = y.index >= bp
    return {
        labels[0]: fit_ols(y[pre_mask], X[pre_mask], hac_lags=hac_lags, label=labels[0]),
        labels[1]: fit_ols(y[post_mask], X[post_mask], hac_lags=hac_lags, label=labels[1]),
    }


__all__ = ["OLSResult", "fit_ols", "subsample_ols"]
