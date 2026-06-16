"""PCA factor-block utilities for advanced portfolio diagnostics."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.decomposition import PCA


@dataclass
class PCABlockFit:
    block: str
    columns: list[str]
    mean: pd.Series
    scale: pd.Series
    pca: PCA


def _standardized(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    mean = df.mean()
    scale = df.std().replace(0, 1).fillna(1)
    return (df - mean) / scale, mean, scale


def fit_block_pca(
    df: pd.DataFrame,
    blocks: dict[str, list[str]],
    n_components: int = 2,
    standardize: bool = True,
) -> dict[str, PCABlockFit]:
    """Fit PCA independently for each available factor block.

    Blocks with fewer than two usable variables are skipped because PCA would be
    a relabeling rather than a dimension-reduction method.
    """

    fitted: dict[str, PCABlockFit] = {}
    for block, cols in blocks.items():
        cols_here = [col for col in cols if col in df.columns]
        block_df = df[cols_here].dropna()
        if len(cols_here) < 2 or len(block_df) < 30:
            continue
        if standardize:
            x, mean, scale = _standardized(block_df)
        else:
            x = block_df
            mean = pd.Series(0.0, index=cols_here)
            scale = pd.Series(1.0, index=cols_here)
        k = min(n_components, len(cols_here), len(block_df))
        pca = PCA(n_components=k)
        pca.fit(x)
        fitted[block] = PCABlockFit(block, cols_here, mean, scale, pca)
    return fitted


def transform_block_pca(df: pd.DataFrame, fitted: dict[str, PCABlockFit]) -> pd.DataFrame:
    """Transform ``df`` into PCA component columns using fitted block models."""

    out = pd.DataFrame(index=df.index)
    for block, fit in fitted.items():
        x = df[fit.columns].copy()
        x = (x - fit.mean) / fit.scale
        clean = x.dropna()
        scores = fit.pca.transform(clean)
        for i in range(scores.shape[1]):
            out.loc[clean.index, f"{block}_pc{i + 1}"] = scores[:, i]
    return out


def make_pca_factor_panel(
    feat: pd.DataFrame, blocks: dict[str, list[str]], n_components: int = 2
) -> tuple[pd.DataFrame, dict[str, PCABlockFit]]:
    """Fit block PCA and return component scores plus fitted models."""

    fitted = fit_block_pca(feat, blocks, n_components=n_components, standardize=True)
    return transform_block_pca(feat, fitted), fitted


def pca_block_summary(fitted: dict[str, PCABlockFit]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return loadings and explained-variance summary tables."""

    loading_rows: list[dict[str, object]] = []
    variance_rows: list[dict[str, object]] = []
    for block, fit in fitted.items():
        for component_idx, component in enumerate(fit.pca.components_, start=1):
            variance_rows.append(
                {
                    "block": block,
                    "component": component_idx,
                    "explained_variance_ratio": float(
                        fit.pca.explained_variance_ratio_[component_idx - 1]
                    ),
                    "n_variables": len(fit.columns),
                }
            )
            for col, loading in zip(fit.columns, component, strict=False):
                loading_rows.append(
                    {
                        "block": block,
                        "component": component_idx,
                        "feature": col,
                        "loading": float(loading),
                    }
                )
    return pd.DataFrame(loading_rows), pd.DataFrame(variance_rows)


__all__ = [
    "PCABlockFit",
    "fit_block_pca",
    "make_pca_factor_panel",
    "pca_block_summary",
    "transform_block_pca",
]
