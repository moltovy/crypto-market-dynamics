"""Reusable regime definitions for the Crypto Market Factor Lab.

Each regime produces a boolean mask over a DatetimeIndex, along with metadata
(name, description, observation counts). Regimes are used throughout the
feature-strength and block-attribution analyses to answer how factor relevance
changes across time windows, ETF eras, and volatility states.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd

BTC_ETF_DATE = pd.Timestamp("2024-01-11")
ETH_ETF_DATE = pd.Timestamp("2024-07-23")
PANEL_END = pd.Timestamp("2026-04-11")


@dataclass
class Regime:
    """A named time/condition filter over a panel index."""

    name: str
    description: str
    mask: pd.Series  # bool Series aligned to panel index
    n: int = 0
    notes: str = ""

    def __post_init__(self) -> None:
        self.n = int(self.mask.sum())


def _date_mask(
    index: pd.DatetimeIndex, start: str | pd.Timestamp, end: str | pd.Timestamp
) -> pd.Series:
    return pd.Series(
        (index >= pd.Timestamp(start)) & (index <= pd.Timestamp(end)),
        index=index,
    )


def _year_mask(index: pd.DatetimeIndex, year: int) -> pd.Series:
    return pd.Series(index.year == year, index=index)


def get_time_regimes(index: pd.DatetimeIndex) -> list[Regime]:
    """Return the core set of calendar and ETF-era regimes."""

    panel_start = index.min()
    panel_end = index.max()

    regimes = [
        Regime(
            name="full",
            description=f"Full panel {panel_start.date()} to {panel_end.date()}",
            mask=pd.Series(True, index=index),
        ),
        Regime(
            name="pre_btc_etf",
            description=f"Before BTC ETF launch ({BTC_ETF_DATE.date()})",
            mask=pd.Series(index < BTC_ETF_DATE, index=index),
        ),
        Regime(
            name="post_btc_etf",
            description=f"From BTC ETF launch ({BTC_ETF_DATE.date()})",
            mask=pd.Series(index >= BTC_ETF_DATE, index=index),
        ),
        Regime(
            name="post_eth_etf",
            description=f"From ETH ETF launch ({ETH_ETF_DATE.date()})",
            mask=pd.Series(index >= ETH_ETF_DATE, index=index),
        ),
    ]

    # Yearly regimes
    for year in sorted(set(index.year)):
        label = f"year_{year}"
        if year == panel_end.year and panel_end.month < 12:
            label = f"year_{year}_ytd"
        regimes.append(
            Regime(
                name=label,
                description=f"Calendar year {year}",
                mask=_year_mask(index, year),
            )
        )

    return regimes


def get_volatility_regimes(
    index: pd.DatetimeIndex,
    btc_ret: pd.Series,
    window: int = 30,
) -> list[Regime]:
    """Return high-vol / low-vol quartile regimes based on rolling realized vol.

    Realized volatility is computed as annualized rolling standard deviation
    of ``btc_ret`` over ``window`` trading days.
    """

    rv = btc_ret.rolling(window, min_periods=window).std() * np.sqrt(365)
    rv = rv.reindex(index)
    q25 = rv.quantile(0.25)
    q75 = rv.quantile(0.75)

    return [
        Regime(
            name="low_vol",
            description=f"Bottom quartile BTC {window}d realized vol (< {q25:.4f})",
            mask=pd.Series((rv <= q25).fillna(False).values, index=index),
            notes=f"threshold={q25:.4f}",
        ),
        Regime(
            name="high_vol",
            description=f"Top quartile BTC {window}d realized vol (> {q75:.4f})",
            mask=pd.Series((rv >= q75).fillna(False).values, index=index),
            notes=f"threshold={q75:.4f}",
        ),
    ]


def get_all_regimes(
    index: pd.DatetimeIndex,
    btc_ret: pd.Series | None = None,
) -> list[Regime]:
    """Return all regimes: time-based plus volatility-based if btc_ret given."""

    regimes = get_time_regimes(index)
    if btc_ret is not None:
        regimes.extend(get_volatility_regimes(index, btc_ret))
    return regimes


def regimes_to_dataframe(regimes: Sequence[Regime]) -> pd.DataFrame:
    """Convert regime list to a summary DataFrame for export."""

    rows = []
    for r in regimes:
        valid_dates = r.mask.index[r.mask]
        rows.append(
            {
                "regime": r.name,
                "description": r.description,
                "start": valid_dates.min().date().isoformat() if len(valid_dates) else "",
                "end": valid_dates.max().date().isoformat() if len(valid_dates) else "",
                "n": r.n,
                "notes": r.notes,
            }
        )
    return pd.DataFrame(rows)


__all__ = [
    "BTC_ETF_DATE",
    "ETH_ETF_DATE",
    "Regime",
    "get_all_regimes",
    "get_time_regimes",
    "get_volatility_regimes",
    "regimes_to_dataframe",
]
