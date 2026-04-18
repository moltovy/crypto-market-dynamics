"""Derive the **feature panel** used by every model.

Given the master daily panel, we:

* Compute log returns on *price-like* variables (BTC, ETH, SPY, QQQ, GLD, XLK,
  DXY, CME basis, DVOL, TVL, stablecoin total).
* Compute first differences on rate/yield-type variables (FRED rates, FNG).
* Scale ETF flows by prior-day BTC (resp. ETH) market cap to produce a
  stationary "flow intensity" regressor.
* Drop obvious non-stationary levels from downstream modeling.

All features are named with a clear suffix (``_ret``, ``_d1``, ``_intensity``)
so regression specs cannot accidentally mix levels and returns.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from cqresearch.features.returns import first_diff, log_return


PRICE_COLS = [
    "btc_close", "eth_close",
    "spy_close", "qqq_close", "gld_close", "xlk_close",
    "dxy_tv_close",
    "defi_tvl_usd", "stables_total_usd",
]

# Basis / implied-vol levels — use log-return of (1 + x/100) or first diff.
# We use first difference for basis and DVOL since they are already spreads / vol levels.
DIFF_COLS = [
    # Macro rate levels (percentage points → first difference in pp)
    "DGS10", "DGS2", "DGS30", "DFII10", "T10Y2Y", "SOFR", "DFF",
    "BAMLH0A0HYM2", "VIXCLS", "RRPONTSYD", "DTWEXBGS", "USEPUINDXD",
    # Vol / basis
    "dvol_btc_close", "cme_btc_basis_close", "cme_eth_basis_close",
    # Sentiment (0-100 index)
    "fng_value",
]


def build_feature_panel(panel: pd.DataFrame) -> pd.DataFrame:
    """Return a feature DataFrame with the same index as ``panel``."""

    feat = pd.DataFrame(index=panel.index)

    # Log returns
    for c in PRICE_COLS:
        if c in panel.columns:
            r = log_return(panel[c])
            feat[f"{c.replace('_close','')}_ret"] = r

    # First differences
    for c in DIFF_COLS:
        if c in panel.columns:
            feat[f"{c}_d1"] = first_diff(panel[c])

    # Oil — use log return
    if "DCOILWTICO" in panel.columns:
        feat["wti_ret"] = log_return(panel["DCOILWTICO"])

    # ETF flow intensity = flow_t / (market_cap_{t-1})
    # market cap ≈ close × circulating supply. We don't have circulating in the
    # panel, so we use prior-day *close* as a scaling proxy — this is a
    # **flow-per-unit-price** regressor (flow_$USD_M / price). It's stationary
    # even if price drifts.
    if "btc_etf_total" in panel.columns and "btc_close" in panel.columns:
        feat["btc_etf_intensity"] = panel["btc_etf_total"] / panel["btc_close"].shift(1)
    if "eth_etf_total" in panel.columns and "eth_close" in panel.columns:
        feat["eth_etf_intensity"] = panel["eth_etf_total"] / panel["eth_close"].shift(1)

    return feat


__all__ = ["build_feature_panel", "PRICE_COLS", "DIFF_COLS"]
