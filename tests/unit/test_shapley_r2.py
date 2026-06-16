from __future__ import annotations

import numpy as np
import pandas as pd

from cqresearch.modeling.shapley_r2 import (
    exact_block_shapley_r2,
    rolling_block_shapley_r2,
    validate_shapley_sum,
)


def test_exact_block_shapley_sums_to_full_r2() -> None:
    idx = pd.date_range("2024-01-01", periods=80)
    x1 = pd.Series(np.linspace(-2, 2, len(idx)), index=idx, name="x1")
    x2 = pd.Series(np.sin(np.arange(len(idx))), index=idx, name="x2")
    y = (1.5 * x1 + 0.1 * x2).rename("btc_ret")
    x = pd.concat([x1, x2], axis=1)

    out = exact_block_shapley_r2(y, x, {"Signal": ["x1"], "Small": ["x2"]})
    full_r2 = float(out["full_r2"].iloc[0])

    assert validate_shapley_sum(out, full_r2)
    assert float(out.loc[out["block"] == "Signal", "shapley_r2"].iloc[0]) > float(
        out.loc[out["block"] == "Small", "shapley_r2"].iloc[0]
    )


def test_rolling_block_shapley_uses_stepped_windows() -> None:
    idx = pd.date_range("2024-01-01", periods=80)
    x = pd.DataFrame(
        {
            "x1": np.linspace(-2, 2, len(idx)),
            "x2": np.sin(np.arange(len(idx))),
        },
        index=idx,
    )
    y = (x["x1"] + x["x2"]).rename("eth_ret")

    out = rolling_block_shapley_r2(
        y,
        x,
        {"A": ["x1"], "B": ["x2"]},
        window=30,
        step=10,
        min_periods=25,
    )

    assert not out.empty
    assert set(out["step"]) == {10}
    assert {"date", "window", "block", "shapley_r2"}.issubset(out.columns)
