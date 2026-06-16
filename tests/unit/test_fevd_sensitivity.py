from __future__ import annotations

import numpy as np
import pandas as pd

from cqresearch.modeling.fevd_sensitivity import (
    run_fevd_order_sensitivity,
    summarize_fevd_sensitivity,
)


def test_fevd_order_sensitivity_records_successes_and_failures() -> None:
    rng = np.random.default_rng(7)
    idx = pd.date_range("2024-01-01", periods=140)
    df = pd.DataFrame(
        rng.normal(scale=0.01, size=(len(idx), 4)),
        index=idx,
        columns=["btc_ret", "eth_ret", "spy_ret", "VIXCLS_d1"],
    )

    out = run_fevd_order_sensitivity(
        df,
        {
            "crypto_first": ["btc_ret", "eth_ret", "spy_ret", "VIXCLS_d1"],
            "too_small": ["btc_ret", "eth_ret"],
        },
        horizon=3,
        maxlags=2,
    )
    summary = summarize_fevd_sensitivity(out)

    assert "fewer_than_3_available_columns" in set(out["error"].dropna())
    assert not summary.empty
    assert {"from", "to", "range"}.issubset(summary.columns)
