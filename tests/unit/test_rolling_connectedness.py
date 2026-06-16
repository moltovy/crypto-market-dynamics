from __future__ import annotations

import numpy as np
import pandas as pd

from cqresearch.modeling.rolling_connectedness import (
    connectedness_by_regime,
    rolling_fevd_connectedness,
)


def test_rolling_connectedness_returns_window_rows() -> None:
    rng = np.random.default_rng(11)
    idx = pd.date_range("2023-01-01", periods=180)
    df = pd.DataFrame(
        rng.normal(scale=0.01, size=(len(idx), 4)),
        index=idx,
        columns=["btc_ret", "eth_ret", "spy_ret", "VIXCLS_d1"],
    )

    out = rolling_fevd_connectedness(df, window=80, step=40, horizon=3)
    regimes = connectedness_by_regime(out, pd.Timestamp("2023-04-01"))

    assert not out.empty
    assert {"date", "connectedness_pct", "error"}.issubset(out.columns)
    assert set(regimes["regime"]).issubset({"pre", "post"})
