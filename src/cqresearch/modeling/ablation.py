"""Nested OLS ablation helpers for BTC/ETH factor stacks."""
from __future__ import annotations

import numpy as np
import pandas as pd

MACRO = ["DGS10_d1", "DGS2_d1", "VIXCLS_d1", "DTWEXBGS_d1", "DFF_d1"]
TRADFI = ["spy_ret", "qqq_ret", "gld_ret"]
LIQUIDITY = ["defi_tvl_usd_ret", "stables_total_usd_ret"]
SENTIMENT = ["fng_value_d1"]
BTC_NATIVE_EX_MVRV = [
    "cme_btc_basis_close_d1",
    "btc_exchange_netflow_d1",
    "btc_miner_to_exchange_flow_d1",
]
BTC_MVRV = ["btc_mvrv_d1"]
ETH_NATIVE = ["cme_eth_basis_close_d1"]
BTC_ETF = ["btc_etf_intensity"]
ETH_ETF = ["eth_etf_intensity"]


def _available(cols: list[str], feat: pd.DataFrame) -> list[str]:
    return [col for col in cols if col in feat.columns]


def _ols_stats(y: pd.Series, x: pd.DataFrame) -> tuple[int, float, float]:
    y_name = "__y__"
    df = pd.concat([y.rename(y_name), x], axis=1).dropna()
    n = len(df)
    if n == 0:
        return 0, float("nan"), float("nan")

    y_arr = df[y_name].to_numpy(dtype=float)
    x_arr = (
        df[list(x.columns)].to_numpy(dtype=float)
        if len(x.columns)
        else np.empty((n, 0), dtype=float)
    )
    design = np.column_stack([np.ones(n), x_arr])
    beta, *_ = np.linalg.lstsq(design, y_arr, rcond=None)
    resid = y_arr - design @ beta
    rss = float(resid @ resid)
    tss = float(((y_arr - y_arr.mean()) ** 2).sum())
    if tss <= 0:
        return n, float("nan"), float("nan")
    r2 = 1.0 - rss / tss
    p = len(x.columns)
    adj = 1.0 - (1.0 - r2) * (n - 1) / (n - p - 1) if n > p + 1 else np.nan
    return n, float(r2), float(adj)


def run_nested_ablation(
    y: pd.Series, feature_df: pd.DataFrame, specs: list[tuple[str, list[str]]]
) -> pd.DataFrame:
    """Run nested in-sample OLS ablations.

    The function reports variable availability and sample size for every model.
    R^2 is nondecreasing when added variables are evaluated on the same row set;
    ETF-intensity additions can change support if callers include pre-launch
    rows, so the output includes ``n`` and ``note`` for auditability.
    """

    asset = str(y.name).replace("_ret", "") if y.name else "unknown"
    sample = str(y.attrs.get("sample", "full"))
    rows: list[dict[str, object]] = []
    prev_r2: float | None = None

    for model_id, requested in specs:
        variables = _available(requested, feature_df)
        missing = [col for col in requested if col not in feature_df.columns]
        n, r2, adj_r2 = _ols_stats(y, feature_df[variables])
        delta = np.nan if prev_r2 is None or not np.isfinite(r2) else r2 - prev_r2
        note_parts = []
        if missing:
            note_parts.append(f"skipped_missing={';'.join(missing)}")
        if "etf" in model_id.lower():
            note_parts.append("ETF intensity is only interpretable on post-launch support")
        rows.append(
            {
                "model_id": model_id,
                "asset": asset,
                "sample": sample,
                "n": int(n),
                "r2": r2,
                "adj_r2": adj_r2,
                "delta_r2_vs_prev": delta,
                "variables": ";".join(variables),
                "missing_variables": ";".join(missing),
                "note": "; ".join(note_parts) if note_parts else "ok",
            }
        )
        if np.isfinite(r2):
            prev_r2 = r2
    return pd.DataFrame(rows)


def make_default_btc_ablation_specs(feat: pd.DataFrame) -> list[tuple[str, list[str]]]:
    """Return cumulative BTC ablation specs using columns available in ``feat``."""

    del feat
    m1 = MACRO
    m2 = m1 + TRADFI
    m3 = m2 + LIQUIDITY
    m4 = m3 + SENTIMENT
    m5 = m4 + BTC_NATIVE_EX_MVRV
    m6 = m5 + BTC_MVRV
    m7 = m6 + BTC_ETF
    return [
        ("M0_intercept", []),
        ("M1_macro", m1),
        ("M2_macro_tradfi", m2),
        ("M3_macro_tradfi_liquidity", m3),
        ("M4_plus_sentiment", m4),
        ("M5_plus_native_ex_mvrv", m5),
        ("M6_plus_mvrv", m6),
        ("M7_plus_etf_intensity_post_launch", m7),
    ]


def make_default_eth_ablation_specs(feat: pd.DataFrame) -> list[tuple[str, list[str]]]:
    """Return cumulative ETH ablation specs using columns available in ``feat``."""

    del feat
    m1 = MACRO
    m2 = m1 + TRADFI
    m3 = m2 + LIQUIDITY
    m4 = m3 + SENTIMENT
    m5 = m4 + ETH_NATIVE
    m6 = m5 + ETH_ETF
    return [
        ("M0_intercept", []),
        ("M1_macro", m1),
        ("M2_macro_tradfi", m2),
        ("M3_macro_tradfi_liquidity", m3),
        ("M4_plus_sentiment", m4),
        ("M5_plus_eth_native", m5),
        ("M6_plus_eth_etf_intensity_post_launch", m6),
    ]


__all__ = [
    "BTC_MVRV",
    "BTC_NATIVE_EX_MVRV",
    "ETH_NATIVE",
    "LIQUIDITY",
    "MACRO",
    "SENTIMENT",
    "TRADFI",
    "make_default_btc_ablation_specs",
    "make_default_eth_ablation_specs",
    "run_nested_ablation",
]
