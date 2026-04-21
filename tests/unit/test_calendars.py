"""Tests for calendar alignment and config-driven ffill limits."""

from __future__ import annotations

import pandas as pd


def test_get_master_ffill_limit_reads_config() -> None:
    from cqresearch.data.calendars import get_master_ffill_limit

    lim = get_master_ffill_limit()
    assert isinstance(lim, int)
    assert 0 <= lim <= 31


def test_align_to_master_respects_ffill_limit() -> None:
    from cqresearch.data.calendars import align_to_master, crypto_index, get_master_ffill_limit

    idx = pd.date_range("2024-01-01", periods=10, freq="D")
    # Fri value only — weekend + Mon should fill within limit
    s = pd.Series([100.0], index=[pd.Timestamp("2024-01-05")])
    out = align_to_master(s, kind="stock", master_index=idx, ffill_limit_days=get_master_ffill_limit())
    assert pd.notna(out.loc["2024-01-06"])  # Sat
    lim = get_master_ffill_limit()
    if lim < 3:
        return
    assert pd.notna(out.loc["2024-01-08"])  # Mon


def test_business_day_mask_weekends_false() -> None:
    from cqresearch.data.calendars import business_day_mask

    # Sat / Sun / Mon — middle day is still a weekend
    idx = pd.date_range("2024-01-06", periods=3, freq="D")
    m = business_day_mask(idx)
    assert not bool(m.iloc[0])
    assert not bool(m.iloc[1])
    assert bool(m.iloc[2])
