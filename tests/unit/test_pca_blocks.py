from __future__ import annotations

import numpy as np
import pandas as pd

from cqresearch.modeling.pca_blocks import (
    fit_block_pca,
    make_pca_factor_panel,
    pca_block_summary,
)


def test_block_pca_skips_single_variable_blocks() -> None:
    idx = pd.date_range("2024-01-01", periods=80)
    df = pd.DataFrame(
        {
            "x1": np.linspace(-2, 2, len(idx)),
            "x2": np.sin(np.arange(len(idx))),
            "single": np.cos(np.arange(len(idx))),
        },
        index=idx,
    )

    fitted = fit_block_pca(df, {"TwoVar": ["x1", "x2"], "Single": ["single"]})

    assert "TwoVar" in fitted
    assert "Single" not in fitted
    assert fitted["TwoVar"].pca.n_components_ == 2


def test_pca_factor_panel_and_summary_have_expected_columns() -> None:
    idx = pd.date_range("2024-01-01", periods=80)
    df = pd.DataFrame(
        {
            "x1": np.linspace(-2, 2, len(idx)),
            "x2": np.sin(np.arange(len(idx))),
            "x3": np.cos(np.arange(len(idx))),
        },
        index=idx,
    )

    panel, fitted = make_pca_factor_panel(df, {"Block": ["x1", "x2", "x3"]}, n_components=2)
    loadings, variance = pca_block_summary(fitted)

    assert {"Block_pc1", "Block_pc2"}.issubset(panel.columns)
    assert {"block", "component", "feature", "loading"}.issubset(loadings.columns)
    assert variance["explained_variance_ratio"].between(0, 1).all()
