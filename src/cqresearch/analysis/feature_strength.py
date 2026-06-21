"""Feature-strength metrics engine for Crypto Market Dynamics.

Computes per-feature and per-block diagnostics across regimes and model
families. All multivariate inference uses HAC standard errors via the existing
``cqresearch.modeling.ols`` module. Drop-one ΔR² uses the existing
``cqresearch.modeling.partial_r2`` infrastructure.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from cqresearch.modeling.ols import fit_ols
from cqresearch.modeling.partial_r2 import (
    block_partial_r2,
    safe_standardize,
)

# ── Feature dictionary helpers ──────────────────────────────────────────────

BLOCK_MAP: dict[str, str] = {
    # Target returns
    "btc_ret": "Target",
    "eth_ret": "Target",
    # Macro
    "DGS10_d1": "Macro",
    "DGS2_d1": "Macro",
    "VIXCLS_d1": "Macro",
    "DTWEXBGS_d1": "Macro",
    "DFF_d1": "Macro",
    # TradFi
    "spy_ret": "TradFi",
    "qqq_ret": "TradFi",
    "gld_ret": "TradFi",
    # Liquidity
    "defi_tvl_usd_ret": "Liquidity",
    "stables_total_usd_ret": "Liquidity",
    # Sentiment
    "fng_value_d1": "Sentiment",
    # BTC native valuation
    "btc_mvrv_d1": "BTC Native Valuation",
    # BTC native flow
    "cme_btc_basis_close_d1": "BTC Native Flow",
    "btc_exchange_netflow_d1": "BTC Native Flow",
    "btc_miner_to_exchange_flow_d1": "BTC Native Flow",
    # ETH native
    "cme_eth_basis_close_d1": "ETH Native",
    # ETF flow
    "btc_etf_intensity": "ETF Flow",
    "eth_etf_intensity": "ETF Flow",
}

TRANSFORM_MAP: dict[str, str] = {
    "btc_ret": "log return",
    "eth_ret": "log return",
    "spy_ret": "log return",
    "qqq_ret": "log return",
    "gld_ret": "log return",
    "defi_tvl_usd_ret": "log return",
    "stables_total_usd_ret": "log return",
    "DGS10_d1": "first difference",
    "DGS2_d1": "first difference",
    "VIXCLS_d1": "first difference",
    "DTWEXBGS_d1": "first difference",
    "DFF_d1": "first difference",
    "fng_value_d1": "first difference",
    "btc_mvrv_d1": "first difference",
    "cme_btc_basis_close_d1": "first difference",
    "btc_exchange_netflow_d1": "first difference",
    "btc_miner_to_exchange_flow_d1": "first difference",
    "cme_eth_basis_close_d1": "first difference",
    "btc_etf_intensity": "flow / prior mcap",
    "eth_etf_intensity": "flow / prior mcap",
}

INTERPRETATION_RISK: dict[str, str] = {
    "btc_mvrv_d1": "high — near-price valuation state, corr ≈ 0.955 with btc_ret",
    "btc_etf_intensity": "medium — simultaneity with daily returns",
    "eth_etf_intensity": "medium — simultaneity with daily returns",
    "stables_total_usd_ret": "low — proxy, not identified shock",
    "defi_tvl_usd_ret": "low — proxy, not identified shock",
}


def build_factor_dictionary(features: list[str]) -> pd.DataFrame:
    """Build a factor dictionary table for the given feature list."""

    rows = []
    for feat in features:
        block = BLOCK_MAP.get(feat, "Unknown")
        rows.append(
            {
                "feature": feat,
                "clean_label": feat.replace("_d1", " Δ")
                .replace("_ret", " return")
                .replace("_", " ")
                .title(),
                "block": block,
                "transformation": TRANSFORM_MAP.get(feat, "unknown"),
                "role": "target" if block == "Target" else "explanatory",
                "use_in_full_model": block != "Target",
                "use_in_ex_mvrv_model": block not in ("Target", "BTC Native Valuation"),
                "interpretation_risk": INTERPRETATION_RISK.get(feat, "low"),
            }
        )
    return pd.DataFrame(rows)


# ── Feature strength computation ─────────────────────────────────────────────

MIN_OBS = 30  # Minimum observations for regression


def compute_feature_strength(
    feat_df: pd.DataFrame,
    target: str,
    features: list[str],
    regime_mask: pd.Series | None = None,
    model_family: str = "full",
    hac_lags: int = 5,
) -> pd.DataFrame:
    """Compute per-feature strength metrics on same-support within regime.

    Returns a DataFrame with one row per feature containing correlation,
    univariate regression stats, multivariate regression stats, and
    drop-one ΔR².
    """

    available = [f for f in features if f in feat_df.columns]
    if not available:
        return pd.DataFrame()

    df = feat_df[[target, *available]].copy()
    if regime_mask is not None:
        df = df.loc[regime_mask.reindex(df.index, fill_value=False)]

    # Same-support: drop all rows with any NaN across target + all features
    df_clean = df.dropna()
    n_total = len(df_clean)

    if n_total < MIN_OBS:
        rows = []
        for feat in available:
            rows.append(
                {
                    "feature": feat,
                    "block": BLOCK_MAP.get(feat, "Unknown"),
                    "model_family": model_family,
                    "n": n_total,
                    "note": "insufficient_obs",
                }
            )
        return pd.DataFrame(rows)

    y = df_clean[target]
    x_feats = df_clean[available]

    # Standardize for multivariate standardized betas
    x_std_feats = safe_standardize(x_feats)
    y_std = (y - y.mean()) / (y.std() if y.std() > 0 else 1.0)

    # Multivariate fit (standardized)
    try:
        multi_res = fit_ols(y_std, x_std_feats, hac_lags=hac_lags, label="multivar_std")
        multi_params = multi_res.params
        multi_tvals = multi_res.tvals
        multi_pvals = multi_res.pvals
        multi_r2 = multi_res.r2
    except Exception:
        multi_params = pd.Series(dtype=float)
        multi_tvals = pd.Series(dtype=float)
        multi_pvals = pd.Series(dtype=float)
        multi_r2 = np.nan

    rows = []
    for feat in available:
        # Correlation
        corr = float(y.corr(x_feats[feat]))

        # Univariate regression
        try:
            uni_res = fit_ols(y, x_feats[[feat]], hac_lags=hac_lags, label="univar")
            uni_beta = float(uni_res.params.get(feat, np.nan))
            uni_t = float(uni_res.tvals.get(feat, np.nan))
            uni_r2 = uni_res.r2
        except Exception:
            uni_beta = np.nan
            uni_t = np.nan
            uni_r2 = np.nan

        # Multivariate stats
        std_beta = float(multi_params.get(feat, np.nan))
        multi_t = float(multi_tvals.get(feat, np.nan))
        multi_p = float(multi_pvals.get(feat, np.nan))

        # Drop-one ΔR²: fit full model, then fit without this feature
        try:
            reduced_features = [f for f in available if f != feat]
            if reduced_features:
                full_res = fit_ols(y, x_feats, hac_lags=hac_lags, label="full")
                reduced_res = fit_ols(
                    y, x_feats[reduced_features], hac_lags=hac_lags, label="reduced"
                )
                drop_one = full_res.r2 - reduced_res.r2
            else:
                drop_one = uni_r2 if np.isfinite(uni_r2) else np.nan
        except Exception:
            drop_one = np.nan

        rows.append(
            {
                "feature": feat,
                "block": BLOCK_MAP.get(feat, "Unknown"),
                "model_family": model_family,
                "n": n_total,
                "missing_pct": round(1.0 - n_total / max(len(df), 1), 4),
                "correlation": round(corr, 6),
                "abs_correlation": round(abs(corr), 6),
                "univariate_beta": round(uni_beta, 6) if np.isfinite(uni_beta) else np.nan,
                "univariate_hac_t": round(uni_t, 4) if np.isfinite(uni_t) else np.nan,
                "univariate_r2": round(uni_r2, 6) if np.isfinite(uni_r2) else np.nan,
                "standardized_multivar_beta": round(std_beta, 6)
                if np.isfinite(std_beta)
                else np.nan,
                "multivar_hac_t": round(multi_t, 4) if np.isfinite(multi_t) else np.nan,
                "multivar_p": round(multi_p, 6) if np.isfinite(multi_p) else np.nan,
                "multivar_r2": round(multi_r2, 6) if np.isfinite(multi_r2) else np.nan,
                "drop_one_delta_r2": round(drop_one, 6) if np.isfinite(drop_one) else np.nan,
                "note": "ok",
            }
        )

    result = pd.DataFrame(rows)
    # Add ranks
    if not result.empty:
        result["rank_by_abs_corr"] = (
            result["abs_correlation"].rank(ascending=False, method="min").astype("Int64")
        )
        result["rank_by_abs_t"] = (
            result["multivar_hac_t"]
            .abs()
            .rank(ascending=False, method="min", na_option="bottom")
            .astype("Int64")
        )
        result["rank_by_delta_r2"] = (
            result["drop_one_delta_r2"]
            .rank(ascending=False, method="min", na_option="bottom")
            .astype("Int64")
        )

    return result


# ── Block strength ───────────────────────────────────────────────────────────


def compute_block_strength(
    feat_df: pd.DataFrame,
    target: str,
    blocks: dict[str, list[str]],
    regime_mask: pd.Series | None = None,
    regime_name: str = "full",
) -> pd.DataFrame:
    """Compute block-level R² / ΔR² for a given regime.

    Wraps the existing ``block_partial_r2`` function with regime filtering.
    """

    df = feat_df.copy()
    if regime_mask is not None:
        df = df.loc[regime_mask.reindex(df.index, fill_value=False)]

    y = df[target].dropna()
    x_df = df.drop(columns=[target], errors="ignore")

    result = block_partial_r2(y, x_df, blocks)
    result.insert(0, "regime", regime_name)
    result.insert(1, "target", target)
    return result


# ── Same-support ablation ────────────────────────────────────────────────────


def compute_same_support_ablation(
    feat_df: pd.DataFrame,
    target: str,
    model_specs: list[tuple[str, list[str]]],
    regime_mask: pd.Series | None = None,
    regime_name: str = "full",
    hac_lags: int = 5,
) -> pd.DataFrame:
    """Run nested ablation where all models use the same set of non-missing rows.

    Unlike the existing ``run_nested_ablation``, this function first computes
    the intersection of rows where *all* features across *all* specs are
    non-missing, then fits every model on that identical sample.
    """

    df = feat_df.copy()
    if regime_mask is not None:
        df = df.loc[regime_mask.reindex(df.index, fill_value=False)]

    # Collect all features across all specs
    all_features: list[str] = []
    for _, features in model_specs:
        for f in features:
            if f in df.columns and f not in all_features:
                all_features.append(f)

    # Same-support: rows where target + all features are non-missing
    cols_needed = [target, *all_features]
    cols_available = [c for c in cols_needed if c in df.columns]
    df_clean = df[cols_available].dropna()
    n = len(df_clean)

    if n < MIN_OBS:
        return pd.DataFrame(
            [
                {
                    "model_id": spec_id,
                    "regime": regime_name,
                    "target": target,
                    "n": n,
                    "r2": np.nan,
                    "adj_r2": np.nan,
                    "delta_r2_vs_prev": np.nan,
                    "variables": ";".join(feats),
                    "note": "insufficient_obs",
                }
                for spec_id, feats in model_specs
            ]
        )

    y = df_clean[target]
    rows = []
    prev_r2: float | None = None

    for model_id, requested_features in model_specs:
        available = [f for f in requested_features if f in df_clean.columns]
        if not available:
            # Intercept-only model
            r2 = 0.0
            adj_r2 = 0.0
        else:
            try:
                res = fit_ols(y, df_clean[available], hac_lags=hac_lags, label=model_id)
                r2 = res.r2
                adj_r2 = res.adj_r2
            except Exception:
                r2 = np.nan
                adj_r2 = np.nan

        delta = np.nan if prev_r2 is None or not np.isfinite(r2) else r2 - prev_r2

        rows.append(
            {
                "model_id": model_id,
                "regime": regime_name,
                "target": target,
                "n": n,
                "r2": round(r2, 6) if np.isfinite(r2) else np.nan,
                "adj_r2": round(adj_r2, 6) if np.isfinite(adj_r2) else np.nan,
                "delta_r2_vs_prev": round(delta, 6) if np.isfinite(delta) else np.nan,
                "variables": ";".join(available),
                "note": "same_support",
            }
        )
        if np.isfinite(r2):
            prev_r2 = r2

    return pd.DataFrame(rows)


# ── Rolling feature rank stability ───────────────────────────────────────────


def compute_rolling_feature_rank(
    feat_df: pd.DataFrame,
    target: str,
    features: list[str],
    window: int = 180,
    step: int = 30,
) -> pd.DataFrame:
    """Compute rolling-window feature rankings by absolute correlation.

    Returns a long DataFrame with columns: date, feature, abs_correlation, rank.
    """

    available = [f for f in features if f in feat_df.columns]
    df = feat_df[[target, *available]].dropna()

    rows = []
    dates = df.index[window - 1 :: step]

    for end_date in dates:
        end_idx = df.index.get_loc(end_date)
        if isinstance(end_idx, slice):
            end_idx = end_idx.stop - 1
        start_idx = max(0, end_idx - window + 1)
        chunk = df.iloc[start_idx : end_idx + 1]

        if len(chunk) < MIN_OBS:
            continue

        y_chunk = chunk[target]
        for feat in available:
            corr = float(y_chunk.corr(chunk[feat]))
            rows.append(
                {
                    "date": end_date,
                    "feature": feat,
                    "correlation": round(corr, 6),
                    "abs_correlation": round(abs(corr), 6),
                }
            )

    result = pd.DataFrame(rows)
    if not result.empty:
        result["rank"] = (
            result.groupby("date")["abs_correlation"]
            .rank(ascending=False, method="min")
            .astype("Int64")
        )
    return result


# ── Correlation matrices ─────────────────────────────────────────────────────


def compute_core_correlation_matrix(feat_df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    """Compute pairwise correlation matrix for core features."""

    available = [f for f in features if f in feat_df.columns]
    return feat_df[available].corr().round(4)


def compute_pre_post_correlation_delta(
    feat_df: pd.DataFrame,
    pairs: list[tuple[str, str]],
    breakpoint: pd.Timestamp,
) -> pd.DataFrame:
    """Compute pre/post breakpoint correlation deltas for specified pairs."""

    pre = feat_df.loc[feat_df.index < breakpoint]
    post = feat_df.loc[feat_df.index >= breakpoint]

    rows = []
    for lhs, rhs in pairs:
        if lhs not in feat_df.columns or rhs not in feat_df.columns:
            continue
        pre_corr = float(pre[[lhs, rhs]].dropna().corr().iloc[0, 1])
        post_corr = float(post[[lhs, rhs]].dropna().corr().iloc[0, 1])
        rows.append(
            {
                "lhs": lhs,
                "rhs": rhs,
                "pre_corr": round(pre_corr, 4),
                "post_corr": round(post_corr, 4),
                "delta": round(post_corr - pre_corr, 4),
            }
        )
    return pd.DataFrame(rows)


__all__ = [
    "BLOCK_MAP",
    "build_factor_dictionary",
    "compute_block_strength",
    "compute_core_correlation_matrix",
    "compute_feature_strength",
    "compute_pre_post_correlation_delta",
    "compute_rolling_feature_rank",
    "compute_same_support_ablation",
]
