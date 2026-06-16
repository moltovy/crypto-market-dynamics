from __future__ import annotations

import numpy as np
import pandas as pd

from cqresearch.modeling.cusum import cusum_bounds, cusum_recursive_residuals, cusum_summary


def test_cusum_path_and_summary_are_generated() -> None:
    idx = pd.date_range("2024-01-01", periods=80)
    x = pd.DataFrame({"x1": np.linspace(-1, 1, len(idx))}, index=idx)
    y = (0.5 * x["x1"] + 0.01 * np.sin(np.arange(len(idx)))).rename("btc_ret")

    path = cusum_recursive_residuals(y, x)
    summary = cusum_summary(y, x)

    assert len(path) == 80
    assert {"date", "cusum"}.issubset(path.columns)
    assert summary["method"] == "exploratory_standardized_residual_cusum"
    assert cusum_bounds(len(path)) == 1.36
