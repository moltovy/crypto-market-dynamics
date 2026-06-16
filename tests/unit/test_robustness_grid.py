from __future__ import annotations

import numpy as np
import pandas as pd

from cqresearch.modeling.robustness_grid import apply_winsorization, run_robustness_grid


def test_robustness_grid_runs_requested_cells() -> None:
    idx = pd.date_range("2024-01-01", periods=120)
    x1 = np.linspace(-1, 1, len(idx))
    x2 = np.sin(np.arange(len(idx)))
    feat = pd.DataFrame(
        {
            "btc_ret": 0.4 * x1 + 0.1 * x2,
            "x1": x1,
            "btc_mvrv_d1": x2,
        },
        index=idx,
    )

    out = run_robustness_grid(
        feat,
        "btc_ret",
        ["x1", "btc_mvrv_d1"],
        windows=(60,),
        hac_lags=(2,),
        winsorization=(None,),
        include_mvrv=(True, False),
        calendars=("crypto7", "weekday"),
    )

    assert len(out) == 4
    assert out["error"].fillna("").eq("").all()


def test_apply_winsorization_preserves_shape() -> None:
    df = pd.DataFrame({"x": [1.0, 2.0, 100.0], "label": ["a", "b", "c"]})

    out = apply_winsorization(df, 0.1)

    assert out.shape == df.shape
    assert out["label"].equals(df["label"])
