from __future__ import annotations

import numpy as np
import pandas as pd

from cqresearch.modeling.lead_lag import (
    LAG_CONVENTION,
    flow_quintile_summary,
    lead_lag_regression_grid,
    make_lagged_frame,
)


def test_make_lagged_frame_negative_lag_means_x_leads() -> None:
    idx = pd.date_range("2024-01-01", periods=5)
    x = pd.Series([10, 20, 30, 40, 50], index=idx, name="flow")
    y = pd.Series(range(5), index=idx, name="btc_ret")

    frame = make_lagged_frame(y, x, range(-1, 2))

    assert frame.loc[idx[1], "flow_lag_-1"] == 10
    assert frame.loc[idx[1], "flow_lag_1"] == 30


def test_regression_grid_returns_one_row_per_lag_and_controls() -> None:
    idx = pd.date_range("2024-01-01", periods=90)
    x = pd.Series(np.linspace(0, 1, len(idx)), index=idx, name="flow")
    y = (x.shift(1).fillna(0) * 0.5).rename("btc_ret")
    controls = pd.DataFrame({"spy_ret": np.sin(np.arange(len(idx)))}, index=idx)

    out = lead_lag_regression_grid(y, x, controls, lags=range(-2, 3))

    assert len(out) == 5
    assert set(out["lag"]) == {-2, -1, 0, 1, 2}
    assert out["controls"].eq("spy_ret").all()
    assert out["lag_convention"].eq(LAG_CONVENTION).all()


def test_small_sample_is_reported_not_crashed() -> None:
    idx = pd.date_range("2024-01-01", periods=5)
    y = pd.Series(range(5), index=idx, name="btc_ret")
    x = pd.Series(range(5), index=idx, name="flow")

    out = lead_lag_regression_grid(y, x, None, lags=range(-1, 2))

    assert len(out) == 3
    assert out["note"].eq("insufficient_sample").all()


def test_flow_quintile_summary_has_requested_horizons() -> None:
    idx = pd.date_range("2024-01-01", periods=100)
    flow = pd.Series(np.linspace(-1, 1, len(idx)), index=idx, name="flow")
    ret = pd.Series(np.linspace(0.01, 0.02, len(idx)), index=idx, name="btc_ret")

    out = flow_quintile_summary(ret, flow, horizons=(0, 3))

    assert set(out["horizon"]) == {0, 3}
    assert set(out["quintile"]) == {1, 2, 3, 4, 5}
