"""Binance public market-data URL builders and payload normalizers."""
from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import pandas as pd

BASE_URL = "https://api.binance.com/api/v3"


def klines_url(
    symbol: str,
    *,
    interval: str = "1d",
    limit: int = 1000,
    start_time: int | None = None,
    end_time: int | None = None,
) -> str:
    """Return a Binance public kline endpoint URL."""

    query: dict[str, str | int] = {
        "symbol": symbol.strip().upper(),
        "interval": interval,
        "limit": limit,
    }
    if start_time is not None:
        query["startTime"] = start_time
    if end_time is not None:
        query["endTime"] = end_time
    return f"{BASE_URL}/klines?{urlencode(query)}"


def normalize_klines(payload: list[list[Any]], symbol: str, interval: str = "1d") -> pd.DataFrame:
    """Normalize Binance kline arrays to a typed OHLCV table."""

    cols = [
        "open_time_ms",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time_ms",
        "quote_asset_volume",
        "trade_count",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
        "ignore",
    ]
    frame = pd.DataFrame(payload, columns=cols)
    numeric_cols = [col for col in cols if col != "ignore"]
    for col in numeric_cols:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    frame.insert(0, "source", "binance")
    frame.insert(1, "symbol", symbol.strip().upper())
    frame.insert(2, "interval", interval)
    frame["open_time"] = pd.to_datetime(frame["open_time_ms"], unit="ms", utc=True)
    frame["close_time"] = pd.to_datetime(frame["close_time_ms"], unit="ms", utc=True)
    return frame.drop(columns=["ignore"])


__all__ = ["klines_url", "normalize_klines"]
