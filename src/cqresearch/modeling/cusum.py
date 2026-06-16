"""CUSUM-style regime diagnostics."""
from __future__ import annotations

import numpy as np
import pandas as pd


def cusum_recursive_residuals(y: pd.Series, x: pd.DataFrame) -> pd.DataFrame:
    """Return an exploratory standardized residual CUSUM series.

    This is a regime diagnostic rather than a formal Bai-Perron multi-break
    estimator. It uses full-sample OLS residuals and standardizes the cumulative
    residual path by residual volatility.
    """

    frame = pd.concat([y.rename("__y__"), x], axis=1).dropna()
    if frame.empty:
        return pd.DataFrame(columns=["date", "cusum"])
    design = np.column_stack([np.ones(len(frame)), frame[list(x.columns)].to_numpy(float)])
    y_arr = frame["__y__"].to_numpy(float)
    beta, *_ = np.linalg.lstsq(design, y_arr, rcond=None)
    resid = y_arr - design @ beta
    sigma = float(np.std(resid, ddof=max(1, design.shape[1])))
    if sigma == 0 or not np.isfinite(sigma):
        sigma = 1.0
    cusum = np.cumsum(resid) / (sigma * np.sqrt(len(resid)))
    return pd.DataFrame({"date": frame.index, "cusum": cusum})


def cusum_bounds(n: int, alpha: float = 0.05) -> float:
    """Return a simple two-sided Brownian-bridge-style visual boundary."""

    del n
    return 1.36 if alpha == 0.05 else 1.63


def cusum_summary(y: pd.Series, x: pd.DataFrame) -> dict[str, object]:
    """Summarize maximum absolute CUSUM and boundary crossing status."""

    path = cusum_recursive_residuals(y, x)
    if path.empty:
        return {"n": 0, "max_abs_cusum": np.nan, "bound_5pct": np.nan, "crossed_5pct": False}
    bound = cusum_bounds(len(path), alpha=0.05)
    max_abs = float(path["cusum"].abs().max())
    return {
        "n": len(path),
        "max_abs_cusum": max_abs,
        "bound_5pct": bound,
        "crossed_5pct": bool(max_abs > bound),
        "method": "exploratory_standardized_residual_cusum",
    }


__all__ = ["cusum_bounds", "cusum_recursive_residuals", "cusum_summary"]
