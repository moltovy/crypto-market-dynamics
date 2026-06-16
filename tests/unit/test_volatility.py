from __future__ import annotations

import numpy as np
import pandas as pd

from cqresearch.features.volatility import add_realized_vol_features, realized_vol


def test_realized_vol_uses_window_and_annualization() -> None:
    idx = pd.date_range("2024-01-01", periods=6)
    ret = pd.Series([0.0, 0.01, -0.01, 0.02, -0.02, 0.01], index=idx)

    out = realized_vol(ret, window=3, annualization=365)
    expected = ret.iloc[:3].std() * np.sqrt(365)

    assert pd.isna(out.iloc[1])
    assert np.isclose(out.iloc[2], expected)


def test_add_realized_vol_features_adds_available_assets() -> None:
    idx = pd.date_range("2024-01-01", periods=40)
    feat = pd.DataFrame(
        {
            "btc_ret": np.linspace(-0.01, 0.01, len(idx)),
            "eth_ret": np.linspace(0.02, -0.02, len(idx)),
        },
        index=idx,
    )

    out = add_realized_vol_features(feat)

    assert "btc_rv_30d" in out.columns
    assert "eth_rv_30d" in out.columns
    assert out["btc_rv_30d"].notna().sum() == 11
