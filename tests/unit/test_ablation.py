from __future__ import annotations

import numpy as np
import pandas as pd

from cqresearch.modeling.ablation import run_nested_ablation


def test_nested_ablation_r2_is_nondecreasing_on_common_support() -> None:
    idx = pd.date_range("2024-01-01", periods=80)
    x1 = pd.Series(np.linspace(-1, 1, len(idx)), index=idx, name="x1")
    x2 = pd.Series(np.cos(np.arange(len(idx))), index=idx, name="x2")
    y = (x1 + 0.5 * x2).rename("btc_ret")
    feat = pd.concat([x1, x2], axis=1)

    out = run_nested_ablation(
        y,
        feat,
        [
            ("M0_intercept", []),
            ("M1_x1", ["x1"]),
            ("M2_x1_x2", ["x1", "x2"]),
        ],
    )

    assert out["r2"].is_monotonic_increasing
    assert np.isclose(
        out.loc[2, "delta_r2_vs_prev"],
        out.loc[2, "r2"] - out.loc[1, "r2"],
    )


def test_nested_ablation_skips_missing_variables_with_metadata() -> None:
    idx = pd.date_range("2024-01-01", periods=40)
    feat = pd.DataFrame({"x1": np.arange(40, dtype=float)}, index=idx)
    y = feat["x1"].rename("eth_ret")

    out = run_nested_ablation(y, feat, [("M1_missing", ["x1", "not_here"])])

    assert out.loc[0, "variables"] == "x1"
    assert out.loc[0, "missing_variables"] == "not_here"
    assert "skipped_missing=not_here" in out.loc[0, "note"]
