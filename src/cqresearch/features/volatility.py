"""Realized-volatility feature helpers."""
from __future__ import annotations

import numpy as np
import pandas as pd


def realized_vol(
    ret: pd.Series, window: int = 30, annualization: int = 365
) -> pd.Series:
    """Return rolling annualized realized volatility from log returns."""

    return ret.rolling(window=window, min_periods=window).std() * np.sqrt(annualization)


def add_realized_vol_features(feat: pd.DataFrame) -> pd.DataFrame:
    """Add 30-day annualized realized-volatility columns when returns exist."""

    out = feat.copy()
    for asset in ("btc", "eth", "spy"):
        ret_col = f"{asset}_ret"
        if ret_col in out.columns:
            annualization = 365 if asset in {"btc", "eth"} else 252
            out[f"{asset}_rv_30d"] = realized_vol(
                out[ret_col],
                window=30,
                annualization=annualization,
            )
    return out


__all__ = ["add_realized_vol_features", "realized_vol"]
