from __future__ import annotations

import numpy as np
import pandas as pd

from cqresearch.modeling.partial_r2 import (
    block_partial_r2,
    fit_rss,
    partial_r2_full_vs_reduced,
    safe_standardize,
)


def test_block_partial_r2_identifies_explanatory_block() -> None:
    idx = pd.date_range("2024-01-01", periods=80)
    x_a = pd.Series(np.linspace(-2, 2, len(idx)), index=idx, name="a")
    x_b = pd.Series(np.sin(np.arange(len(idx))), index=idx, name="b")
    y = (2.0 * x_a).rename("btc_ret")
    x = pd.concat([x_a, x_b], axis=1)

    out = block_partial_r2(y, x, {"A": ["a"], "B": ["b"]})

    a_value = float(out.loc[out["block"] == "A", "partial_r2"].iloc[0])
    b_value = float(out.loc[out["block"] == "B", "partial_r2"].iloc[0])
    assert a_value > 0.95
    assert b_value >= -1.0e-12
    assert a_value > b_value


def test_partial_r2_matches_rss_formula() -> None:
    idx = pd.date_range("2024-01-01", periods=40)
    x1 = pd.Series(np.arange(40, dtype=float), index=idx, name="x1")
    x2 = pd.Series(np.cos(np.arange(40)), index=idx, name="x2")
    y = (0.5 * x1 + x2).rename("target")
    x_full = pd.concat([x1, x2], axis=1)
    x_reduced = pd.DataFrame({"x2": x2})

    value = partial_r2_full_vs_reduced(y, x_full, x_reduced)
    tss = float(((y - y.mean()) ** 2).sum())
    expected = (fit_rss(y, x_reduced) - fit_rss(y, x_full)) / tss

    assert np.isclose(value, expected)


def test_standardize_and_missing_rows_are_safe() -> None:
    idx = pd.date_range("2024-01-01", periods=8)
    x = pd.DataFrame({"constant": 1.0, "varying": range(8)}, index=idx)
    x.loc[idx[3], "varying"] = np.nan
    y = pd.Series(range(8), index=idx, name="y")

    standardized = safe_standardize(x)
    assert standardized["constant"].fillna(0).eq(0).all()

    out = block_partial_r2(y, standardized, {"varying": ["varying"]})
    assert int(out["n"].iloc[0]) == 7
