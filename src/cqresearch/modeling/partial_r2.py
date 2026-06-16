"""Full-vs-reduced block partial R^2 helpers.

These functions compare a full model with a reduced model that removes an
entire factor block:

``(RSS_reduced - RSS_full) / TSS``

That is useful for portfolio-grade block attribution, but it is not the same as
the existing rolling drop-one marginal R^2, not a Shapley/Owen fair allocation,
and not sequential R^2 from an ordered model build.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def safe_standardize(df: pd.DataFrame) -> pd.DataFrame:
    """Return z-scored numeric columns, leaving constant columns at zero.

    Missing values are preserved. Columns with zero or undefined standard
    deviation are centered and divided by one so they cannot create infinities.
    """

    out = df.copy()
    for col in out.columns:
        values = pd.to_numeric(out[col], errors="coerce")
        mean = values.mean()
        std = values.std()
        if not np.isfinite(std) or std == 0:
            std = 1.0
        out[col] = (values - mean) / std
    return out


def _design_matrix(x: pd.DataFrame, add_const: bool) -> np.ndarray:
    arr = x.to_numpy(dtype=float) if len(x.columns) else np.empty((len(x), 0))
    if add_const:
        return np.column_stack([np.ones(len(x)), arr])
    return arr


def fit_rss(y: pd.Series, x: pd.DataFrame, add_const: bool = True) -> float:
    """Fit OLS on aligned rows and return residual sum of squares.

    ``x`` may be empty, in which case this is an intercept-only model when
    ``add_const=True``.
    """

    y_name = "__y__"
    df = pd.concat([y.rename(y_name), x], axis=1).dropna()
    if df.empty:
        return float("nan")

    y_arr = df[y_name].to_numpy(dtype=float)
    x_arr = _design_matrix(df[list(x.columns)], add_const=add_const)
    beta, *_ = np.linalg.lstsq(x_arr, y_arr, rcond=None)
    resid = y_arr - x_arr @ beta
    return float(resid @ resid)


def _aligned_model_frames(
    y: pd.Series, x_full: pd.DataFrame, x_reduced: pd.DataFrame
) -> tuple[pd.Series, pd.DataFrame, pd.DataFrame]:
    """Align full and reduced models on one common non-missing row set."""

    y_name = "__y__"
    reduced_only = [c for c in x_reduced.columns if c not in x_full.columns]
    df = pd.concat([y.rename(y_name), x_full, x_reduced[reduced_only]], axis=1).dropna()
    return df[y_name], df[list(x_full.columns)], df[list(x_reduced.columns)]


def partial_r2_full_vs_reduced(
    y: pd.Series, x_full: pd.DataFrame, x_reduced: pd.DataFrame
) -> float:
    """Return full-vs-reduced block partial R^2 on a common sample.

    The statistic is ``(RSS_reduced - RSS_full) / TSS``. Tiny negative values
    from floating-point noise are clamped to zero. Material negative values are
    preserved because they usually signal rank or sample problems worth seeing.
    """

    yy, full, reduced = _aligned_model_frames(y, x_full, x_reduced)
    if yy.empty:
        return float("nan")
    tss = float(((yy - yy.mean()) ** 2).sum())
    if tss <= 0:
        return float("nan")

    rss_full = fit_rss(yy, full)
    rss_reduced = fit_rss(yy, reduced)
    value = (rss_reduced - rss_full) / tss
    if value < 0 and abs(value) < 1.0e-12:
        value = 0.0
    return float(value)


def block_partial_r2(
    y: pd.Series, x: pd.DataFrame, blocks: dict[str, list[str]]
) -> pd.DataFrame:
    """Compute full-vs-reduced block partial R^2 for each block.

    All available block variables are included in the full model. Each row then
    refits a reduced model that removes one block. The resulting contribution is
    not Shapley/Owen attribution and should not be labeled that way.
    """

    available_blocks = {
        block: [col for col in cols if col in x.columns]
        for block, cols in blocks.items()
    }
    all_cols = [
        col
        for cols in available_blocks.values()
        for col in cols
        if col in x.columns
    ]
    all_cols = list(dict.fromkeys(all_cols))
    x_full = x[all_cols]

    rows: list[dict[str, object]] = []
    for block, cols in available_blocks.items():
        reduced_cols = [col for col in all_cols if col not in cols]
        yy, full, reduced = _aligned_model_frames(y, x_full, x[reduced_cols])
        tss = float(((yy - yy.mean()) ** 2).sum()) if len(yy) else float("nan")
        rss_full = fit_rss(yy, full)
        rss_reduced = fit_rss(yy, reduced)
        partial = (rss_reduced - rss_full) / tss if tss > 0 else float("nan")
        if np.isfinite(partial) and partial < 0 and abs(partial) < 1.0e-12:
            partial = 0.0
        full_r2 = 1.0 - rss_full / tss if tss > 0 else float("nan")
        reduced_r2 = 1.0 - rss_reduced / tss if tss > 0 else float("nan")
        rows.append(
            {
                "block": block,
                "partial_r2": float(partial) if np.isfinite(partial) else np.nan,
                "full_r2": float(full_r2) if np.isfinite(full_r2) else np.nan,
                "reduced_r2": float(reduced_r2) if np.isfinite(reduced_r2) else np.nan,
                "n": len(yy),
                "n_vars": len(cols),
                "variables": ";".join(cols),
                "method": "full_vs_reduced_block_partial_r2_not_shapley",
            }
        )
    return pd.DataFrame(rows)


def rolling_block_partial_r2(
    y: pd.Series,
    x: pd.DataFrame,
    blocks: dict[str, list[str]],
    window: int = 180,
    min_periods: int | None = None,
) -> pd.DataFrame:
    """Rolling full-vs-reduced block partial R^2.

    Row ``date`` uses the trailing ``window`` observations ending on that date
    after alignment. Sparse windows below ``min_periods`` are skipped.
    """

    if min_periods is None:
        min_periods = window

    cols = list(dict.fromkeys(col for values in blocks.values() for col in values))
    cols = [col for col in cols if col in x.columns]
    df = pd.concat([y.rename("__y__"), x[cols]], axis=1).dropna()
    rows: list[pd.DataFrame] = []
    for end in range(window - 1, len(df)):
        chunk = df.iloc[end - window + 1 : end + 1]
        if len(chunk) < min_periods:
            continue
        out = block_partial_r2(chunk["__y__"], chunk[cols], blocks)
        if out.empty:
            continue
        out.insert(0, "date", df.index[end])
        out.insert(1, "window", window)
        rows.append(out)
    if not rows:
        return pd.DataFrame(
            columns=[
                "date",
                "window",
                "block",
                "partial_r2",
                "full_r2",
                "reduced_r2",
                "n",
                "n_vars",
                "variables",
                "method",
            ]
        )
    return pd.concat(rows, ignore_index=True)


__all__ = [
    "block_partial_r2",
    "fit_rss",
    "partial_r2_full_vs_reduced",
    "rolling_block_partial_r2",
    "safe_standardize",
]
