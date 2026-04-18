"""Trivial sanity tests on the bundled CSV fixtures — guards against accidental corruption."""
from __future__ import annotations

import pandas as pd


def test_tiny_prices_shape(tiny_prices_csv) -> None:
    df = pd.read_csv(tiny_prices_csv, parse_dates=["date"])
    assert list(df.columns) == ["date", "btc_close", "eth_close"]
    assert len(df) == 13
    assert df["date"].is_monotonic_increasing


def test_tiny_macro_shape(tiny_macro_csv) -> None:
    df = pd.read_csv(tiny_macro_csv, parse_dates=["date"])
    assert {"date", "DGS10", "DGS2", "VIXCLS", "DXY"}.issubset(set(df.columns))
    assert len(df) == 13
