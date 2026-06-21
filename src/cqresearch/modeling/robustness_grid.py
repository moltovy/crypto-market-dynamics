"""Compact robustness-grid utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd

from cqresearch.data.calendars import business_day_mask
from cqresearch.features.returns import winsorize
from cqresearch.modeling.ols import fit_ols


def apply_winsorization(df: pd.DataFrame, q: float | None) -> pd.DataFrame:
    """Winsorize numeric columns or return a copy when ``q`` is None."""

    out = df.copy()
    if q is None:
        return out
    for col in out.columns:
        if out[col].dtype.kind in "fc":
            out[col] = winsorize(out[col], q=q)
    return out


def run_robustness_grid(
    feat: pd.DataFrame,
    y_col: str,
    regressors: list[str],
    windows: tuple[int, ...] = (90, 180, 365),
    hac_lags: tuple[int, ...] = (5, 10, 20),
    winsorization: tuple[float | None, ...] = (None, 0.01, 0.05),
    include_mvrv: tuple[bool, ...] = (True, False),
    calendars: tuple[str, ...] = ("crypto7", "weekday"),
) -> pd.DataFrame:
    """Run a small static trailing-window robustness grid."""

    rows: list[dict[str, object]] = []
    base_cols = [col for col in regressors if col in feat.columns]
    for window in windows:
        tail = feat.tail(window)
        for q in winsorization:
            data = apply_winsorization(tail, q)
            for lags in hac_lags:
                for use_mvrv in include_mvrv:
                    cols = [col for col in base_cols if use_mvrv or col != "btc_mvrv_d1"]
                    for calendar in calendars:
                        sub = data
                        if calendar == "weekday":
                            sub = sub.loc[business_day_mask(sub.index)]
                        try:
                            res = fit_ols(sub[y_col], sub[cols], hac_lags=lags, label="robustness")
                            rows.append(
                                {
                                    "window": window,
                                    "hac_lags": lags,
                                    "winsorization": "none" if q is None else q,
                                    "include_mvrv": use_mvrv,
                                    "calendar": calendar,
                                    "n": res.nobs,
                                    "r2": res.r2,
                                    "adj_r2": res.adj_r2,
                                    "error": "",
                                }
                            )
                        except Exception as exc:
                            rows.append(
                                {
                                    "window": window,
                                    "hac_lags": lags,
                                    "winsorization": "none" if q is None else q,
                                    "include_mvrv": use_mvrv,
                                    "calendar": calendar,
                                    "n": 0,
                                    "r2": np.nan,
                                    "adj_r2": np.nan,
                                    "error": str(exc),
                                }
                            )
    return pd.DataFrame(rows)


__all__ = ["apply_winsorization", "run_robustness_grid"]
